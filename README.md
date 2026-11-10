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
- The site is a single page, with no navigation or separate posts, projects, or search pages.
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
