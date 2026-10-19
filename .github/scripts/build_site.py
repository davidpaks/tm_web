"""A GitHub Pages oldal összerakása a Feladatok mappából és a tananyag.json-ból.

- A tananyag.json mondja meg, melyik feladat melyik tanegységhez tartozik.
- Minden feladat minden almappájából (Nyersanyag, Megoldás …) letölthető .zip készül.
- A főoldal és a feladatonkénti oldalak automatikusan generálódnak.

Futtatás:  python3 .github/scripts/build_site.py  [kimeneti mappa, alapból _site]
"""
import html
import json
import shutil
import sys
import unicodedata
import zipfile
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "Feladatok"
DATA = json.loads((ROOT / "tananyag.json").read_text(encoding="utf-8"))
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"
REPO_URL = "https://github.com/davidpaks/tm_web"
SKIP = {".DS_Store", "Thumbs.db"}
SOLUTION_NAMES = {"megoldás", "megoldas"}
HU = " -_.0123456789aábcdeéfghiíjklmnoóöőpqrstuúüűvwxyz"
e = html.escape


def hu_key(s: str):
    s = unicodedata.normalize("NFC", s).lower()
    return [HU.index(c) if c in HU else 100 + ord(c) for c in s]


def url(*parts: str) -> str:
    return "/".join(quote(p) for p in parts)


def size(n: float) -> str:
    if n < 1024:
        return f"{n:.0f} B"
    n /= 1024
    if n < 1024:
        return f"{n:.0f} KB".replace(".", ",")
    return f"{n / 1024:.1f} MB".replace(".", ",")


def files_in(folder: Path):
    return sorted(
        (p for p in folder.rglob("*") if p.is_file() and p.name not in SKIP),
        key=lambda p: hu_key(p.relative_to(folder).as_posix()),
    )


def make_zip(folder: Path, dest: Path):
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files_in(folder):
            zf.write(f, f"{folder.name}/{f.relative_to(folder).as_posix()}")


def is_solution(d: Path) -> bool:
    return d.name.lower() in SOLUTION_NAMES


def parts_of(task: Path):
    return sorted(
        (d for d in task.iterdir() if d.is_dir()),
        key=lambda d: (is_solution(d), hu_key(d.name)),
    )


ICON_DL = '<svg aria-hidden="true" viewBox="0 0 16 16"><path d="M8 2v8m0 0-3-3m3 3 3-3M3 13h10" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ICON_OPEN = '<svg aria-hidden="true" viewBox="0 0 16 16"><path d="M9 3h4v4m0-4L7 9M11 10v3H3V5h3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

CSS = """
:root{
  --paper:#f2f5f9; --sheet:#ffffff; --ink:#14213d; --muted:#56607a; --line:#d6dde8;
  --cobalt:#2b59c3; --cobalt-soft:#e4ecfb; --teal:#0e6b5c; --teal-soft:#e0f1ed;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --sans:"Atkinson Hyperlegible",system-ui,-apple-system,"Segoe UI",sans-serif;
}
@media (prefers-color-scheme:dark){:root{
  --paper:#0f1626; --sheet:#162036; --ink:#e6ebf5; --muted:#9aa6c0; --line:#2a3754;
  --cobalt:#8fb0ff; --cobalt-soft:#1e2c4d; --teal:#6fd3c0; --teal-soft:#15332f;
}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 var(--sans)}
a{color:var(--cobalt);text-underline-offset:3px}
a:focus-visible{outline:3px solid var(--cobalt);outline-offset:2px;border-radius:4px}
.wrap{max-width:880px;margin:0 auto;padding:0 16px}
code,.chip{font-family:var(--mono);font-size:.82em}

/* fejléc */
.hero{padding:56px 0 40px;border-bottom:1px solid var(--line)}
.hero h1{font-size:clamp(2.1rem,6vw,3.1rem);line-height:1.1;margin:0 0 .6rem;letter-spacing:-.01em}
.hero h1 .tag{color:var(--muted);font-family:var(--mono);font-weight:400;font-size:.62em;vertical-align:.18em}
.hero p{margin:0;max-width:62ch;color:var(--muted)}
.path{list-style:none;margin:28px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.path li{display:flex;align-items:center;font-size:.9rem;color:var(--muted)}
.path span{padding:4px 10px;border-radius:999px;border:1px dashed var(--line)}
.path .kesz span{border:1px solid transparent;background:var(--teal-soft);color:var(--teal);font-weight:700}
.path-note{margin:10px 0 0;font-size:.85rem;color:var(--muted)}

/* órák */
.lessons{list-style:none;margin:0;padding:8px 0 48px}
.lesson{display:grid;grid-template-columns:72px 1fr;gap:0 20px;padding:36px 0;border-bottom:1px solid var(--line)}
.lesson:last-child{border-bottom:0}
.num{font-size:3.2rem;line-height:1;font-weight:700;color:var(--cobalt);font-variant-numeric:tabular-nums}
.num small{display:block;font-size:.8rem;font-weight:400;color:var(--muted);margin-top:4px}
.lesson h2{font-size:1.45rem;line-height:1.25;margin:4px 0 12px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 20px;padding:0;list-style:none}
.chip{background:var(--teal-soft);color:var(--teal);padding:2px 8px;border-radius:5px;white-space:nowrap}
.tasks{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}
.task{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px;padding:14px 0;border-bottom:1px solid var(--line)}
.task-name{font-weight:700;font-size:1.08rem}
.task-name a{color:var(--ink);text-decoration:none}
.task-name a:hover{color:var(--cobalt);text-decoration:underline}
.role{display:inline-block;font-size:.78rem;font-weight:700;padding:1px 8px;border-radius:999px;margin-right:8px;vertical-align:.12em}
.role-órai{background:var(--cobalt);color:var(--sheet)}
.role-gyakorló{border:1px solid var(--cobalt);color:var(--cobalt)}
.note{display:block;font-weight:400;font-size:.9rem;color:var(--muted);margin-top:2px}
.actions{display:flex;flex-wrap:wrap;gap:8px}
.btn{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border-radius:7px;font-size:.9rem;font-weight:700;text-decoration:none;background:var(--cobalt-soft);color:var(--cobalt)}
.btn:hover{background:var(--cobalt);color:var(--sheet)}
.btn svg{width:15px;height:15px}
.btn.quiet{background:none;padding-left:4px;padding-right:4px;font-weight:400;text-decoration:underline}
.btn.quiet:hover{color:var(--ink);background:none}

/* feladatoldal */
.crumb{display:inline-block;margin:32px 0 0;font-size:.95rem}
.task-hero{padding:16px 0 28px;border-bottom:1px solid var(--line)}
.task-hero h1{font-size:clamp(1.9rem,5vw,2.6rem);line-height:1.15;margin:0 0 .5rem}
.where{margin:0;padding:0;list-style:none;color:var(--muted)}
.steps{counter-reset:s;list-style:none;margin:28px 0 8px;padding:0;display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.steps li{counter-increment:s;padding:14px 16px 14px 52px;position:relative;background:var(--sheet);border:1px solid var(--line);border-radius:10px;font-size:.95rem}
.steps li::before{content:counter(s);position:absolute;left:16px;top:12px;width:24px;height:24px;border-radius:50%;background:var(--cobalt);color:var(--sheet);font-weight:700;font-size:.85rem;display:grid;place-items:center}
.folder{margin:28px 0;background:var(--sheet);border:1px solid var(--line);border-radius:10px;padding:18px 20px}
.folder.solution{border-color:var(--cobalt)}
.folder-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:10px;margin-bottom:12px}
.folder h2{font-size:1.2rem;margin:0}
.folder h2 small{display:block;font-size:.85rem;font-weight:400;color:var(--muted)}
.files{list-style:none;margin:0;padding:0}
.files li{display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-top:1px solid var(--line);font-size:.95rem}
.files a{word-break:break-all}
.files span{color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums}
footer{border-top:1px solid var(--line);padding:24px 0 48px;color:var(--muted);font-size:.9rem}

@media (max-width:560px){
  .lesson{grid-template-columns:1fr}
  .num{font-size:2.2rem;display:flex;align-items:baseline;gap:8px;margin-bottom:6px}
  .num small{display:inline;margin:0}
  .hero{padding-top:36px}
}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700'
         '&family=JetBrains+Mono:wght@400&display=swap">')


def page(title: str, body: str, base: str) -> str:
    return f"""<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
{FONTS}
<link rel="stylesheet" href="{base}assets/oldal.css">
</head>
<body>
{body}
<footer><div class="wrap">A feladatok forrásfájljai a <a href="{REPO_URL}">tm_web GitHub repositoryban</a> is elérhetők.</div></footer>
</body>
</html>
"""


def task_href(task: str, base: str = "") -> str:
    return f"{base}{url('Feladatok', task)}/"


def zip_name(task: Path, part: Path) -> str:
    return f"{task.name} - {part.name}.zip"


VIEWABLE = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf", ".html", ".txt"}


def open_target(part: Path) -> list[str] | None:
    """A mappán belüli út, ami böngészőben megnyitható: a mappa maga, ha van benne index.html,
    vagy az egyetlen fájl, ha csak egy (megjeleníthető) fájl van benne."""
    if (part / "index.html").exists():
        return []
    files = files_in(part)
    if len(files) == 1 and files[0].suffix.lower() in VIEWABLE:
        return list(files[0].relative_to(part).parts)
    return None


def task_row(task: Path, role: str | None, note: str | None) -> str:
    parts = parts_of(task)
    btns = []
    sol = next((p for p in parts if is_solution(p)), None)
    if sol and (sol / "index.html").exists():
        btns.append(f'<a class="btn" href="{url("Feladatok", task.name, sol.name)}/">{ICON_OPEN}Mintamegoldás</a>')
    raw = next((p for p in parts if not is_solution(p)), None)
    if raw:
        target = open_target(raw)
        if target is None:
            btns.append(f'<a class="btn" href="{url("Feladatok", task.name, zip_name(task, raw))}" download>{ICON_DL}{e(raw.name)}</a>')
        else:
            href = url("Feladatok", task.name, raw.name, *target) + ("/" if not target else "")
            btns.append(f'<a class="btn" href="{href}">{ICON_OPEN}{e(raw.name)}</a>')
    btns.append(f'<a class="btn quiet" href="{task_href(task.name)}">Minden fájl</a>')
    role_html = f'<span class="role role-{role}">{"Órai" if role == "órai" else "Gyakorló"}</span>' if role else ""
    note_html = f'<span class="note">{e(note)}</span>' if note else ""
    return (f'<li class="task"><div class="task-name">{role_html}'
            f'<a href="{task_href(task.name)}">{e(task.name)}</a>{note_html}</div>'
            f'<div class="actions">{"".join(btns)}</div></li>')


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT / "Feladatok", ignore=shutil.ignore_patterns(*SKIP))
    (OUT / "assets").mkdir()
    (OUT / "assets" / "oldal.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("")

    tasks = {d.name: d for d in SRC.iterdir() if d.is_dir()}
    lessons_of: dict[str, list[tuple[int, dict, dict]]] = {}
    for i, ora in enumerate(DATA["orak"], 1):
        for f in ora["feladatok"]:
            if f["mappa"] not in tasks:
                sys.exit(f"HIBA: a tananyag.json-ban szereplő '{f['mappa']}' mappa nincs a Feladatok alatt.")
            lessons_of.setdefault(f["mappa"], []).append((i, ora, f))

    # --- feladatonkénti oldalak ---
    for name, task in tasks.items():
        parts = parts_of(task)
        folders = []
        for part in parts:
            make_zip(part, OUT / "Feladatok" / name / zip_name(task, part))
            btns = [f'<a class="btn" href="{url(zip_name(task, part))}" download>{ICON_DL}Letöltés (.zip)</a>']
            target = open_target(part)
            if target is not None:
                href = url(part.name, *target) + ("/" if not target else "")
                btns.insert(0, f'<a class="btn" href="{href}">{ICON_OPEN}Megnyitás böngészőben</a>')
            desc = "A kész weboldal, összevetéshez" if is_solution(part) else "A feladathoz szükséges kiinduló anyagok"
            items = "".join(
                f'<li><a href="{url(part.name, *f.relative_to(part).parts)}">{e(f.relative_to(part).as_posix())}</a>'
                f"<span>{size(f.stat().st_size)}</span></li>" for f in files_in(part))
            folders.append(
                f'<section class="folder{" solution" if is_solution(part) else ""}"><div class="folder-head">'
                f'<h2>{e(part.name)}<small>{desc}</small></h2><div class="actions">{"".join(btns)}</div></div>'
                f'<ul class="files">{items}</ul></section>')

        where = "".join(
            f'<li>{i}. tanegység ({"órai" if f["szerep"] == "órai" else "gyakorló"} feladat): {e(ora["cim"])}'
            + (f' – {e(f["megjegyzes"])}' if f.get("megjegyzes") else "") + "</li>"
            for i, ora, f in lessons_of.get(name, []))
        where_html = f'<ul class="where">{where}</ul>' if where else ""
        has_raw = any(not is_solution(p) for p in parts)
        steps = ""
        if has_raw and any(is_solution(p) for p in parts):
            steps = ('<ol class="steps"><li>A feladat és a kiinduló anyag megnyitása vagy letöltése.</li>'
                     '<li>A weboldal önálló elkészítése a minta alapján.</li>'
                     '<li>Összevetés a mintamegoldással.</li></ol>')
        body = (f'<main class="wrap"><a class="crumb" href="../../">← Vissza a tanegységekhez</a>'
                f'<header class="task-hero"><h1>{e(name)}</h1>'
                f'{where_html}{steps}</header>'
                + "".join(folders) + "</main>")
        (OUT / "Feladatok" / name / "index.html").write_text(page(name, body, "../../"), encoding="utf-8")

    # --- főoldal ---
    path = "".join(
        f'<li class="{s["allapot"]}"><span>{e(s["nev"])}</span></li>' for s in DATA["tanulasi_ut"])
    lessons = []
    for i, ora in enumerate(DATA["orak"], 1):
        chips = "".join(f'<li class="chip">{e(k)}</li>' for k in ora.get("kulcsszavak", []))
        rows = "".join(task_row(tasks[f["mappa"]], f["szerep"], f.get("megjegyzes")) for f in ora["feladatok"])
        lessons.append(
            f'<li class="lesson"><div class="num">{i}.<small>tanegység</small></div><div>'
            f'<h2>{e(ora["cim"])}</h2><ul class="chips" aria-label="Új elemek">{chips}</ul>'
            f'<ul class="tasks">{rows}</ul></div></li>')
    extra = sorted((n for n in tasks if n not in lessons_of), key=hu_key)
    if extra:
        rows = "".join(task_row(tasks[n], None, None) for n in extra)
        lessons.append(f'<li class="lesson"><div class="num">+</div><div><h2>További feladatok</h2>'
                       f'<ul class="tasks">{rows}</ul></div></li>')

    body = (f'<header class="hero"><div class="wrap">'
            f'<h1><span class="tag">&lt;h1&gt;</span> {e(DATA["cim"])}</h1><p>{e(DATA["alcim"])}</p>'
            f'<ol class="path" aria-label="A tárgy témakörei">{path}</ol>'
            f'<p class="path-note">Kiemelve az eddig vett témakörök.</p></div></header>'
            f'<main class="wrap"><ol class="lessons">{"".join(lessons)}</ol></main>')
    (OUT / "index.html").write_text(page(DATA["cim"], body, ""), encoding="utf-8")
    print(f"{len(DATA['orak'])} tanegység, {len(tasks)} feladat -> {OUT}")


if __name__ == "__main__":
    build()
