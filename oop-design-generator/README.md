# OOP Design Generator (Flask)

Converts a natural-language software description into:

1. Structured Object-Oriented design (classes, attributes, methods, relationships)
2. Code skeleton with boilerplate in **Python / C++ / Java / C# / TypeScript**
3. PlantUML class-diagram source
4. Rendered UML diagram image (PlantUML public server, with Kroki fallback)

No database. Pure Flask + HTML/CSS + a single JS file.

---

## 1. Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your AI provider credentials. Any **OpenAI-compatible**
chat-completions endpoint works:

| Provider     | OPENAI_BASE_URL                          | OPENAI_MODEL example       |
|--------------|------------------------------------------|----------------------------|
| OpenAI       | `https://api.openai.com/v1`              | `gpt-4o-mini`              |
| Groq         | `https://api.groq.com/openai/v1`         | `llama-3.3-70b-versatile`  |
| OpenRouter   | `https://openrouter.ai/api/v1`           | `openai/gpt-4o-mini`       |
| Ollama local | `http://localhost:11434/v1`              | `llama3.1`                 |

## 2. Run

```bash
python app.py
```

Open <http://127.0.0.1:5000>.

## 3. Use

1. Type a software description (e.g. *"A library system where members borrow books..."*).
2. Pick a target language.
3. Click **Generate**.
4. View classes, attributes, methods, relationships, code skeleton, PlantUML
   source, and the rendered UML diagram. Copy or download any block.

## 4. Project structure

```
oop-design-generator/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── services/
│   ├── ai_client.py
│   ├── prompt_builder.py
│   ├── parser.py
│   └── plantuml_client.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── result.html
└── static/
    ├── style.css
    └── app.js
```
