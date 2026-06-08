# Backup Script for Dashboard Files
# Run this before making any changes to the dashboard

param(
    [Parameter(Mandatory=$false)]
    [string]$Description = "manual_backup"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = ".\backups\$timestamp`_$Description"

Write-Host "=== Dashboard Backup Script ===" -ForegroundColor Cyan
Write-Host "Creating backup: $backupDir" -ForegroundColor Yellow
Write-Host ""

# Create backup directory
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Files to backup
$filesToBackup = @(
    "app.py",
    "auth.py",
    "auth_dash.py",
    "requirements.txt",
    "Dockerfile"
)

Write-Host "Backing up files:" -ForegroundColor Green
foreach ($file in $filesToBackup) {
    if (Test-Path $file) {
        Copy-Item $file -Destination "$backupDir\$file"
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (not found)" -ForegroundColor Yellow
    }
}

# Create backup manifest
$manifest = @"
Dashboard Backup Manifest
=========================
Timestamp: $timestamp
Description: $Description
Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Files Backed Up:
$($filesToBackup | ForEach-Object { "- $_" } | Out-String)

To Restore:
-----------
1. Navigate to backup directory: cd $backupDir
2. Copy files back: Copy-Item * -Destination ..\ -Force
3. Restart application

Git Commit (if using version control):
---------------------------------------
git add .
git commit -m "Backup before changes: $Description"
git tag "backup_$timestamp"
"@

$manifest | Out-File "$backupDir\BACKUP_MANIFEST.txt"

Write-Host ""
Write-Host "Backup Summary:" -ForegroundColor Cyan
Get-ChildItem $backupDir | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize

Write-Host ""
Write-Host "Backup Location: $backupDir" -ForegroundColor Green
Write-Host "Manifest: $backupDir\BACKUP_MANIFEST.txt" -ForegroundColor Green
Write-Host ""
Write-Host "To restore this backup:" -ForegroundColor Yellow
Write-Host "  Copy-Item '$backupDir\*' -Destination .\ -Force" -ForegroundColor White
Write-Host ""

# Made with Bob
