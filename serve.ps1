$ErrorActionPreference = "Stop"
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$siteRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $siteRoot

try {
    $hugoBin = "$env:LOCALAPPDATA\Microsoft\WinGet\Links\hugo.exe"
    python .\tools\generate_mkdocs_nav.py
    python .\tools\prepare_generated_content.py
    $job = Start-Job -ArgumentList $siteRoot, $hugoBin -ScriptBlock {
        param($root, $hugo)
        [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
        [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
        $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
        $env:PYTHONUTF8 = "1"
        $env:PYTHONIOENCODING = "utf-8"
        Set-Location $root
        & $hugo server -D --noBuildLock --contentDir generated-content
    }

    $publicRoot = Join-Path $siteRoot "public"
    $sourceDocsRoot = Join-Path $siteRoot "content\docs"
    $mkdocsPath = Join-Path $siteRoot "mkdocs.yml"
    $lastPatched = [datetime]::MinValue
    $lastPrepared = [datetime]::MinValue

    function Get-LatestTimestamp {
        param(
            [string[]]$Paths,
            [string[]]$Extensions = @()
        )

        $latest = [datetime]::MinValue
        foreach ($path in $Paths) {
            if (-not (Test-Path $path)) { continue }
            $item = Get-Item $path -ErrorAction SilentlyContinue
            if (-not $item) { continue }
            if (-not $item.PSIsContainer) {
                if ($item.LastWriteTimeUtc -gt $latest) { $latest = $item.LastWriteTimeUtc }
                continue
            }
            $files = Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue
            if ($Extensions.Count -gt 0) {
                $files = $files | Where-Object { $Extensions -contains $_.Extension.ToLowerInvariant() }
            }
            $candidate = $files | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
            if ($candidate -and $candidate.LastWriteTimeUtc -gt $latest) {
                $latest = $candidate.LastWriteTimeUtc
            }
        }
        return $latest
    }

    $lastSourceChange = Get-LatestTimestamp -Paths @($sourceDocsRoot, $mkdocsPath) -Extensions @(".md", ".ipynb", ".yml")

    while ($true) {
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try {
            Receive-Job $job 2>&1 | Out-Host
        }
        finally {
            $ErrorActionPreference = $previousErrorActionPreference
        }
        if ($job.State -ne "Running") {
            break
        }

        $currentSourceChange = Get-LatestTimestamp -Paths @($sourceDocsRoot, $mkdocsPath) -Extensions @(".md", ".ipynb", ".yml")
        if ($currentSourceChange -gt $lastSourceChange -and $currentSourceChange -gt $lastPrepared) {
            python .\tools\generate_mkdocs_nav.py | Out-Host
            python .\tools\prepare_generated_content.py | Out-Host
            $lastPrepared = Get-Date
            $lastSourceChange = $currentSourceChange
        }

        if (Test-Path $publicRoot) {
            $latest = Get-ChildItem $publicRoot -Recurse -Filter *.html -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTimeUtc -Descending |
                Select-Object -First 1
            if ($latest -and $latest.LastWriteTimeUtc -gt $lastPatched) {
                python .\tools\fix_demo_redirects.py | Out-Host
                $lastPatched = Get-Date
            }
        }

        Start-Sleep -Milliseconds 800
    }

}
finally {
    if ($job) {
        Stop-Job $job -ErrorAction SilentlyContinue | Out-Null
        Remove-Job $job -Force -ErrorAction SilentlyContinue | Out-Null
    }
    Pop-Location
}
