# Personal site

A Hugo website using PaperMod, ready to publish with GitHub Pages.

## Preview locally

Install Hugo with `brew install hugo` if needed. After cloning this repository:

```sh
git submodule update --init --recursive
hugo server -D
```

Open http://localhost:1313. The `-D` flag includes draft posts locally.

## Make it yours

- Edit `hugo.yaml` for the site title, description, author, and social profile URLs.
- Edit `content/_index.md` for the homepage introduction.
- About is the homepage. Releases is a separate page at `/releases/`, linked from the navigation. Projects is retained as a draft at `/projects/` for local `hugo server -D` previews, with external write-ups and resources configured in `data/projects.json`; its navigation entry is temporarily commented out. There are no posts or search pages.
- Social links are configured under `params.socialIcons` in `hugo.yaml`.

## Build

```sh
hugo --gc --minify
```

The generated site is in `public/`, which is intentionally ignored by Git.

## Publish to GitHub Pages

1. Sign in to GitHub CLI with `gh auth login`.
2. Create your own empty GitHub repository. For a personal homepage, name it `YOURUSERNAME.github.io`; the local folder can stay `personal-site`.
3. Add that repository as `origin` and push `main`.
4. In the GitHub repository, open **Settings > Pages** and select **GitHub Actions** as the source.
5. Open **Actions > Publish Hugo site > Run workflow** if the initial push ran before Pages was configured.

The included workflow builds Hugo and deploys to GitHub Pages. It automatically uses the Pages URL, including the repository subpath for project sites.

Set `baseURL` in `hugo.yaml` to your final site URL, for example `https://YOURUSERNAME.github.io/`. The site is currently configured for `https://bofenghuang.github.io/`. The publishing workflow also sets the base URL from GitHub Pages automatically.

A custom domain can be connected later through GitHub Pages and your DNS provider. After connecting one, update `baseURL` to match it.

## Theme updates

PaperMod is a Git submodule pinned to a specific commit. To update deliberately:

```sh
git submodule update --remote themes/PaperMod
hugo --gc --minify
git add themes/PaperMod
git commit -m "Update PaperMod theme"
```

Review the preview before publishing a theme update. See the theme's MIT license at `themes/PaperMod/LICENSE`.

## Current design

The homepage uses a white background and locally hosted Source Sans 3. Custom styling lives in `assets/css/extended/personal.css`.

The Hugging Face link uses `static/icons/huggingface.svg` (monochrome). The alternate color asset is intentionally retained at `static/icons/huggingface-color.svg`; it is not displayed on the homepage.

Hugging Face SVG assets come from `@lobehub/icons-static-svg` version 1.102.0. Font license files are included alongside the fonts in `static/fonts/`.

## Hugging Face releases

About (`/`) and Releases (`/releases/`) are separate pages. The homepage never renders the release list or its statistics script.

Releases displays a selected subset of releases as collection links, grouped by category, with a short description and an explicitly configured release year. Unmapped collections fall back to the earliest original model/dataset repository year (with a release-date correction for Distil-Whisper v3.5). Collection names and full membership come directly from Hugging Face. Individual checkpoints are not displayed. `data/release_collections.json` stores only presentation metadata (category, short description, release year, and optional display order), keyed by stable collection ID; it does not enumerate collection membership. It may define explicit per-collection statistical exclusions: English Distil-Whisper v3.5 is counted only in its dedicated collection, not again in Multilingual Distil Whisper v0.2. This exclusion is shown next to that collection. New unmapped collections appear under Other releases rather than being silently omitted.

The snapshot includes public collections owned by `bofenghuang` (the superseded Vigogne 2 Instruct collection is omitted in favor of merged Vigogne 2), plus the shared-work Distil-Whisper v3.5, DoctoBERT-fr, and FineMed-fr collections. No newly discovered community conversions are added automatically. Existing community checkpoints already curated in these collections remain included. Explicitly excluded checkpoints remain excluded.

Refresh the saved collection catalog and statistics:

```sh
python3 scripts/refresh_huggingface.py
```

The script reads complete collection contents, follows pagination, and sums model/dataset downloads within each collection. Papers and Spaces do not contribute download counters. Overall totals deduplicate by repository type and ID, including models shared by multiple collections. Collection counters may therefore sum to more than the overall total. Downloads are not unique users.

The checked-in `data/huggingface.json` supplies a network-free build fallback. On the Releases page only, `assets/js/releases.js` refreshes statistics anonymously on load and every five minutes while visible. There is no manual refresh button. The entire selected inventory must have valid monthly and cumulative values before any numbers or the timestamp are replaced. Failures preserve the displayed snapshot. Updated means the last successful retrieval, shown in Europe/Paris time; upstream counters follow Hugging Face's refresh schedule.

Run the Python refresh script to pick up collection name/membership changes or newly public collections. Browser refreshing updates the statistics for the saved inventory. This feature does not modify Hugging Face resources or publish the website.

The three shared-work collections also have public copies on the personal Hugging Face profile. `collection_sources` maps those copies' stable IDs back to the external originals. The site reads and links the original collections, deduplicating the copies before fetching, so neither their rows nor download counters are duplicated. Personal copies are for profile discoverability and do not automatically mirror later upstream membership changes. Optional `title` metadata provides a website-only display name.

The shared navigation includes a light/dark theme toggle. Light is the default; PaperMod persists the visitor’s choice as `pref-theme` in localStorage and restores it before rendering. Theme-aware custom colors live in `personal.css`; the monochrome Hugging Face icon is inverted only in dark mode.
