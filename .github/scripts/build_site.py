"""A GitHub Pages oldal összerakása a Feladatok mappából.

Minden feladat minden almappájából (Megoldás, Nyersanyag, Alapanyag, Minta …)
letölthető .zip készül, a főoldal és a feladatonkénti oldalak pedig
automatikusan generálódnak. A repóban csak a kicsomagolt fájlok vannak.

Futtatás:  python .github/scripts/build_site.py  [kimeneti mappa, alapból _site]
"""
import html
import shutil
import sys
import unicodedata
import zipfile
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "Feladatok"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"
TITLE = "Weboldalak készítése – feladatok"
SKIP = {".DS_Store", "Thumbs.db", "index.gen.html"}

# A megoldás kerüljön a lista végére, minden más (nyersanyag) elé.
SOLUTION_NAMES = {"megoldás", "megoldas"}

HU = " -_.0123456789aábcdeéfghiíjklmnoóöőpqrstuúüűvwxyz"


def hu_key(s: str):
    s = unicodedata.normalize("NFC", s).lower()
    return [HU.index(c) if c in HU else 100 + ord(c) for c in s]


def url(*parts: str) -> str:
    return "/".join(quote(p) for p in parts)


def size(n: int) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024 or unit == "MB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def files_in(folder: Path):
    return sorted(
        (p for p in folder.rglob("*") if p.is_file() and p.name not in SKIP),
        key=lambda p: hu_key(str(p.relative_to(folder))),
    )


def make_zip(folder: Path, dest: Path):
    # A zip-en belül a mappa neve is benne van, így kibontva nem szóródnak szét a fájlok.
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files_in(folder):
            zf.write(f, f"{folder.name}/{f.relative_to(folder).as_posix()}")


CSS = """
:root{--bg:#f7f6f2;--card:#fff;--fg:#1d1d1b;--muted:#6b6a64;--line:#e3e1da;--accent:#1f5fbf;--accent-bg:#e8effa}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--card:#1f1f1d;--fg:#ecebe6;--muted:#a3a29b;--line:#34332f;--accent:#7fb0ff;--accent-bg:#1d2a3d}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:860px;margin:0 auto;padding:40px 16px 64px}
h1{font-size:1.9rem;margin:0 0 .25rem}
h2{font-size:1.15rem;margin:0}
p.lead{color:var(--muted);margin:0 0 2rem}
a{color:var(--accent)}
.back{display:inline-block;margin-bottom:1.25rem;text-decoration:none}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px}
a.card{display:block;text-decoration:none;color:inherit;transition:border-color .15s}
a.card:hover{border-color:var(--accent)}
.card small{color:var(--muted)}
.section{margin-top:16px}
.head{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;margin-bottom:10px}
.btns{display:flex;flex-wrap:wrap;gap:8px}
.btn{display:inline-block;padding:6px 12px;border-radius:7px;background:var(--accent-bg);text-decoration:none;font-size:.92rem;font-weight:500}
ul.files{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}
ul.files li{display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-bottom:1px solid var(--line);font-size:.95rem}
ul.files li span{color:var(--muted);white-space:nowrap}
ul.files a{word-break:break-all}
"""


def page(title: str, body: str, css_href: str) -> str:
    return f"""<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{css_href}">
</head>
<body><main>
{body}
</main></body>
</html>
"""


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT / "Feladatok", ignore=shutil.ignore_patterns(*SKIP))
    (OUT / "assets").mkdir()
    (OUT / "assets" / "lista.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("")

    tasks = sorted((d for d in SRC.iterdir() if d.is_dir()), key=lambda d: hu_key(d.name))
    cards = []
    for task in tasks:
        parts = sorted(
            (d for d in task.iterdir() if d.is_dir()),
            key=lambda d: (d.name.lower() in SOLUTION_NAMES, hu_key(d.name)),
        )
        loose = [f for f in task.iterdir() if f.is_file() and f.name not in SKIP]
        sections = []
        for part in parts:
            zip_name = f"{task.name} - {part.name}.zip"
            make_zip(part, OUT / "Feladatok" / task.name / zip_name)
            btns = [f'<a class="btn" href="{url(zip_name)}" download>Letöltés (.zip)</a>']
            if (part / "index.html").exists():
                btns.insert(0, f'<a class="btn" href="{url(part.name)}/">Megnyitás böngészőben</a>')
            items = "".join(
                f'<li><a href="{url(part.name, *f.relative_to(part).parts)}">'
                f"{html.escape(f.relative_to(part).as_posix())}</a><span>{size(f.stat().st_size)}</span></li>"
                for f in files_in(part)
            )
            sections.append(
                f'<section class="card section"><div class="head"><h2>{html.escape(part.name)}</h2>'
                f'<div class="btns">{"".join(btns)}</div></div><ul class="files">{items}</ul></section>'
            )
        if loose:
            items = "".join(
                f'<li><a href="{url(f.name)}">{html.escape(f.name)}</a><span>{size(f.stat().st_size)}</span></li>'
                for f in sorted(loose, key=lambda f: hu_key(f.name))
            )
            sections.insert(0, f'<section class="card section"><h2>Fájlok</h2><ul class="files">{items}</ul></section>')

        body = (
            f'<a class="back" href="../../">← Összes feladat</a>'
            f"<h1>{html.escape(task.name)}</h1>"
            f'<p class="lead">A fájlok böngészőben megnyithatók, vagy mappánként letölthetők .zip-ként.</p>'
            + "".join(sections)
        )
        # Ha a feladat mappájában van saját index.html, azt nem írjuk felül.
        target = OUT / "Feladatok" / task.name / ("index.gen.html" if (task / "index.html").exists() else "index.html")
        target.write_text(page(task.name, body, "../../assets/lista.css"), encoding="utf-8")

        kinds = ", ".join(p.name for p in parts) or "fájlok"
        cards.append(
            f'<a class="card" href="{url("Feladatok", task.name, target.name if target.name != "index.html" else "")}">'
            f"<h2>{html.escape(task.name)}</h2><small>{html.escape(kinds)}</small></a>"
        )

    body = (
        f"<h1>{html.escape(TITLE)}</h1>"
        f'<p class="lead">Válassz feladatot: a megoldások böngészőben megnézhetők, '
        f"a nyersanyagok és megoldások .zip-ként letölthetők.</p>"
        f'<div class="grid">{"".join(cards)}</div>'
    )
    (OUT / "index.html").write_text(page(TITLE, body, "assets/lista.css"), encoding="utf-8")
    print(f"{len(tasks)} feladat -> {OUT}")


if __name__ == "__main__":
    build()
