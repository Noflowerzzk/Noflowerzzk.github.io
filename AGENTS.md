# Agent Notes

This directory is intended to be maintained as an independent Hugo project.

## Source of truth

- Edit content in `content/docs/**`
- Edit navigation in `mkdocs.yml`
- Do not manually edit `generated-content/**` or `public/**`

## Build pipeline

1. `tools/generate_mkdocs_nav.py`
2. `tools/prepare_generated_content.py`
3. Hugo builds with `--contentDir generated-content`

The generated docs root is `generated-content/docs/_index.md`, and it is forced to:

- `type: docs`
- `cascade.type: docs`

This is required so Hextra uses its `layouts/docs/*` templates instead of generic single/list templates.

## Important conventions

- Keep `mkdocs.yml` aligned with the documents you want exposed in navigation
- Use `!!!` admonition syntax in source Markdown; preprocessing converts it for Hugo
- Previous / next navigation is based on `mkdocs.yml`, not raw folder order
- Top navbar and sidebar are also derived from `mkdocs.yml`

## Safe edit areas

- `content/docs/**`
- `mkdocs.yml`
- `layouts/**`
- `assets/**`
- `static/**`
- `tools/**`
- `build.ps1`
- `serve.ps1`

## Areas to treat as generated

- `generated-content/**`
- `public/**`
- `resources/**`

## Local commands

Develop:

```powershell
.\serve.ps1
```

Build:

```powershell
.\build.ps1
```

## Deployment

GitHub Pages deployment is defined in:

- `.github/workflows/pages.yml`

The workflow sets up:

- Go
- Python
- Hugo Extended
- GitHub Pages artifact deployment
