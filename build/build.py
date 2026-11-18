#!/usr/bin/env python3
"""Baut aus der Quelle (src/index.html) die fertige Website nach docs/.

Jede Ansicht der Quelle wird eine eigene Seite unter eigener Adresse,
z. B. alyn-partners.de/arbeitsweise/. GitHub Pages veröffentlicht docs/
aus dem Branch main. Aufruf im Repo-Ordner:

    python3 build/build.py
"""
import json, re, shutil, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
DOMAIN = "https://alyn-partners.de"
STAND = date.today().isoformat()

PAGES = {
    "start": ("/", "ALYN Partners · Personal- und Managementberatung für den Mittelstand",
              "Stefanie Oelhaf berät Geschäftsführungen im Mittelstand zu Personal, Führung, Organisation und Veränderung – mit eigener Erfahrung in Ergebnis- und Personalverantwortung."),
    "personal-fuehrung": ("/personal-fuehrung/", "Personal & Führung · ALYN Partners",
              "HR-Beratung, Führungskräfteentwicklung, Konfliktklärung und Nachfolgeplanung für mittelständische Unternehmen. Führung und Zusammenarbeit, die mit dem Unternehmen wachsen."),
    "organisation": ("/organisation/", "Organisation & Struktur · ALYN Partners",
              "Organisationsentwicklung, Reorganisation und Restrukturierung, Integration nach Zukäufen (PMI) und HR-Transformation für den Mittelstand."),
    "change": ("/change/", "Change Management · ALYN Partners",
              "Veränderungen vorbereiten, Führungskräfte und Mitarbeitende einbeziehen und neue Arbeitsweisen im Alltag verankern."),
    "personalberatung": ("/personalberatung/", "Personalberatung · ALYN Partners",
              "Anforderungsprofile entwickeln, Führungskräfte beurteilen und Schlüsselpositionen gezielt besetzen – von der Eignungsdiagnostik bis zur Direktsuche."),
    "arbeitsweise": ("/arbeitsweise/", "Arbeitsweise · ALYN Partners",
              "Managementberatung, Projektmandat, Interim Management oder Executive Search: wie die Zusammenarbeit mit ALYN Partners abläuft, in vier klaren Schritten."),
    "ueber-mich": ("/ueber-mich/", "Über mich · Stefanie Oelhaf · ALYN Partners",
              "Stefanie Oelhaf, Diplom-Betriebswirtin: Niederlassungsleiterin, Head of HR, Prokuristin und Chief People Officer DACH. Heute Beraterin für den Mittelstand."),
    "impressum": ("/impressum/", "Impressum · ALYN Partners", "Impressum von ALYN Partners, Stefanie Oelhaf, Wilhelmsdorf."),
    "datenschutz": ("/datenschutz/", "Datenschutzerklärung · ALYN Partners", "Datenschutzerklärung von ALYN Partners."),
}
LEGAL = {"impressum", "datenschutz"}


def grab(s, start, end):
    a = s.index(start)
    b = s.index(end, a)
    return s[a:b]


def main():
    s = (SRC / "index.html").read_text(encoding="utf8")

    css = grab(s, "<style>\n", "</style>")[len("<style>\n"):]
    css = css.replace('url("img/', 'url("/img/').replace('url("fonts/', 'url("/fonts/')
    sprite = grab(s, '<svg width="0" height="0"', "</svg>") + "</svg>"
    header = grab(s, '<header class="site">', "</header>") + "</header>"
    contact = grab(s, '<section class="closing-contact"', "</section>") + "</section>"
    footer = grab(s, '<footer class="site">', "</footer>") + "</footer>"

    views = {}
    for m in re.finditer(r'<div class="view" data-view="([a-z-]+)"([^>]*)>\n(.*?)\n</div>', s, re.S):
        name, attrs, body = m.group(1), m.group(2), m.group(3)
        attrs = attrs.replace(" hidden", "")
        views[name] = (attrs, body)
    missing = set(PAGES) - set(views)
    assert not missing, f"Ansichten fehlen im Entwurf: {missing}"

    def links(html, page):
        def rep(m):
            target = m.group(2)
            if target in PAGES:
                return f'{m.group(1)}{PAGES[target][0]}"'
            if target == "kontakt" and page in LEGAL:
                return f'{m.group(1)}/#kontakt"'
            return m.group(0)
        html = re.sub(r'(<a\b[^>]*?\bhref=")#([a-z-]+)"', rep, html)
        return html.replace('src="img/', 'src="/img/')

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    (OUT / "assets" / "style.css").write_text(css, encoding="utf8")
    (OUT / "assets" / "site.js").write_text(SITE_JS, encoding="utf8")
    shutil.copytree(SRC / "fonts", OUT / "fonts")
    shutil.copytree(SRC / "img", OUT / "img", ignore=shutil.ignore_patterns("hero-b.jpg", "treppe.jpg", "bildmarke-kreis.png", ".*"))
    shutil.copy(SRC / "favicon.ico", OUT / "favicon.ico")

    for name, (path, title, desc) in PAGES.items():
        attrs, body = views[name]
        group = "felder" if 'data-group="felder"' in attrs else None
        h = header
        if group:
            h = h.replace('id="dd-btn" aria-expanded="false">', 'id="dd-btn" aria-expanded="false" class="active">')
            h = h.replace(f'href="#{name}">', f'href="#{name}" aria-current="page">', 1)
        h = re.sub(rf'(<a class="navlink" href="#{name}" data-view="{name}")', r'\1 aria-current="page"', h)
        h = h.replace(f'class="navlink" href="#{name}" data-view="{name}"', f'class="navlink active" href="#{name}" data-view="{name}"')
        main = f'<div class="view" data-view="{name}"{attrs}>\n{body}\n</div>'
        parts = [h, "<main>", main, "</main>"]
        if name not in LEGAL:
            parts.append(contact)
        parts.append(footer)
        content = links("\n".join(parts), name)
        robots = '<meta name="robots" content="index, follow">'
        ld = ""
        if name == "start":
            ld = '<script type="application/ld+json">' + json.dumps(LD, ensure_ascii=False) + "</script>\n"
        html = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{DOMAIN}{path}">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="ALYN Partners">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{DOMAIN}{path}">
<meta property="og:image" content="{DOMAIN}/img/hero.jpg">
<link rel="icon" href="/favicon.ico?v=2" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png?v=2">
<link rel="icon" type="image/png" sizes="64x64" href="/img/favicon-64.png?v=2">
<link rel="apple-touch-icon" href="/img/favicon-180.png?v=2">
<link rel="preload" href="/fonts/figtree-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
{ld}</head>
<body data-view="{name}">
{sprite}
{content}
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
        target = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf8")

    # 404-Seite
    notfound = f'''<div class="view" data-view="404">
  <section class="page-head grey"><div class="wrap">
    <div class="eyebrow">Fehler 404</div>
    <h1 class="display">Diese Seite gibt es nicht.</h1>
    <p class="lead">Vielleicht hat sich die Adresse geändert. Auf der Startseite finden Sie alle Beratungsfelder.</p>
    <div style="margin-top:32px"><a class="btn" href="/">Zur Startseite <svg><use href="#arr"/></svg></a></div>
  </div></section>
</div>'''
    page404 = (OUT / "index.html").read_text(encoding="utf8")
    page404 = re.sub(r"<title>.*?</title>", "<title>Seite nicht gefunden · ALYN Partners</title>", page404)
    page404 = page404.replace('<meta name="robots" content="index, follow">', '<meta name="robots" content="noindex">')
    page404 = re.sub(r'<link rel="canonical"[^>]*>\n', "", page404)
    page404 = re.sub(r'<script type="application/ld\+json">.*?</script>\n', "", page404)
    page404 = re.sub(r"<main>.*</main>", "<main>\n" + notfound + "\n</main>", page404, flags=re.S)
    page404 = page404.replace('<body data-view="start">', '<body data-view="404">')
    (OUT / "404.html").write_text(page404, encoding="utf8")

    urls = "\n".join(f"  <url><loc>{DOMAIN}{p}</loc><lastmod>{STAND}</lastmod></url>" for p, _, _ in PAGES.values())
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n', encoding="utf8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf8")
    (OUT / "CNAME").write_text("alyn-partners.de\n", encoding="utf8")
    (OUT / ".nojekyll").write_text("", encoding="utf8")
    print("fertig:", OUT)


LD = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "ALYN Partners",
    "description": "Personal- und Managementberatung für den Mittelstand: Personal & Führung, Organisation & Struktur, Change Management, Personalberatung.",
    "url": DOMAIN + "/",
    "image": DOMAIN + "/img/hero.jpg",
    "email": "kontakt@alyn-partners.de",
    "telephone": "+49 179 4304046",
    "address": {"@type": "PostalAddress", "streetAddress": "Elenweg 6", "postalCode": "88271",
                "addressLocality": "Wilhelmsdorf", "addressCountry": "DE"},
    "areaServed": ["Bodenseeregion", "Oberschwaben", "Allgäu", "Ulm", "Stuttgart", "Neckar-Alb", "DACH"],
    "founder": {"@type": "Person", "name": "Stefanie Oelhaf", "jobTitle": "Unternehmens- und Personalberaterin",
                "sameAs": ["https://www.linkedin.com/in/stefanieoelhaf"]},
}

SITE_JS = """(function(){
  var menuBtn=document.getElementById('menu-btn'),mobile=document.getElementById('mobile-nav');
  var ddBtn=document.getElementById('dd-btn'),dd=ddBtn.parentElement;
  menuBtn.addEventListener('click',function(){var o=mobile.classList.toggle('open');menuBtn.setAttribute('aria-expanded',o?'true':'false')});
  ddBtn.addEventListener('click',function(){var o=dd.classList.toggle('open');ddBtn.setAttribute('aria-expanded',o?'true':'false')});
  document.addEventListener('click',function(e){if(!dd.contains(e.target)){dd.classList.remove('open');ddBtn.setAttribute('aria-expanded','false')}});
  mobile.addEventListener('click',function(e){if(e.target.closest('a')){mobile.classList.remove('open');menuBtn.setAttribute('aria-expanded','false')}});
  var top=document.querySelector('.to-top');
  if(top){top.addEventListener('click',function(e){e.preventDefault();window.scrollTo({top:0,behavior:'smooth'})})}
})();
"""

if __name__ == "__main__":
    sys.exit(main())
