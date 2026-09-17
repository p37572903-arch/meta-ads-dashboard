# Meta Ads Dashboard — daily update instructions

You are being handed an ongoing task: keep a Meta Ads performance dashboard current and publicly viewable via a GitHub Pages link, updating it once a day **only when the user (Naval) explicitly asks you to**. This file plus the two scripts in `scripts/` are everything you need — you don't need to see the conversation this was built in.

Read this whole file once before doing anything. Then jump to **"One-time setup"** if this is the first run, or straight to **"Daily update workflow"** if the repo is already set up.

## What you're maintaining

A self-contained HTML dashboard (`scripts/build_dashboard.py` generates it — one Python script, no build tooling) built from a Meta (Facebook/Instagram) Ads Manager export. It shows:

- A default view of 14 tiles: Spends, ROAS, Orders, CPA, Sale, AOV, CTR, CPM, CPC, LP rate, ATC rate, Cost per ATC, IC rate, CVR — plus 12 more metrics available through a "Metrics" multi-select filter.
- A date-range filter (defaults to the single latest day in the data).
- Campaign → Ad set → Ad cascading filters, with scope comparisons and per-entity rank.
- A weighted 0–100 "Performance Score" per campaign/ad set/ad, with a worked-example and methodology explanation (collapsed by default — click to expand).
- A chat assistant bubble, top right. **It will not appear on the GitHub Pages version** — it depends on a Claude-only browser API (`window.claude`) that only exists inside Claude's own Artifact viewer, not on a plain static site. This is expected, not a bug; nothing needs fixing. Leave the code as-is.

This is a heavily customized fork of Anthropic's `meta-performance-dashboard-skill` — the metric list, formulas, filters, and score formula were all specifically requested by Naval over several rounds. **Don't regenerate these scripts from the base skill or "clean them up"** — treat `scripts/build_dashboard.py` and `scripts/extract_data.py` as the source of truth, and only change them if Naval explicitly asks for a dashboard change (see "Making a dashboard change" below).

## What you have access to (stated assumptions — adjust if wrong)

- **A GitHub repo**, reachable however this session reaches GitHub (an authenticated `git`/`gh` CLI, a GitHub connector, or the Chrome extension logged into github.com). If no repo is already open/connected, ask Naval which repo to use, or create one (e.g. `meta-ads-dashboard`).
- **The Chrome extension**, logged in. Its main job here is the one-time GitHub Pages setup in the repo's web Settings UI, and spot-checking the published page after each update. It is not needed for the routine data pipeline.
- **A dedicated local folder** that Naval (or some other process) drops the day's raw Meta Ads export into. You do not fetch this yourself — treat it as an inbox. If more than one file in it looks like a recent export, ask Naval which one is today's before proceeding rather than guessing.

## Repo layout (create this if it doesn't exist yet)

```
scripts/
  extract_data.py       <- provided, do not regenerate
  build_dashboard.py    <- provided, do not regenerate
data/
  raw/
    meta_ads_export_2026-09-15.xlsx   <- one archived copy per day, dated, NEVER overwritten
    meta_ads_export_2026-09-16.xlsx
    ...
  data.json              <- extracted dataset from the MOST RECENT raw file (overwritten each run)
docs/
  index.html              <- the built dashboard — this is what GitHub Pages serves
  .nojekyll               <- empty file, stops GitHub Pages from running Jekyll over the repo
```

`data/raw/` is the "store all the previous data of Meta" archive Naval asked for — every day's export accumulates there, dated, so nothing is ever lost. `docs/index.html` is overwritten every run; that's fine, it's a build output, and the dated source it was built from is still sitting in `data/raw/`.

## One-time setup (first run only)

1. Create the repo structure above. Commit `scripts/extract_data.py` and `scripts/build_dashboard.py` from this handoff into `scripts/` unchanged.
2. Create an empty `docs/.nojekyll` file (cheap insurance against GitHub Pages' default Jekyll processing interfering with anything).
3. Push to the repo's default branch (usually `main`).
4. In the GitHub web UI (use Chrome), go to the repo's **Settings → Pages**, and set **Source = Deploy from a branch**, **Branch = main**, **folder = /docs**. Save. GitHub will build and give you a URL of the form `https://<username>.github.io/<repo>/` — this is the stable link Naval will share. It does not change on future updates.
5. Confirm with Naval that this is the right repo/URL before treating setup as done.

You only do this section once. Every day after, skip straight to the next section.

## Daily update workflow

**Trigger: only run this when Naval explicitly asks you to update the dashboard.** Do not schedule it, do not run it automatically, do not run it just because a new file appeared in the folder.

1. **Find today's raw export.** Look in the dedicated drop folder for the most recently modified `.xlsx`. If it's ambiguous (several recent files, or none), ask Naval rather than guessing.
2. **Archive it.** Copy that file into `data/raw/` in the repo, named `meta_ads_export_YYYY-MM-DD.xlsx` using today's date. If a file for that date already exists there, ask Naval before overwriting it — don't silently clobber a previous archive.
3. **Extract.** From the repo root:
   ```
   python3 scripts/extract_data.py data/raw/meta_ads_export_YYYY-MM-DD.xlsx data/data.json
   ```
   This needs `openpyxl` (`pip install openpyxl --break-system-packages` if missing). It auto-detects a raw Ads Manager export vs. an already-simplified sheet — you don't need to tell it which.

   Watch its printed summary line. If it says no date column was found, the dashboard's date-range filter will just stay inactive on this build (not an error) — mention that to Naval if it's unexpected for this file. If it errors about missing columns, tell Naval the exact missing-column list rather than trying to patch around it.
4. **Build.** From the repo root:
   ```
   python3 scripts/build_dashboard.py data/data.json docs/index.html
   ```
   This produces a complete, self-contained, standalone HTML file — no other assets needed, nothing else to copy into `docs/`.
5. **Commit and push** `data/raw/<new file>`, `data/data.json`, and `docs/index.html` together, with a message like `Update dashboard — YYYY-MM-DD`. Push to the branch GitHub Pages is serving from.
6. **Wait roughly 30–60 seconds** for GitHub Pages to redeploy, then open the Pages URL in Chrome and spot-check it: tiles show real numbers (not all `–`), the date range picker's max date matches today's data, no blank/broken page.
7. **Report back to Naval**: confirm it's updated, give the (unchanged) Pages URL, and note the date range now reflected in the data.

## Making a dashboard change (only if Naval asks for one)

`scripts/build_dashboard.py` is one Python file containing the entire HTML/CSS/JS as a single string — there's no separate build step or framework. To change dashboard behavior (a metric, a filter, the score formula, styling):

1. Read the relevant section of `build_dashboard.py` first — it's long (~1700 lines) but organized with `// ---------- section ----------` comments; search for the feature by name rather than reading top to bottom.
2. Make the smallest edit that satisfies the request.
3. Rebuild (`python3 scripts/build_dashboard.py data/data.json docs/index.html`) and open the result in a browser before pushing — check the browser console for errors and click through the change.
4. Commit, push, and re-verify the live Pages URL exactly as in the daily workflow above.

Do not change `scripts/extract_data.py`'s column-detection logic unless Naval's export format itself changes (a genuinely different column name, for instance) — it was reverse-engineered and verified row-for-row against known-good numbers, so don't "simplify" it speculatively.

## Quick reference

| Step | Command |
|---|---|
| Extract | `python3 scripts/extract_data.py data/raw/<file>.xlsx data/data.json` |
| Build | `python3 scripts/build_dashboard.py data/data.json docs/index.html` |
| Verify | Open the GitHub Pages URL, check tiles have real numbers and no console errors |
| Never | Auto-run this on a timer; overwrite a previous day's file in `data/raw/`; "fix" the missing chat bubble on GitHub Pages |
