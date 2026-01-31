# Script to deploy anki_template_designer to Anki addons folder
# This script copies the addon to Anki's addons21 directory

$ErrorActionPreference = "Stop"

# Find Anki addons folder
$AnkiAddonsPath = "$env:APPDATA\Anki2\addons21"
$AddonSourcePath = "$PSScriptRoot\anki_template_designer"
$AddonDestPath = "$AnkiAddonsPath\anki_template_designer"

Write-Host "Anki Template Designer Deployment Script"
Write-Host "========================================="
Write-Host ""

# Check if source exists
if (-not (Test-Path $AddonSourcePath -PathType Container)) {
    Write-Host "ERROR: Source addon path not found: $AddonSourcePath" -ForegroundColor Red
    exit 1
}

Write-Host "Source: $AddonSourcePath"
Write-Host "Target: $AddonDestPath"
Write-Host ""

# Check if Anki addons folder exists
if (-not (Test-Path $AnkiAddonsPath -PathType Container)) {
    Write-Host "ERROR: Anki addons folder not found at: $AnkiAddonsPath" -ForegroundColor Yellow
    Write-Host "Please ensure Anki has been run at least once on this computer." -ForegroundColor Yellow
    exit 1
}

# Remove existing addon if it exists
if (Test-Path $AddonDestPath -PathType Container) {
    Write-Host "Removing existing addon..." -ForegroundColor Yellow
    Remove-Item $AddonDestPath -Recurse -Force
    Write-Host "Existing addon removed." -ForegroundColor Green
}

# Copy new addon
Write-Host "Copying addon..." -ForegroundColor Yellow
Copy-Item $AddonSourcePath -Destination $AddonDestPath -Recurse
Write-Host "Addon copied successfully!" -ForegroundColor Green

# Verify
if (Test-Path $AddonDestPath -PathType Container) {
    $files = Get-ChildItem $AddonDestPath -Recurse -File
    Write-Host ""
    Write-Host "Deployment Summary:" -ForegroundColor Green
    Write-Host "  Addon location: $AddonDestPath"
    Write-Host "  Files deployed: $($files.Count)"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Restart Anki"
    Write-Host "  2. Look for 'Template Designer' in Tools menu"
    Write-Host "  3. Check Anki's console for any errors"
} else {
    Write-Host "ERROR: Addon was not deployed successfully!" -ForegroundColor Red
    exit 1
}
