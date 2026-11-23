# Tim, Pip, Tom & Kit — static rebuild

A cleaned-up, dependency-free static rebuild of the family WordPress blog
`tptkschofield.wordpress.com` ("The Who, What, Where, Why & When of the
Schofield Family"). All WordPress cruft is gone: share buttons, "Like
Loading…", related posts, comments UI, blog stats, cookie banners,
tracking pixels and the marketing bar. What remains is the writing and
the photographs.

## What's here

- `source/` — the editable content:
  - `posts/YYYY/MM/DD/<slug>/post.md` — one file per post; the first line
    is an HTML comment holding the original title, e.g.
    `<!-- title: Post title -->`
  - `images.json` — photo galleries attached to the 2009-and-later posts
    (paths relative to `.../wp-content/uploads/`)
  - `build.py` — pure-stdlib static site generator
  - `style.css` — single stylesheet (Georgia serif, dark mode via
    `prefers-color-scheme`, no JavaScript)
  - `sitemap.md` / `manifest.json` — coverage checklists from the
    original site's sitemap
- `site/` — the generated output, ready to deploy as-is.

## Building

```bash
cd source
python3 build.py
```

This rebuilds everything into `../site` (138 posts + index + about).

## Deploying to wisp.place

From the repo root, run wisp's deploy tool against the generated folder:

```bash
npx wispctl deploy site/
```

## URL structure

Old WordPress links keep working — post pages live at the same paths
(`/YYYY/MM/DD/slug/index.html`), plus `index.html` (year-grouped list,
newest first) and `about/index.html`.

## Notes on images

Images are hotlinked from their original CDNs (WordPress.com uploads,
i0.wp.com Blogger/Picasa/Photobucket proxies, Flickr, Blogger). If those
services ever remove the files the images will break — the binary files
could not be archived, only linked.
