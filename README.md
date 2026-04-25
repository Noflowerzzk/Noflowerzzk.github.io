# `hextra-site`

Independent Hugo + Hextra site for Abies's notebook.

## Local development

Prerequisites:

- Hugo Extended
- Go
- Python 3
- PowerShell

Run locally:

```powershell
cd F:\Codes\Abies_Notebook\hextra-site
.\serve.ps1
```

Production build:

```powershell
cd F:\Codes\Abies_Notebook\hextra-site
.\build.ps1
```

## Project structure

- `content/docs/`: source documents you edit directly
- `mkdocs.yml`: source of truth for navbar, sidebar order, and page titles
- `tools/generate_mkdocs_nav.py`: converts `mkdocs.yml` into `data/mkdocs_nav.json`
- `tools/prepare_generated_content.py`: copies `content/` to `generated-content/`, rewrites MkDocs-specific syntax, and prepares the Hugo input tree
- `generated-content/`: build input generated from source content; do not edit manually
- `layouts/`, `assets/`, `static/`: Hugo / Hextra overrides

## How to add a page

1. Create a new Markdown file under `content/docs/**`
2. Add the page to `mkdocs.yml`
3. Run `.\serve.ps1` or `.\build.ps1`

If you only create the file without updating `mkdocs.yml`, Hugo may still render it, but the page will not participate correctly in:

- top navigation
- sidebar ordering
- previous / next links
- display title overrides

## GitHub Pages deployment

This repository is prepared for deployment through GitHub Actions.

After moving `hextra-site` into its own repository:

1. Push the whole directory as the root of the new repository
2. In GitHub, open `Settings -> Pages`
3. Set `Source` to `GitHub Actions`
4. Push to `main`
5. GitHub Actions will build and deploy the site

Workflow file:

- [pages.yml](./.github/workflows/pages.yml)

The workflow does three project-specific steps before `hugo` runs:

1. generate `data/mkdocs_nav.json`
2. prepare `generated-content/`
3. build Hugo from `generated-content`

## Repository-specific settings to update after splitting

When this directory becomes a new repository, review these fields in [hugo.yaml](./hugo.yaml):

- `params.editURL.base`
- `menu.main` GitHub link
- `title`
- `baseURL` if you later switch away from GitHub Pages defaults

For GitHub Pages:

- user / org site: repository name should be `<username>.github.io`
- project site: repository name can be arbitrary, and the workflow uses GitHub Pages `base_url` automatically

## Notes

- `public/`, `resources/`, and `generated-content/` are generated artifacts
- do not manually edit files under `public/` or `generated-content/`
- `mkdocs.yml` remains the navigation source, even though the site is now Hugo-based

## References

- Hugo: Host on GitHub Pages  
  https://gohugo.io/host-and-deploy/host-on-github-pages/
- GitHub Docs: Configuring a publishing source for your GitHub Pages site  
  https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
