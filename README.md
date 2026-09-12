# Subhajit Chattopadhyay — Portfolio

A static academic portfolio site (plain HTML/CSS/JS, no build step) with a
Google Scholar publications feed that updates itself automatically.

## Structure

```
index.html                       Single-page site (Home/About/Research/Publications/Achievements/Contact)
css/style.css                    All styling
js/main.js                       Renders publications + stats from data/publications.json
data/publications.json           Publications data — overwritten daily by the sync job
assets/img/                      Images (currently placeholder avatar + favicon, see below)
scripts/fetch_scholar.py         Scraper that rebuilds data/publications.json from Google Scholar
scripts/requirements.txt         Python deps for the scraper
.github/workflows/update-publications.yml   Scheduled GitHub Action that runs the scraper daily
```

## 1. Preview locally

No build tools needed — any static file server works, e.g.:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## 2. Put it on GitHub Pages

1. Create a new **public** repo on GitHub (e.g. `subhajit-portfolio`).
2. From this folder:
   ```bash
   git init
   git add .
   git commit -m "Initial portfolio MVP"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
3. On GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch**,
   branch `main`, folder `/ (root)`. Save.
4. Your site goes live at `https://<your-username>.github.io/<repo-name>/`
   within a minute or two. Every future push to `main` redeploys automatically.

## 3. Turn on the automatic Google Scholar sync

The scraper needs permission to push its own commits:

1. **Settings → Actions → General → Workflow permissions** → select
   **"Read and write permissions"** → Save.
2. That's it — the workflow in `.github/workflows/update-publications.yml`
   runs every day at 03:17 UTC, re-scrapes
   [your Scholar profile](https://scholar.google.com/citations?user=OPXCrBcAAAAJ&hl=en),
   and commits `data/publications.json` if anything changed (new paper, new
   citation count, etc). The site reads that file at load time, so a new
   paper shows up on the live site the next day with zero manual edits.
3. To trigger it immediately instead of waiting: **Actions tab → "Sync
   Google Scholar publications" → Run workflow**.

Note: Google Scholar has no official API and occasionally rate-limits
scrapers. If a run gets blocked, the workflow fails (so GitHub emails you)
but the site is unaffected — `data/publications.json` keeps its last good
contents and the next scheduled run retries. An occasional red run is
normal; a run failing every day means something actually needs fixing.

## 4. Updating the profile photo

`assets/img/profile.jpg` is the current photo (auto-contrast + sharpened
from the original with `scripts/enhance_photo.py`, since the original was a
little washed out). To swap in a different photo later:

1. Replace `assets/img/profile.jpg` with your new image (a square-ish crop
   works best, ~600×600px+ — it's shown in a circular frame with
   `object-fit: cover`, so it gets center-cropped automatically).
2. Optional: run it through the same enhancement pass —
   ```bash
   pip install Pillow
   python3 scripts/enhance_photo.py path/to/new-photo.jpg profile.jpg
   ```

## 5. Point the CV button at your real file

In `index.html`, the "Download CV" button (`id="cvLink"`) currently points
to a placeholder Google Drive link. Replace `href="..."` with your actual
CV link (Drive share link, or a PDF you add under `assets/`).

## 6. Moving to Vercel later

No changes needed — Vercel (and Netlify) both auto-detect a static site
with no framework. Just "Import Project" from the same GitHub repo; the
GitHub Action keeps committing fresh publication data to `main` either way,
and Vercel redeploys on every push just like Pages does.
