# Subhajit Chattopadhyay — Academic Portfolio

Personal research portfolio for Subhajit Chattopadhyay, Research Scholar in the
School of Mechanical Sciences at IIT Bhubaneswar.

**Live site:** https://inderjeet0202.github.io/subhajit-portfolio/
**Repository:** https://github.com/INDERJEET0202/subhajit-portfolio
**Google Scholar:** https://scholar.google.com/citations?user=OPXCrBcAAAAJ&hl=en

Plain HTML/CSS/JS — no framework, no build step. The publications list keeps
itself up to date from Google Scholar, so no manual editing is needed when a
new paper is published.

---

## Contents

- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Local preview](#local-preview)
- [Setup: hosting](#setup-hosting)
- [Setup: the Scholar auto-sync](#setup-the-scholar-auto-sync)
- [Secrets handling](#secrets-handling)
- [Editing content](#editing-content)
- [Maintenance notes](#maintenance-notes)
- [Design decisions and why](#design-decisions-and-why)
- [Troubleshooting](#troubleshooting)
- [Open TODOs](#open-todos)

---

## How it works

Two independent systems. This separation matters — confusing them causes
most of the confusion about "will it still auto-update if I change hosts?"

```
        ┌──────────────────────── daily, 03:17 UTC ────────────────────────┐
        │                                                                  │
   GitHub Actions ──► SerpApi ──► Google Scholar profile                   │
        │                              │                                   │
        │              publications + citation counts                      │
        ▼                                                                  │
   data/publications.json  ──git commit + push──►  repo (main branch)      │
                                                        │                  │
                                                        ▼                  │
                                              GitHub Pages redeploys       │
                                                        │                  │
                                                        ▼                  │
                                    Live site fetches the JSON at page load
```

1. **GitHub Actions** runs the scraper on a daily cron, on GitHub's servers.
2. It writes `data/publications.json` and commits it if anything changed.
3. **GitHub Pages** serves the repo; a new commit triggers a redeploy.
4. **The browser** fetches that JSON at page load and renders the list plus
   the publications/citations counters.

**The host and the sync are unrelated.** The sync runs on GitHub Actions
regardless of who serves the site. Moving to Vercel or Netlify would change
step 3 only — the sync keeps working identically.

---

## Project structure

```
index.html                    Single-page site (Hero/About/Research/Publications/Achievements/Contact)
css/style.css                 All styling — design tokens at the top under :root
js/main.js                    Mobile nav + renders publications/stats from the JSON
data/publications.json        Publication data — rewritten by the daily sync
assets/img/profile.jpg        Profile photo (contrast/sharpness enhanced)
assets/img/iitbbs-logo.png    IIT Bhubaneswar logo in the pinned header
assets/img/favicon.svg        Tab icon (SC monogram)
scripts/fetch_scholar.py      Fetches Scholar data via SerpApi → publications.json
scripts/enhance_photo.py      One-off photo enhancement helper
scripts/requirements.txt      Python deps (just `requests`)
.github/workflows/update-publications.yml   The daily sync job
.env                          SERPAPI_KEY — git-ignored, never committed
.env.example                  Template for the above
.nojekyll                     Stops GitHub Pages running Jekyll over the files
```

---

## Local preview

No build tools required:

```bash
python3 -m http.server 8000
```

Open http://localhost:8000. Edit any file and refresh — that's the whole loop.

To run the sync locally:

```bash
python3 -m pip install -r scripts/requirements.txt
cp .env.example .env      # then paste your real key into .env
set -a && . ./.env && set +a
python3 scripts/fetch_scholar.py
```

---

## Setup: hosting

Currently on **GitHub Pages**, configured as:

- **Settings → Pages → Source:** Deploy from a branch
- **Branch:** `main`, folder `/ (root)`
- Enforce HTTPS: on

Every push to `main` redeploys automatically, usually within a minute.

### Moving to Vercel later

No code changes needed — it's a static site. Import the repo at
vercel.com/new, then **override the auto-detection**:

- **Framework Preset:** Other
- **Root Directory:** `./`
- **Build Command:** leave empty
- **Output Directory:** `./`

Vercel's auto-detect sees `scripts/requirements.txt` and wrongly guesses this
is a Python project named "scripts". If you accept that guess, the deploy
fails or serves nothing. The overrides above are the fix.

---

## Setup: the Scholar auto-sync

Two one-time settings on the repository:

### 1. Let the workflow push its commits

**Settings → Actions → General → Workflow permissions**
→ select **"Read and write permissions"** → Save.

Without this the job runs but the final `git push` fails with a 403.

### 2. Add the SerpApi key as a secret

**Settings → Secrets and variables → Actions → New repository secret**

- **Name:** `SERPAPI_KEY` (exact — the workflow looks for this name)
- **Value:** your key from https://serpapi.com/manage-api-key

### Running it

- **Automatically:** daily at 03:17 UTC.
- **Manually:** Actions tab → "Sync Google Scholar publications" → Run workflow.

A run that ends with `No changes to publications.json` is a success — it means
Scholar had nothing new since last time.

---

## Secrets handling

The SerpApi key lives in two places, and **neither is the git repo**:

| Where | Used by | Notes |
|---|---|---|
| `.env` (local) | Running the script on your machine | Git-ignored via `.gitignore` |
| GitHub repository secret | The daily Actions run | Encrypted; masked in logs |

Rules:

- **Never commit the key.** `.gitignore` blocks `.env` and `.env.*`. This repo
  is public — a committed key is a leaked key, and rewriting git history does
  not reliably un-leak it.
- **Don't paste keys into chat or issues.** Put them straight into the GitHub
  secret field, which is the only place the workflow reads from.
- **Rotate if exposed.** Regenerate at https://serpapi.com/manage-api-key,
  then update both the GitHub secret and your local `.env`.

To verify nothing secret is staged before a commit:

```bash
git diff --cached --name-only     # .env must not appear
git check-ignore -v .env          # should print the matching .gitignore rule
```

---

## Editing content

Most content is plain HTML in `index.html` — edit the text directly.

| To change | Where |
|---|---|
| Bio / intro paragraph | `index.html`, `.hero-lede` and the About section |
| Academic background | `index.html`, the `.timeline` list |
| Research focus cards | `index.html`, the `.cards-grid` section |
| Achievements | `index.html`, the `.achievements-list` |
| Contact links | `index.html`, the `.contact-list` |
| Colours / fonts | `css/style.css`, the `:root` block at the top |
| Publications | Don't edit — it's overwritten by the sync |

### Profile photo

Replace `assets/img/profile.jpg`. It renders in a circular frame with
`object-fit: cover`, so a square-ish crop works best (600×600px or larger).

Optionally run it through the same enhancement pass used on the current one
(auto-contrast, mild sharpening — the original was washed out):

```bash
python3 -m pip install Pillow
python3 scripts/enhance_photo.py path/to/new-photo.jpg profile.jpg
```

### CV

The "Download CV (PDF)" button in the Achievements section (`id="cvLink"`)
serves `assets/resume/Subhajit_CV.pdf` straight from the repo. To update it,
replace that file and push — the filename and link stay the same.

Note that this PDF is publicly downloadable and search-indexable, and it
contains a phone number, date of birth, and three referees' email addresses.
That was a deliberate choice. If you ever want those off the public web,
replace the file with a redacted version — but be aware the original stays in
git history, so a genuinely clean removal means rewriting history or
publishing the redacted copy under a fresh filename in a new repo.

---

## Maintenance notes

Things that could need attention someday, roughly in order of likelihood:

- **SerpApi free tier: 250 searches/month.** A daily sync uses about 30, so
  there's plenty of headroom. If the tier changes or the quota is exceeded,
  runs fail and the site keeps serving the last good data.
- **GitHub disables cron workflows after 60 days of repository inactivity**
  (it emails first). The sync commits a fresh `last_updated` timestamp on
  every successful run, which counts as activity and keeps the clock reset —
  so this should not trigger in practice. If it ever does, click
  "Enable workflow" in the Actions tab.
- **Failures are loud on purpose.** The workflow has no `continue-on-error`,
  so a broken sync turns the run red and GitHub emails you. An occasional red
  run is fine; a run failing every day means something needs fixing.
- **A failed sync never breaks the site.** `data/publications.json` keeps its
  last good contents, so the page renders normally with slightly stale data.

---

## Design decisions and why

Recording these because each one was a dead end that cost time.

### SerpApi instead of scraping Scholar directly

The first version used the `scholarly` Python package to scrape Scholar
directly. It worked perfectly from a laptop and **failed 100% of the time on
GitHub Actions.** Google blocks datacenter IP ranges for Scholar, and Actions
runners are datacenter IPs.

There is no free way around this from CI — the blocking is deliberate.
SerpApi fetches the same profile from its own infrastructure and handles the
blocking, which is what makes unattended daily syncing possible at all.

Dropping `scholarly` also removed a large fragile dependency tree (selenium,
sphinx, bibtexparser). The sync now needs only `requests`.

### Not OpenAlex, despite it being free and key-less

OpenAlex was evaluated as a no-signup alternative. Its author disambiguation
merges **four different people** named Subhajit Chattopadhyay into one profile
(`A5004286784`): the correct materials-engineering papers, plus a
statistician's arXiv copula papers, some SSRN economics papers, and a medical
paper in *Folia Medica*. Publishing other people's work on an academic
portfolio is worse than stale data, so this was rejected.

Google Scholar remains the right source precisely because it is manually
curated and correct.

### Publication links point to Scholar, not DOIs

SerpApi's author endpoint returns Scholar's per-citation page as each paper's
link. Resolving real publisher DOIs would require one extra API call per
paper per sync, which multiplies quota use and adds failure modes. The Scholar
page lists the publisher link, so it's one extra click.

### Single page instead of four

The original Google Sites version had Home/About/Achievement/Publications as
separate pages. This is one scrolling page with anchor navigation — fewer
files, no cross-page nav state, and it reads better on mobile.

---

## Troubleshooting

**Sync fails with `No module named 'bibtexparser.bibdatabase'`**
Historical — from the old `scholarly` implementation, which is gone. If you
ever reintroduce `scholarly`, pin `bibtexparser<2`; v2 removed that module and
`scholarly` declares no upper bound.

**Sync fails at the fetch step with a blocking/CAPTCHA error**
The `SERPAPI_KEY` secret is missing, wrong, or out of quota. Check
Settings → Secrets, and your usage at serpapi.com.

**Sync fails at the commit step with 403 / "Permission denied"**
Workflow permissions are read-only. Settings → Actions → General →
Workflow permissions → "Read and write permissions".

**Sync fails at the commit step with `remote: fatal error in commit_refs`**
A GitHub-side transient error, not a configuration problem — the fetch
succeeded and only the push was rejected. The commit step retries three
times with a rebase in between, so this normally self-heals. If every
attempt fails, just re-run the workflow; nothing is lost, since the next
run re-fetches from scratch.

**Site shows old data after a successful sync**
Pages redeploy takes a minute or two. Also hard-refresh (Cmd+Shift+R) — the
JSON is fetched with `cache: 'no-store'`, but the browser may still hold the
old HTML.

**Site is completely unstyled or 404s**
Check that `.nojekyll` still exists at the repo root. Without it, Pages runs
Jekyll, which can skip files.

---

## Open TODOs

- [x] Point the CV button at a real PDF — now `assets/resume/Subhajit_CV.pdf`
- [ ] Confirm one full sync run pushes successfully (the SerpApi fetch already
      succeeds in CI; the push was last blocked by a GitHub-wide outage)
- [ ] Rotate the SerpApi key if it was ever shared outside the secret store
