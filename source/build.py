#!/usr/bin/env python3
"""Build the static site from source/posts + images.json -> ../site"""

import html
import json
import os
import re

SOURCE = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(SOURCE, "posts")
SITE = os.path.normpath(os.path.join(SOURCE, "..", "site"))
WP = "https://tptkschofield.wordpress.com/wp-content/uploads/"
SITE_URL = "https://tptkschofield.wordpress.com/"

MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

BASE_CSS = os.path.join(SOURCE, "style.css")


def load_post(path):
    with open(os.path.join(POSTS, path)) as f:
        text = f.read()
    m = re.match(r"<!-- title: (.*?) -->\n", text)
    title = m.group(1) if m else "(untitled)"
    body = text[m.end():] if m else text
    return title, body.strip()


def md_to_html(md):
    """Minimal markdown: paragraphs, - bullet lists, *em* / **strong**."""
    out = []
    para = []
    in_list = False
    closing = ["</ul>"]

    def close_list():
        nonlocal in_list, closing
        if in_list:
            for tag in reversed(closing):
                out.append(tag)
            in_list = False
            closing = ["</ul>"]

    def flush():
        if para:
            close_list()
            out.append("<p>" + " ".join(para) + "</p>")
            para.clear()

    for line in md.split("\n"):
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("{{img|"):
            flush()
            _tag, src, href, alt = s.strip("{}").split("|")
            out.append(img_html(src, href, alt))
        elif s.startswith("- "):
            flush()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + s[2:] + "</li>")
        else:
            if in_list:
                close_list()
            para.append(re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                               lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">'
                                         f"{m.group(1)}</a>", s))
    flush()
    close_list()
    return "\n".join(out)


def img_html(src, href=None, alt=""):
    if not href:
        if src.startswith("http"):
            href = src
            show = src + "?w=600"
        else:
            href = WP + src
            show = href + "?w=600"
    else:
        show = src
    return (f'<a href="{html.escape(href, quote=True)}">'
            f'<img src="{html.escape(show, quote=True)}" '
            f'alt="{html.escape(alt)}" loading="lazy"></a>')


def page(title, body, rel_depth):
    prefix = "../" * rel_depth
    css = prefix + "style.css"
    home = prefix + (".." if rel_depth else ".")
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{css}">
<link rel="me" href="https://cyberplace.social/@chiefoldmist">
</head>
<body>
<header>
<h1><a href="{home}">Tim, Pip, Tom &amp; Kit</a></h1>
<p class="tagline">The Who, What, Where, Why &amp; When of the Schofield Family</p>
<nav><a href="{home}">Blog</a> &middot; <a href="{prefix}about/">About</a></nav>
</header>
<main>
{body}
</main>
</body>
</html>
"""


def render_post(idir, title, body, images, depth):
    m = re.match(r"(\d{4})/(\d{2})/(\d{2})/(.+)$", idir)
    year, month, day, _ = m.groups()
    datestr = f"{MONTHS[int(month)]} {int(day)}, {year}"
    parts = [f"<article>\n<h2>{html.escape(title)}</h2>",
             f'<p class="date"><time datetime="{year}-{month}-{day}">{datestr}</time></p>']
    if body:
        parts.append(md_to_html(body))
    if images:
        parts.append('<div class="photos">')
        parts.extend(img_html(p) for p in images)
        parts.append("</div>")
    parts.append("</article>")
    return page(title, "\n".join(parts), depth)


def render_post_list(years, images):
    sections = []
    for year in sorted(years, reverse=True):
        entries = []
        for idir in years[year]:
            m = re.match(r"(\d{4})/(\d{2})/(\d{2})/(.+)$", idir)
            _year, month, day, _slug = m.groups()
            title, _ = load_post(idir + "/post.md")
            datestr = f"{MONTHS[int(month)]} {int(day)}"
            entries.append(
                f'<li><a href="{idir}/">{html.escape(title)}</a> '
                f'<span class="date">{datestr}</span></li>')
        sections.append(f"<h2>{year}</h2>\n<ul>\n" + "\n".join(entries) + "\n</ul>")
    return page("Tim, Pip, Tom & Kit", "\n".join(sections), 0)


def main():
    os.makedirs(SITE, exist_ok=True)
    with open(os.path.join(SOURCE, "images.json")) as f:
        images = json.load(f)

    years = {}
    posts = []
    for root, dirs, files in os.walk(POSTS):
        if "post.md" not in files:
            continue
        idir = os.path.relpath(root, POSTS).replace(os.sep, "/")
        posts.append(idir)
        years.setdefault(idir[:4], []).append(idir)

    for y in years:
        years[y].sort(reverse=True)

    for idir in posts:
        title, body = load_post(idir + "/post.md")
        imgs = images.get(idir + "/", [])
        outdir = os.path.join(SITE, *idir.split("/"))
        out = render_post(idir, title, body, imgs, depth=len(idir.split("/")))
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "index.html"), "w") as f:
            f.write(out)

    with open(os.path.join(SITE, "index.html"), "w") as f:
        f.write(render_post_list(years, images))

    about = page("About", """<article>
<h2>About</h2>
<p>The Who, What, Where, Why &amp; When of the Schofield Family.</p>
<p>Tim, Pip, Tom &amp; Kit. A family blog, 2005&ndash;2026.</p>
<p><a href="https://cyberplace.social/@chiefoldmist" rel="me">cyberplace.social/@chiefoldmist</a></p>
</article>
""", 1)
    os.makedirs(os.path.join(SITE, "about"), exist_ok=True)
    with open(os.path.join(SITE, "about", "index.html"), "w") as f:
        f.write(about)

    with open(BASE_CSS) as fcss, open(os.path.join(SITE, "style.css"), "w") as fdst:
        fdst.write(fcss.read())

    print(f"built {len(posts)} posts + index + about into {SITE}")


if __name__ == "__main__":
    main()
