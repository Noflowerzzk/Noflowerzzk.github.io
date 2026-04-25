$ErrorActionPreference = "Stop"
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$siteRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $siteRoot

try {
    python .\tools\generate_mkdocs_nav.py
    python .\tools\prepare_generated_content.py
    & "$env:LOCALAPPDATA\Microsoft\WinGet\Links\hugo.exe" --gc --minify --noBuildLock --contentDir generated-content
    python .\tools\fix_demo_redirects.py
}
finally {
    Pop-Location
}
