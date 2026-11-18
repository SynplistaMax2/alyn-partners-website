# alyn-partners.de

Website von ALYN Partners (Stefanie Oelhaf).

- `src/index.html` – Quelle: eine Datei mit allen Ansichten (`<div class="view" data-view="…">`), dazu `src/img`, `src/fonts`, `src/favicon.ico`
- `build/build.py` – erzeugt daraus die Einzelseiten in `docs/` (`python3 build/build.py`)
- `docs/` – fertige Website, wird von GitHub Pages aus `main` veröffentlicht (eigene Domain über `docs/CNAME`)

Änderungen: in `src/` ändern, bauen, `docs/` mit committen. Nie direkt in `docs/` editieren.
DNS liegt bei STRATO (A-Record 185.199.108.153, `www` → `synplistamax2.github.io.`).
