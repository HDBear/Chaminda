# CRBTechs × James Heal — Product Catalogue Library

Mobile-first single landing page for exhibition QR-code visitors to browse and
download 25 James Heal brochures and flyers (2 brochures + 23 flyers).
Hosted on GitHub Pages: **https://hdbear.github.io/Chaminda/**

## Layout

```
index.html          generated landing page (edit catalogue.json + re-run build, don't hand-edit)
styles.css          mobile-first styles (light/dark aware)
app.js              search + category filter (progressive enhancement)
catalogue.json      SOURCE OF TRUTH: site text, groups, documents, blurbs
pdfs/               renamed, URL-safe copies of the source PDFs
thumbs/             first-page cover thumbnails (WebP, 440px)
assets/             favicon.svg, logo-jamesheal.png (extracted from the brochure cover)
qr/                 qr.svg, qr.png, poster-a4.svg/png/pdf, handout-a6.svg/png/pdf
tools/build.py      rebuilds pdfs/, thumbs/ and index.html from catalogue.json
tools/make_qr.py    regenerates QR + A4 poster + A6 handout for the (possibly new) URL
```

Source PDFs live one folder up (`../Brochures`, `../Flyers`) and are never
modified. The `Sales Toolkits` folder is intentionally NOT published.

## Update a document / add a new flyer

1. Replace or add the PDF in the source folder (`../Flyers`, `../Brochures`).
2. If new: add an entry to `documents` in `catalogue.json`
   (title, group, type, `source` path, URL-safe `file` name, blurb).
   Groups: `featured`, `abrasion`, `strength`, `colour`, `washing`, `comfort`.
3. Rebuild and publish:

```sh
python3 tools/build.py
git add -A && git commit -m "Update catalogues" && git push
```

GitHub Pages republishes ~1 minute after the push.

## Branding / text changes

`site` block in `catalogue.json` (company name, intro). Colours: CSS
variables at the top of `styles.css` (`--navy`, `--accent`).

## Regenerate the QR / poster (e.g. URL change, custom domain)

```sh
python3 tools/make_qr.py "https://NEW-URL/" "short-label-for-poster"
```

Requires `pip install segno`. Then `git add qr && git commit && git push`.
Branding: the poster/handout use the real James Heal logo extracted from the
Performance Brochure (300 dpi). To use the exact vector CRB Techs logo instead
of the drawn stand-in, drop the file in as `assets/crbtechs-logo.png` and re-run.

## Notes

- The 18 MB Performance Brochure is compressed server-side to ~1.2 MB during
  build (ghostscript `/ebook`); original stays untouched in the source folder.
- Thumbnails are renders of each PDF's own cover page — James Heal covers
  already include product photography.
- Test Materials brochure is labeled "2019 edition" (`tag` in catalogue.json).
- Deferred ideas: per-category ZIP bundles, download analytics, lead-capture
  form, custom short domain (then re-run make_qr.py).
