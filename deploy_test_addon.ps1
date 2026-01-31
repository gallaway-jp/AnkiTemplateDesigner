# Script to deploy minimal test addon to Anki addons directory
# Copies latest files and removes old version if exists

param(
    [string]$AnkiAddonsPath = "$env:APPDATA\Anki2\addons21"
)

$SourceAddonPath = "d:\Development\Python\AnkiTemplateDesigner\test_addon_minimal"
$DestAddonPath = Join-Path $AnkiAddonsPath "test_addon_minimal"
$AddonName = "test_addon_minimal"

# Validate source exists
if (-not (Test-Path $SourceAddonPath)) {
    Write-Host "ERROR: Source addon path does not exist: $SourceAddonPath" -ForegroundColor Red
    exit 1
}

# Validate Anki addons directory exists
if (-not (Test-Path $AnkiAddonsPath)) {
    Write-Host "ERROR: Anki addons directory does not exist: $AnkiAddonsPath" -ForegroundColor Red
    Write-Host "Please ensure Anki is installed and you've opened it at least once." -ForegroundColor Yellow
    exit 1
}

Write-Host "Deploying $AddonName addon..." -ForegroundColor Cyan

# Remove existing addon if present
if (Test-Path $DestAddonPath) {
    Write-Host "Removing existing addon at: $DestAddonPath" -ForegroundColor Yellow
    Remove-Item -Path $DestAddonPath -Recurse -Force
    Write-Host "Existing addon removed." -ForegroundColor Green
}

# Copy new addon
Write-Host "Copying addon from: $SourceAddonPath" -ForegroundColor Cyan
Copy-Item -Path $SourceAddonPath -Destination $DestAddonPath -Recurse -Force

# Verify deployment
if (Test-Path $DestAddonPath) {
    Write-Host "`n✓ SUCCESS: Addon deployed to: $DestAddonPath" -ForegroundColor Green
    Write-Host "`nDeployed files:" -ForegroundColor Cyan
    Get-ChildItem -Path $DestAddonPath -Recurse | ForEach-Object {
        $RelativePath = $_.FullName.Replace($DestAddonPath, "").TrimStart("\")
        Write-Host "  - $RelativePath"
    }
    Write-Host "`nRestart Anki to load the addon." -ForegroundColor Yellow
} else {
    Write-Host "ERROR: Deployment failed. Destination not found: $DestAddonPath" -ForegroundColor Red
    exit 1
}
