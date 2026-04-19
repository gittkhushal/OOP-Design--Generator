// Copy buttons + UML image fallback.
(function () {
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-copy-target]");
    if (!btn) return;
    var sel = btn.getAttribute("data-copy-target");
    var node = document.querySelector(sel);
    if (!node) return;
    var text = node.innerText;
    navigator.clipboard.writeText(text).then(
      function () {
        var prev = btn.textContent;
        btn.textContent = "Copied!";
        btn.disabled = true;
        setTimeout(function () {
          btn.textContent = prev;
          btn.disabled = false;
        }, 1200);
      },
      function () {
        alert("Copy failed. Select the text manually.");
      }
    );
  });

  // If the primary PlantUML URL fails to load the image, swap to the Kroki fallback.
  var img = document.getElementById("uml-img");
  if (img) {
    img.addEventListener("error", function once() {
      var fb = img.getAttribute("data-fallback");
      if (fb && img.src !== fb) {
        img.removeEventListener("error", once);
        img.src = fb;
      }
    });
  }
})();
