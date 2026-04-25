$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory = $true)]
    [string]$RelativePath,

    [Parameter(Mandatory = $true)]
    [string]$Title
)

$siteRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$contentRoot = Join-Path $siteRoot "content\\docs"

$normalized = $RelativePath.TrimStart('\', '/').Replace('/', '\')
if (-not $normalized.EndsWith(".md")) {
    $normalized = Join-Path $normalized ((Split-Path $normalized -Leaf) + ".md")
}

$targetPath = Join-Path $contentRoot $normalized
$targetDir = Split-Path -Parent $targetPath

if (Test-Path $targetPath) {
    throw "File already exists: $targetPath"
}

New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

$frontmatter = @"
---
title: $Title
---

"@

Set-Content -Path $targetPath -Value $frontmatter -Encoding UTF8

Write-Host "Created:" $targetPath
Write-Host ""
Write-Host "Next:"
Write-Host "1. Add the page to .\\mkdocs.yml so it appears in the sidebar and gets the correct title/order/prev-next links."
Write-Host "2. If the page uses local images, put them next to the Markdown file."
Write-Host "3. If .\\serve.ps1 is already running, it will regenerate automatically after the file and mkdocs.yml change."
