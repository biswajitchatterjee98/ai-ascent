#!/usr/bin/env python3
"""Build index.html and content-manifest.json from AI-Ascent.md."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "AI-Ascent.md"
OUT_PATH = ROOT / "index.html"
MANIFEST_PATH = ROOT / "content-manifest.json"

REG_CTA = """
<section class="contact" id="registration-form">
<h2>Ready to register?</h2>
<p class="contact-intro">Open the registration page to submit your details. Your form goes to <strong>atharv.kumar@webisdom.com</strong>.</p>
<p class="contact-actions"><a class="contact-submit" href="register.html" style="display:inline-block;text-decoration:none">Go to registration form</a></p>
</section>
"""


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[`'\"“”‘’]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def yt_id(url: str) -> str | None:
    m = re.search(r"(?:v=|/embed/|youtu\.be/)([A-Za-z0-9_-]{6,})", url)
    return m.group(1) if m else None


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+|mailto:[^)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        text,
    )
    return text


def render_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    head, *body = rows
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    trs = [f"<tr>{th}</tr>"]
    for row in body:
        # pad short rows
        while len(row) < len(head):
            row.append("")
        trs.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row[: len(head)]) + "</tr>")
    return '<div class="table-wrap"><table>' + "".join(trs) + "</table></div>"


def yt_card(vid: str, title: str) -> str:
    safe_title = html.escape(title)
    poster = f"images/youtube/{vid}.jpg"
    url = f"https://www.youtube.com/watch?v={vid}"
    return (
        f'<div class="yt-card" data-ytid="{vid}">'
        f'<a class="yt-title" href="{url}" target="_blank" rel="noopener">{safe_title}</a>'
        f'<button type="button" class="yt-poster" aria-label="Play video: {safe_title}" '
        f'data-ytid="{vid}" data-yturl="{url}">'
        f'<img src="{poster}" alt="{safe_title}" loading="lazy" referrerpolicy="no-referrigener" />'
        f'<span class="yt-play" aria-hidden="true"></span></button>'
        f'<div class="yt-frame" hidden></div></div>'
    ).replace("no-referrigener", "no-referrer")


def parse_blocks(md: str):
    """Split into topic panels on H1. Returns (topics, preamble)."""
    lines = md.splitlines()
    topics: list[dict] = []
    current: dict | None = None
    buf: list[str] = []
    preamble_lines: list[str] = []

    def flush():
        nonlocal buf, current
        if current is not None:
            current["body"] = "\n".join(buf).strip()
            topics.append(current)
        buf = []

    for line in lines:
        if line.startswith("# ") and not line.startswith("##"):
            title = line[2:].strip()
            numbered = bool(re.match(r"^\d+\.", title))
            if not numbered:
                # Document title / non-topic H1 stays in preamble
                if current is None:
                    preamble_lines.append(line)
                continue
            flush()
            current = {"title": title, "id": slugify(title), "subs": []}
            buf = []
            continue

        if current is None:
            preamble_lines.append(line)
        else:
            if line.startswith("## "):
                sub = line[3:].strip()
                current["subs"].append({"title": sub, "id": slugify(sub)})
            buf.append(line)
    flush()

    preamble = "\n".join(preamble_lines).strip()
    preamble = re.sub(r"^# .+\n*", "", preamble, count=1).strip()
    return topics, preamble


def md_to_html(md: str, topic_id: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    para: list[str] = []
    list_kind: str | None = None
    list_items: list[str] = []
    table_rows: list[list[str]] = []
    in_quote = False
    quote_lines: list[str] = []
    section_open = False

    def open_section(section_id: str) -> None:
        nonlocal section_open
        close_section()
        out.append(
            f'<section class="content-block" data-section-id="{html.escape(section_id)}">'
            f'<div class="content-block-body">'
        )
        section_open = True

    def close_section() -> None:
        nonlocal section_open
        if section_open:
            out.append("</div></section>")
            section_open = False

    def ensure_section() -> None:
        if not section_open:
            open_section(topic_id)

    def flush_para():
        nonlocal para
        if para:
            ensure_section()
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []

    def flush_list():
        nonlocal list_kind, list_items
        if list_kind and list_items:
            ensure_section()
            tag = "ol" if list_kind == "ol" else "ul"
            items = "".join(f"<li>{inline(x)}</li>" for x in list_items)
            out.append(f"<{tag}>{items}</{tag}>")
        list_kind = None
        list_items = []

    def flush_table():
        nonlocal table_rows
        if table_rows:
            ensure_section()
            # drop separator rows like ---|---
            cleaned = []
            for row in table_rows:
                if all(re.fullmatch(r":?-{3,}:?", c.strip()) for c in row):
                    continue
                cleaned.append(row)
            out.append(render_table(cleaned))
        table_rows = []

    def flush_quote():
        nonlocal in_quote, quote_lines
        if quote_lines:
            ensure_section()
            body = "".join(f"<p>{inline(q)}</p>" for q in quote_lines)
            out.append(f"<blockquote>{body}</blockquote>")
        in_quote = False
        quote_lines = []

    def flush_all():
        flush_para()
        flush_list()
        flush_table()
        flush_quote()

    while i < len(lines):
        line = lines[i]
        raw = line.rstrip()

        # images
        mimg = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", raw.strip())
        if mimg:
            flush_all()
            ensure_section()
            alt, src = mimg.group(1), mimg.group(2)
            out.append(
                f'<figure class="media topic"><img src="{html.escape(src)}" alt="{html.escape(alt)}" '
                f'loading="lazy" referrerpolicy="no-referrer" /><figcaption>{html.escape(alt)}</figcaption></figure>'
            )
            i += 1
            continue

        if raw.strip() == "---":
            flush_all()
            ensure_section()
            out.append("<hr />")
            i += 1
            continue

        if raw.startswith("## "):
            flush_all()
            title = raw[3:].strip()
            sid = slugify(title)
            open_section(sid)
            out.append(f'<h2 id="{sid}">{inline(title)}</h2>')
            i += 1
            continue

        if raw.startswith("### "):
            flush_all()
            ensure_section()
            title = raw[4:].strip()
            out.append(f'<h3 id="{slugify(title)}">{inline(title)}</h3>')
            i += 1
            continue

        if raw.startswith("> "):
            flush_para()
            flush_list()
            flush_table()
            in_quote = True
            quote_lines.append(raw[2:])
            i += 1
            continue
        if in_quote and (raw.startswith(">") or raw.strip() == ""):
            if raw.startswith("> "):
                quote_lines.append(raw[2:])
            elif raw.strip() == ">":
                quote_lines.append("")
            else:
                flush_quote()
                continue
            i += 1
            continue
        if in_quote:
            flush_quote()

        # table
        if "|" in raw and raw.strip().startswith("|"):
            flush_para()
            flush_list()
            cells = [c.strip() for c in raw.strip().strip("|").split("|")]
            table_rows.append(cells)
            i += 1
            continue
        if table_rows:
            flush_table()

        # lists
        mol = re.match(r"^(\d+)\.\s+(.+)$", raw)
        mul = re.match(r"^[-*]\s+(.+)$", raw)
        if mol:
            flush_para()
            if list_kind not in (None, "ol"):
                flush_list()
            list_kind = "ol"
            list_items.append(mol.group(2))
            i += 1
            continue
        if mul:
            flush_para()
            if list_kind not in (None, "ul"):
                flush_list()
            list_kind = "ul"
            item = mul.group(1)
            # youtube link as sole item → yt card
            ym = re.fullmatch(r"\[([^\]]+)\]\((https?://(?:www\.)?youtube\.com/watch\?v=[^)]+)\)", item.strip())
            if ym:
                flush_list()
                ensure_section()
                vid = yt_id(ym.group(2))
                if vid:
                    out.append(yt_card(vid, ym.group(1)))
                else:
                    list_kind = "ul"
                    list_items.append(item)
            else:
                list_items.append(item)
            i += 1
            continue
        if list_kind:
            flush_list()

        if raw.strip() == "":
            flush_para()
            i += 1
            continue

        # bare youtube links in paragraphs / bullets already handled
        ym2 = re.fullmatch(r"\[([^\]]+)\]\((https?://(?:www\.)?youtube\.com/watch\?v=[^)]+)\)", raw.strip())
        if ym2:
            flush_para()
            ensure_section()
            vid = yt_id(ym2.group(2))
            if vid:
                out.append(yt_card(vid, ym2.group(1)))
            i += 1
            continue

        para.append(raw.strip())
        i += 1

    flush_all()
    close_section()

    html_body = "\n".join(out)
    # inject registration form into topic 27 after registration heading block
    if topic_id.startswith("27-") or "practitioner-program" in topic_id:
        if 'id="registration-form"' not in html_body:
            html_body += (
                '<section class="content-block" data-section-id="registration-form">'
                f'<div class="content-block-body">{REG_CTA}</div></section>'
            )
    return html_body


CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Source+Sans+3:wght@400;500;600;700&display=swap');
:root{
  --bg:#f3f6f4;--ink:#142033;--muted:#5b6777;--card:#ffffff;--line:#d7e0db;
  --accent:#0f7a6c;--accent-deep:#0b5a51;--accent-soft:#e4f4f0;--navy:#12324a;--navy-soft:#e8eef3;
  --shadow:0 14px 40px rgba(18,50,74,.08);--radius:18px;--max:860px;--sidebar:290px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;color:var(--ink);font-family:"Source Sans 3",ui-sans-serif,system-ui,sans-serif;line-height:1.7;
  background:
    radial-gradient(900px 420px at 8% -8%, rgba(15,122,108,.14), transparent 55%),
    radial-gradient(800px 380px at 100% 0%, rgba(18,50,74,.10), transparent 50%),
    linear-gradient(180deg,#eef3f0 0%, var(--bg) 35%, #eef2f5 100%);
  min-height:100vh;
}
.wrap{max-width:calc(var(--max) + var(--sidebar) + 64px);margin:0 auto;padding:1.5rem 1.25rem 3.5rem;display:grid;grid-template-columns:var(--sidebar) 1fr;gap:1.5rem;align-items:start}
@media(max-width:960px){.wrap{grid-template-columns:1fr;padding-top:4.25rem}.toc{position:static!important;max-height:none}}
.toc-menu-btn{display:none}
.toc-backdrop{display:none}
.toc-close{display:none}
.toc-head{display:flex;align-items:center;justify-content:space-between;gap:.5rem;margin:0 0 .35rem}
.toc-head h2{margin:0 .35rem 0;flex:1}
header.hero{
  grid-column:1/-1;position:relative;overflow:hidden;
  background:linear-gradient(135deg, rgba(18,50,74,.92), rgba(11,90,81,.88) 55%, rgba(15,122,108,.85)),
    radial-gradient(500px 220px at 85% 20%, rgba(255,255,255,.18), transparent 60%);
  color:#f4fffc;border-radius:24px;padding:1.6rem 1.8rem;box-shadow:var(--shadow);
  display:flex;align-items:center;gap:1.75rem;animation:heroIn .7s ease both;
}
.brand-logo{display:block;width:min(300px,40%);height:auto;padding:.7rem 1rem;background:#fff;border-radius:16px;box-shadow:0 10px 28px rgba(0,0,0,.16);position:relative;z-index:1;transition:transform .25s ease}
.brand-logo:hover{transform:translateY(-2px)}
.hero-copy{min-width:0;position:relative;z-index:1}
.hero-kicker{display:block;margin:0 0 .9rem;font-size:.95rem;font-weight:500;color:rgba(244,255,252,.82)}
header.hero h1{margin:0 0 .7rem;font-family:Fraunces,Georgia,serif;font-size:clamp(1.85rem,3.6vw,2.7rem);letter-spacing:-.02em;line-height:1.15;font-weight:700}
header.hero p{margin:0;max-width:58ch;opacity:.95;font-size:1.05rem;line-height:1.55}
.toc{position:sticky;top:1rem;align-self:start;background:rgba(255,255,255,.86);backdrop-filter:blur(10px);border:1px solid var(--line);border-radius:20px;padding:1rem .9rem 1.05rem;box-shadow:var(--shadow);max-height:calc(100vh - 2rem);overflow:auto;animation:sideIn .55s ease both}
.toc h2{margin:0 .35rem .75rem;font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700}
.toc-topics{list-style:none;padding:0;margin:0}
.toc-topic{margin:.18rem 0}
.toc-toggle{display:flex;align-items:center;justify-content:space-between;gap:.5rem;width:100%;border:0;background:transparent;padding:.55rem .55rem;border-radius:12px;cursor:pointer;color:var(--ink);font:600 .86rem "Source Sans 3",sans-serif;text-align:left;transition:background .2s ease,color .2s ease}
.toc-toggle:hover,.toc-link:hover{background:var(--accent-soft);color:var(--accent-deep)}
.toc-toggle[aria-expanded="true"],.toc-topic.is-active > .toc-toggle{background:linear-gradient(135deg,var(--accent-soft),#edf7f4);color:var(--accent-deep);box-shadow:inset 3px 0 0 var(--accent)}
.toc-label{flex:1}
.toc-chevron{width:0;height:0;border-left:5px solid transparent;border-right:5px solid transparent;border-top:6px solid currentColor;transition:transform .2s ease;flex:0 0 auto;opacity:.8}
.toc-toggle[aria-expanded="true"] .toc-chevron{transform:rotate(180deg)}
.toc-subs{list-style:none;padding:.2rem 0 .4rem .55rem;margin:0 0 .25rem;border-left:2px solid #cfe5df;margin-left:.75rem;animation:subsIn .25s ease both}
.toc-subs li{margin:.12rem 0}
.toc-subs a,.toc-link{display:block;padding:.38rem .5rem;border-radius:10px;color:var(--ink);text-decoration:none;font-size:.82rem;font-weight:500;transition:background .18s ease,color .18s ease}
.toc-subs a:hover{background:var(--navy-soft);color:var(--navy)}
.toc-contact{margin-top:.9rem;padding-top:.8rem;border-top:1px solid var(--line)}
.toc-contact .toc-link{font-weight:700;color:#fff;background:linear-gradient(135deg,var(--accent),var(--accent-deep));text-align:center}
.toc-contact .toc-link:hover{filter:brightness(1.05);color:#fff}
.toc-user{margin-top:.75rem;padding-top:.75rem;border-top:1px solid var(--line)}
.toc-user-label{display:block;margin:0 .35rem .35rem;font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:700}
.toc-user-name{display:block;margin:0 .35rem .55rem;font-size:.9rem;font-weight:600;color:var(--navy)}
.toc-admin{display:none;margin-top:.45rem}
.toc-admin.is-visible{display:list-item}
.toc-admin .toc-link{font-weight:700;color:var(--navy);background:var(--navy-soft);text-align:center}
.toc-admin .toc-link:hover{background:#dce6ee;color:var(--navy)}
.toc-subs a.is-locked::after{content:"";display:inline-block;width:.55rem;height:.55rem;margin-left:.35rem;border:1.5px solid currentColor;border-radius:2px;opacity:.65;vertical-align:middle}
.content-block.is-gated .content-block-body{display:none}
.content-block.is-gated.is-pending .content-block-body{display:none}
.access-gate,.access-gate-pending{
  margin:1rem 0 1.4rem;padding:1.1rem 1.15rem;border-radius:16px;
  border:1px dashed #b8ccc4;background:linear-gradient(135deg,#f7fbf9,#eef6f2);
}
.access-gate h4,.access-gate-pending h4{margin:0 0 .35rem;font-family:Fraunces,Georgia,serif;color:var(--navy);font-size:1.05rem}
.access-gate p,.access-gate-pending p{margin:0 0 .85rem;color:var(--muted);font-size:.92rem}
.access-gate-pending{border-style:solid;background:#fff8ec;border-color:#e8c98e}
.btn-primary,.btn-secondary{
  border:0;border-radius:10px;padding:.65rem 1rem;cursor:pointer;
  font:600 .92rem "Source Sans 3",sans-serif;
}
.btn-primary{background:linear-gradient(135deg,var(--accent),var(--accent-deep));color:#fff}
.btn-secondary{background:#fff;border:1px solid var(--line);color:var(--navy);margin-right:.45rem}
.access-modal{position:fixed;inset:0;z-index:100;display:grid;place-items:center;padding:1rem}
.access-modal[hidden]{display:none!important}
.access-modal-backdrop{position:absolute;inset:0;background:rgba(18,50,74,.45)}
.access-modal-panel{
  position:relative;width:min(480px,100%);background:#fff;border-radius:18px;padding:1.25rem 1.3rem;
  box-shadow:0 20px 50px rgba(18,50,74,.25);border:1px solid var(--line);
}
.access-modal-panel h3{margin:0 0 .35rem;font-family:Fraunces,Georgia,serif;color:var(--navy)}
.access-modal-lead{margin:0 0 1rem;color:var(--muted);font-size:.92rem}
.access-modal-section{margin:0 0 .85rem;font-size:.92rem}
.access-modal-panel .field{display:flex;flex-direction:column;gap:.35rem;margin-bottom:.85rem}
.access-modal-panel label{font-size:.88rem;font-weight:700;color:var(--navy)}
.access-modal-panel textarea{
  width:100%;min-height:110px;font:inherit;border:1px solid #c9d5cf;border-radius:11px;padding:.75rem .85rem;resize:vertical;
}
.access-modal-actions{display:flex;justify-content:flex-end;gap:.45rem;margin-top:.2rem}
.access-form-error{margin:.7rem 0 0;color:#8a1f1a;font-weight:600;font-size:.9rem}
main{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:1.7rem 1.6rem 2.3rem;box-shadow:var(--shadow);min-height:68vh;position:relative;overflow:hidden}
main::before{content:"";position:absolute;left:0;top:0;right:0;height:4px;background:linear-gradient(90deg,var(--navy),var(--accent))}
.topic-panel{display:block;animation:panelIn .35s ease both}
.topic-panel[hidden]{display:none!important}
.topic-eyebrow{display:inline-flex;align-items:center;gap:.4rem;margin:0 0 .85rem;padding:.3rem .7rem;border-radius:8px;background:var(--accent-soft);color:var(--accent-deep);font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
main h1{margin:0 0 .9rem;font-family:Fraunces,Georgia,serif;font-size:clamp(1.7rem,2.6vw,2.15rem);line-height:1.2;letter-spacing:-.02em;color:var(--navy)}
main h2{margin:2rem 0 .75rem;padding-top:.35rem;font-family:Fraunces,Georgia,serif;font-size:1.28rem;color:var(--navy);border-top:1px solid #eef2f0}
main h2:first-of-type{border-top:0;padding-top:0}
main h3{margin:1.2rem 0 .5rem;font-size:1.05rem;color:#1d3d36}
p{margin:.75rem 0}ul,ol{margin:.55rem 0 1rem;padding-left:1.25rem}li{margin:.32rem 0}
hr{border:0;border-top:1px solid var(--line);margin:1.6rem 0}a{color:var(--accent-deep)}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.88em;background:var(--accent-soft);color:#0d4f46;padding:.12em .4em;border-radius:6px}
blockquote{margin:1rem 0;padding:.85rem 1rem;background:linear-gradient(135deg,#f4fbf8,#eef6f8);border-left:4px solid var(--accent);border-radius:0 14px 14px 0;color:#3d4d55}
.table-wrap{overflow-x:auto;margin:1rem 0;border:1px solid var(--line);border-radius:14px;box-shadow:0 4px 14px rgba(18,50,74,.04)}
table{width:100%;border-collapse:collapse;font-size:.94rem}
th,td{border-bottom:1px solid var(--line);padding:.7rem .8rem;text-align:left;vertical-align:top}
th{background:linear-gradient(180deg,#eef7f4,#e7f2ef);color:var(--navy);font-weight:700}
tr:last-child td{border-bottom:0}
figure.media{margin:1.15rem 0 1.35rem}
figure.media img{max-width:100%;height:auto;border-radius:16px;border:1px solid var(--line);display:block;background:#eef2f0}
figure.media.topic img{width:100%;max-height:340px;object-fit:cover;box-shadow:0 12px 32px rgba(18,50,74,.12)}
figcaption{font-size:.85rem;color:var(--muted);margin-top:.4rem}
.yt-card{margin:1rem 0 1.35rem;padding:0;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#0f1412;box-shadow:0 10px 28px rgba(0,0,0,.12);transition:transform .22s ease}
.yt-card:hover{transform:translateY(-2px)}
.yt-title{display:block;padding:.8rem 1rem .6rem;font-size:.95rem;font-weight:700;color:#eaf7f3;text-decoration:none;background:linear-gradient(135deg,#14324a,#0f5a51)}
.yt-title:hover{color:#fff;text-decoration:underline}
.yt-poster{position:relative;display:block;width:100%;padding:0;border:0;cursor:pointer;background:#000;aspect-ratio:16/9}
.yt-poster img{width:100%;height:100%;object-fit:cover;display:block}
.yt-play{position:absolute;left:50%;top:50%;width:68px;height:48px;margin:-24px 0 0 -34px;border-radius:14px;background:#ff0033;box-shadow:0 8px 24px rgba(0,0,0,.35);transition:transform .2s ease}
.yt-play::before{content:"";position:absolute;left:27px;top:14px;border-style:solid;border-width:10px 0 10px 18px;border-color:transparent transparent transparent #fff}
.yt-poster:hover .yt-play{transform:scale(1.06)}
.yt-frame{position:relative;width:100%;aspect-ratio:16/9;background:#000}
.yt-frame iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.yt-card.is-playing .yt-poster{display:none}
.yt-card.is-playing .yt-frame{display:block}
footer{grid-column:1/-1;text-align:center;color:var(--muted);font-size:.88rem;margin-top:.35rem;padding:.5rem 0}
main ol{list-style:none;padding-left:0;counter-reset:step}
main ol > li{position:relative;margin:.55rem 0;padding:.55rem .8rem .55rem 2.7rem;background:linear-gradient(90deg, rgba(228,244,240,.65), transparent 85%);border-radius:10px}
main ol > li::before{counter-increment:step;content:counter(step);position:absolute;left:.55rem;top:.55rem;width:1.55rem;height:1.55rem;border-radius:8px;background:linear-gradient(135deg,var(--navy),var(--accent));color:#fff;font-size:.78rem;font-weight:700;display:flex;align-items:center;justify-content:center}
main ul > li::marker{color:var(--accent)}
.contact{margin-top:1.5rem;background:linear-gradient(145deg,#fff,#f3faf7);border:1px solid var(--line);border-radius:18px;padding:1.5rem;box-shadow:0 8px 24px rgba(18,50,74,.05)}
.contact h2{margin:0 0 .4rem;font-family:Fraunces,Georgia,serif;color:var(--navy);font-size:1.45rem;border:0;padding:0}
.contact-intro{margin:0 0 1.2rem;color:var(--muted)}
.contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
.field{display:flex;flex-direction:column;gap:.35rem}
.field.full,.contact-actions,.consent{grid-column:1/-1}
.field label{font-size:.88rem;font-weight:700;color:var(--navy)}
.consent label{font-weight:500;display:flex;gap:.55rem;align-items:flex-start}
.field input,.field textarea,.field select{width:100%;font:inherit;color:var(--ink);background:#fff;border:1px solid #c9d5cf;border-radius:11px;padding:.78rem .85rem;outline:none}
.field input:focus,.field textarea:focus,.field select:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
.field textarea{min-height:110px;resize:vertical}
.contact-submit{border:0;border-radius:11px;padding:.82rem 1.25rem;background:linear-gradient(135deg,var(--accent),var(--accent-deep));color:#fff;font:700 .98rem "Source Sans 3",sans-serif;cursor:pointer;box-shadow:0 8px 18px rgba(15,122,108,.25)}
.contact-submit:hover{filter:brightness(1.05)}
.contact-status{margin:.8rem 0 0;padding:.8rem .95rem;border-radius:11px;background:#dff5ed;color:#0b584c;font:600 .92rem "Source Sans 3",sans-serif}
@keyframes heroIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes sideIn{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}
@keyframes panelIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes subsIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
@media(max-width:960px){header.hero{flex-direction:column;align-items:flex-start;gap:1.1rem}.brand-logo{width:min(340px,100%)}.contact-grid{grid-template-columns:1fr}
.toc-menu-btn{display:inline-flex;align-items:center;justify-content:center;position:fixed;top:1rem;left:1rem;z-index:70;width:2.75rem;height:2.75rem;padding:0;border:1px solid var(--line);border-radius:12px;background:#fff;box-shadow:var(--shadow);cursor:pointer}
.toc-menu-btn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.toc-menu-bars,.toc-menu-bars::before,.toc-menu-bars::after{display:block;width:1.15rem;height:2px;border-radius:2px;background:var(--navy)}
.toc-menu-bars{position:relative}
.toc-menu-bars::before,.toc-menu-bars::after{content:"";position:absolute;left:0}
.toc-menu-bars::before{top:-6px}
.toc-menu-bars::after{top:6px}
.toc-backdrop{display:block;position:fixed;inset:0;z-index:55;background:rgba(18,50,74,.42);opacity:0;pointer-events:none;transition:opacity .22s ease}
body.toc-open .toc-backdrop{opacity:1;pointer-events:auto}
.toc{position:fixed!important;top:0;left:0;bottom:0;z-index:60;width:min(300px,88vw);max-height:none;margin:0;border-radius:0 18px 18px 0;transform:translateX(-105%);transition:transform .24s ease;animation:none}
body.toc-open .toc{transform:none}
.toc-close{display:inline-flex;align-items:center;justify-content:center;width:2rem;height:2rem;border:0;border-radius:8px;background:transparent;color:var(--navy);font:700 1.25rem/1 "Source Sans 3",sans-serif;cursor:pointer}
.toc-close:hover{background:var(--navy-soft)}
}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""

JS = r"""
(function () {
  function showTopic(topicId, scrollToId) {
    document.querySelectorAll('.topic-panel').forEach(function (panel) {
      var match = panel.getAttribute('data-topic-id') === topicId;
      panel.hidden = !match;
      panel.classList.toggle('is-active', match);
      if (match) {
        panel.style.animation = 'none';
        void panel.offsetWidth;
        panel.style.animation = '';
        var heading = panel.querySelector('h1');
        if (heading && !panel.querySelector('.topic-eyebrow')) {
          var eyebrow = document.createElement('p');
          eyebrow.className = 'topic-eyebrow';
          eyebrow.textContent = 'Now reading';
          heading.parentNode.insertBefore(eyebrow, heading);
        }
      }
    });
    document.querySelectorAll('.toc-topic').forEach(function (topic) {
      var btn = topic.querySelector('.toc-toggle');
      var topLink = null;
      topic.querySelectorAll(':scope > .toc-link').forEach(function (a) { topLink = a; });
      var target = btn ? btn.getAttribute('data-target') : (topLink ? topLink.getAttribute('href') : null);
      var id = target ? target.replace(/^#/, '') : '';
      var active = id === topicId;
      topic.classList.toggle('is-active', active);
      if (btn) {
        btn.setAttribute('aria-expanded', active ? 'true' : 'false');
        var subs = topic.querySelector('.toc-subs');
        if (subs) subs.hidden = !active;
      }
    });
    if (scrollToId) {
      var targetEl = document.getElementById(scrollToId);
      var isTopicRoot = scrollToId === topicId;
      setTimeout(function () {
        if (isTopicRoot) window.scrollTo({ top: 0, behavior: 'smooth' });
        else if (targetEl) targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 30);
    }
  }
  function topicIdFromHash(hash) {
    var id = (hash || '').replace(/^#/, '');
    if (!id) return null;
    var el = document.getElementById(id);
    if (!el) return null;
    var panel = el.closest('.topic-panel');
    return panel ? panel.getAttribute('data-topic-id') : null;
  }
  document.addEventListener('click', function (e) {
    var toggle = e.target.closest('.toc-toggle');
    if (toggle) {
      e.preventDefault();
      var topicId = (toggle.getAttribute('data-target') || '').replace(/^#/, '');
      // Second click on the open topic collapses its dropdown.
      if (toggle.getAttribute('aria-expanded') === 'true') {
        toggle.setAttribute('aria-expanded', 'false');
        var topicEl = toggle.closest('.toc-topic');
        if (topicEl) topicEl.classList.remove('is-active');
        var subs = topicEl ? topicEl.querySelector('.toc-subs') : null;
        if (subs) subs.hidden = true;
        return;
      }
      showTopic(topicId, topicId);
      history.replaceState(null, '', '#' + topicId);
      if (typeof isMobileToc === 'function' && isMobileToc()) closeToc();
      return;
    }
    var subLink = e.target.closest('a');
    if (subLink && subLink.getAttribute('href') && subLink.getAttribute('href').charAt(0) === '#') {
      if (subLink.closest('.toc')) {
        e.preventDefault();
        var href = subLink.getAttribute('href');
        var targetId = href.slice(1);
        var topicId = topicIdFromHash(href);
        if (topicId) {
          showTopic(topicId, targetId);
          history.replaceState(null, '', href);
          if (typeof isMobileToc === 'function' && isMobileToc()) closeToc();
        }
        return;
      }
    }
    var btn = e.target.closest('.yt-poster');
    if (!btn) return;
    e.preventDefault();
    var card = btn.closest('.yt-card');
    var id = btn.getAttribute('data-ytid');
    var url = btn.getAttribute('data-yturl');
    if (location.protocol === 'file:') { window.open(url, '_blank', 'noopener'); return; }
    var frame = card.querySelector('.yt-frame');
    frame.hidden = false;
    frame.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0" title="YouTube video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>';
    card.classList.add('is-playing');
  });
  function isMobileToc() {
    return window.matchMedia('(max-width: 960px)').matches;
  }
  function setTocOpen(open) {
    document.body.classList.toggle('toc-open', open);
    var btn = document.getElementById('toc-menu-btn');
    var backdrop = document.getElementById('toc-backdrop');
    var toc = document.getElementById('site-toc');
    if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (backdrop) backdrop.hidden = !open;
    if (toc && isMobileToc()) toc.setAttribute('aria-hidden', open ? 'false' : 'true');
  }
  function closeToc() { setTocOpen(false); }
  var tocMenuBtn = document.getElementById('toc-menu-btn');
  if (tocMenuBtn) {
    tocMenuBtn.addEventListener('click', function () {
      setTocOpen(!document.body.classList.contains('toc-open'));
    });
  }
  var tocBackdrop = document.getElementById('toc-backdrop');
  if (tocBackdrop) tocBackdrop.addEventListener('click', closeToc);
  var tocClose = document.getElementById('toc-close');
  if (tocClose) tocClose.addEventListener('click', closeToc);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeToc();
  });
  if (isMobileToc()) {
    var tocEl = document.getElementById('site-toc');
    if (tocEl) tocEl.setAttribute('aria-hidden', 'true');
  }
  var initialTopic = topicIdFromHash(location.hash);
  if (initialTopic) showTopic(initialTopic, location.hash.replace(/^#/, ''));
  else {
    var first = document.querySelector('.topic-panel');
    if (first) showTopic(first.getAttribute('data-topic-id'), null);
  }
})();
"""


def main() -> None:
    md = MD_PATH.read_text(encoding="utf-8")
    topics, preamble = parse_blocks(md)

    # Overview topic from preamble
    overview_id = "ai-ascent"
    overview_html = md_to_html(preamble, overview_id)
    overview_subs = []
    for m in re.finditer(r"^## (.+)$", preamble, re.M):
        overview_subs.append({"title": m.group(1).strip(), "id": slugify(m.group(1).strip())})

    manifest_sections: list[dict] = []
    sort_order = 0

    def add_manifest(section_id: str, parent_id: str | None, title: str, stype: str) -> None:
        nonlocal sort_order
        sort_order += 1
        manifest_sections.append(
            {
                "id": section_id,
                "parent_id": parent_id,
                "title": title,
                "type": stype,
                "sort_order": sort_order,
            }
        )

    add_manifest(overview_id, None, "AI Ascent", "topic")
    for s in overview_subs:
        add_manifest(s["id"], overview_id, s["title"], "section")

    toc_items = []
    # overview
    subs_html = "".join(
        f'<li><a href="#{s["id"]}" data-section-id="{s["id"]}">{html.escape(s["title"])}</a></li>'
        for s in overview_subs
    )
    toc_items.append(
        f'<li class="toc-topic"><button type="button" class="toc-toggle" aria-expanded="false" '
        f'data-target="#{overview_id}"><span class="toc-label">Overview</span>'
        f'<span class="toc-chevron" aria-hidden="true"></span></button>'
        f'<ul class="toc-subs" hidden>'
        f'<li><a href="#{overview_id}" data-section-id="{overview_id}">Handbook overview</a></li>'
        f'{subs_html}</ul></li>'
    )

    panels = [
        f'<section class="topic-panel is-active" data-topic-id="{overview_id}">'
        f'<h1 id="{overview_id}">AI Ascent</h1>{overview_html}</section>'
    ]

    for t in topics:
        # skip if somehow duplicate overview
        if t["id"] == overview_id:
            continue
        body = md_to_html(t["body"], t["id"])
        panels.append(
            f'<section class="topic-panel" data-topic-id="{t["id"]}" hidden>'
            f'<h1 id="{t["id"]}">{inline(t["title"])}</h1>{body}</section>'
        )
        add_manifest(t["id"], None, t["title"], "topic")
        for s in t["subs"]:
            add_manifest(s["id"], t["id"], s["title"], "section")
        if t["id"].startswith("27-") or "practitioner-program" in t["id"]:
            add_manifest("registration-form", t["id"], "Ready to register?", "section")
        subs = "".join(
            f'<li><a href="#{s["id"]}" data-section-id="{s["id"]}">{html.escape(s["title"])}</a></li>'
            for s in t["subs"]
        )
        label = t["title"]
        if len(label) > 42:
            # keep number + short label for sidebar
            label = label[:40] + "…"
        toc_items.append(
            f'<li class="toc-topic"><button type="button" class="toc-toggle" aria-expanded="false" '
            f'data-target="#{t["id"]}"><span class="toc-label">{html.escape(label)}</span>'
            f'<span class="toc-chevron" aria-hidden="true"></span></button>'
            f'<ul class="toc-subs" hidden>'
            f'<li><a href="#{t["id"]}" data-section-id="{t["id"]}">{html.escape(t["title"])} overview</a></li>'
            f'{subs}</ul></li>'
        )

    toc_items.append(
        '<li class="toc-topic toc-contact"><a class="toc-link" href="register.html">Register · Practitioner Program</a></li>'
    )
    toc_items.append(
        '<li class="toc-topic toc-admin"><a class="toc-link" href="admin.html">Admin</a></li>'
    )
    toc_items.append(
        '<li class="toc-topic toc-user" hidden>'
        '<span class="toc-user-label">Signed in</span>'
        '<span class="toc-user-name" data-auth-name></span>'
        '</li>'
    )

    MANIFEST_PATH.write_text(
        json.dumps({"version": 1, "sections": manifest_sections}, indent=2),
        encoding="utf-8",
    )

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>AI Ascent</title>
<meta name="description" content="AI Ascent: foundations, generative AI, tools, automation, ethics, and practitioner program registration." />
<script src="config.js"></script>
<script src="api.js"></script>
<script src="auth.js"></script>
<style>
{CSS}
</style>
</head>
<body>
<div class="wrap">
<button type="button" class="toc-menu-btn" id="toc-menu-btn" aria-controls="site-toc" aria-expanded="false" aria-label="Open contents">
<span class="toc-menu-bars" aria-hidden="true"></span>
</button>
<div class="toc-backdrop" id="toc-backdrop" hidden></div>
<header class="hero">
<img class="brand-logo" src="images/traininglobe-logo.png" alt="Traininglobe" />
<div class="hero-copy">
<p class="hero-kicker">A practical learning guide</p>
<h1>AI Ascent</h1>
<p>Climb from industry context and model foundations to assistants, automation, governance, and the AI Practitioner program.</p>
</div>
</header>
<nav class="toc" id="site-toc"><div class="toc-head"><h2>Contents</h2><button type="button" class="toc-close" id="toc-close" aria-label="Close contents">×</button></div><ul class="toc-topics">{"".join(toc_items)}</ul></nav>
<main>{"".join(panels)}</main>
<footer>Traininglobe · AI Ascent</footer>
</div>
<div id="access-modal" class="access-modal" hidden aria-hidden="true">
<div class="access-modal-backdrop" data-close-modal></div>
<div class="access-modal-panel" role="dialog" aria-labelledby="access-modal-title">
<h3 id="access-modal-title">Request access</h3>
<p class="access-modal-lead">Tell us why you need this section. An admin will review your request.</p>
<form id="access-request-form">
<input type="hidden" id="access-section-id" name="section_id" />
<p class="access-modal-section"><strong>Section:</strong> <span id="access-section-title"></span></p>
<div class="field">
<label for="access-notes">Reason / notes</label>
<textarea id="access-notes" name="notes" required placeholder="Why do you need access?"></textarea>
</div>
<div class="access-modal-actions">
<button type="button" class="btn-secondary" data-close-modal>Cancel</button>
<button type="submit" class="btn-primary">Submit request</button>
</div>
<p id="access-form-error" class="access-form-error" hidden></p>
</form>
</div>
</div>
<script src="access.js"></script>
<script>
{JS}
AscentAuth.fillUserChrome();
</script>
</body>
</html>
"""
    OUT_PATH.write_text(doc, encoding="utf-8")
    print(
        f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes), "
        f"topics={len(topics)+1}, sections={len(manifest_sections)}"
    )


if __name__ == "__main__":
    main()
