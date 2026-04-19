"""Flask entry point for the OOP Design Generator."""
from __future__ import annotations

import io
import os

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    send_file,
    flash,
    redirect,
    url_for,
)

from services.ai_client import call_ai, AIClientError
from services.prompt_builder import build_prompt, SUPPORTED_LANGUAGES, SYSTEM_PROMPT
from services.parser import parse_response
from services.plantuml_client import pick_working_url


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

LANG_EXT = {
    "Python": "py",
    "C++": "cpp",
    "Java": "java",
    "C#": "cs",
    "TypeScript": "ts",
}


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", languages=SUPPORTED_LANGUAGES)


@app.route("/generate", methods=["POST"])
def generate():
    description = (request.form.get("description") or "").strip()
    language = request.form.get("language") or "Python"
    if language not in SUPPORTED_LANGUAGES:
        language = "Python"

    if not description:
        flash("Please enter a software description.", "error")
        return redirect(url_for("index"))

    prompt = build_prompt(description, language)
    try:
        ai_text = call_ai(prompt, system=SYSTEM_PROMPT)
    except AIClientError as e:
        flash(str(e), "error")
        return redirect(url_for("index"))

    parsed = parse_response(ai_text)
    diagram = pick_working_url(parsed.plantuml) if parsed.plantuml else {
        "chosen": "",
        "primary": "",
        "fallback": "",
    }

    return render_template(
        "result.html",
        description=description,
        language=language,
        code_ext=LANG_EXT.get(language, "txt"),
        parsed=parsed,
        diagram=diagram,
    )


@app.route("/download", methods=["POST"])
def download():
    """Stateless download: client posts the content + filename back."""
    content = request.form.get("content", "")
    filename = request.form.get("filename", "download.txt")
    # very small safety: strip path separators
    filename = os.path.basename(filename) or "download.txt"
    buf = io.BytesIO(content.encode("utf-8"))
    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype="text/plain; charset=utf-8",
    )


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="127.0.0.1", port=5000, debug=debug)
