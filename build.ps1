$ErrorActionPreference = "Stop"
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$siteRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $siteRoot

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

try {
    Invoke-Checked { python .\tools\generate_mkdocs_nav.py }
    Invoke-Checked { python .\tools\prepare_generated_content.py }
    Invoke-Checked { & "$env:LOCALAPPDATA\Microsoft\WinGet\Links\hugo.exe" --gc --minify --noBuildLock --contentDir generated-content }
    Invoke-Checked { python .\tools\fix_demo_redirects.py }
}
finally {
    Pop-Location
}
