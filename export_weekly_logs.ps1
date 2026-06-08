# Weekly Dashboard Log Export Script
# Run this every week to capture usage data before logs expire

$date = Get-Date -Format "yyyy-MM-dd"
$logDir = "Dashboard_Logs"
$logFile = "$logDir/dashboard_logs_$date.txt"

# Create log directory if it doesn't exist
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
    Write-Host "Created log directory: $logDir" -ForegroundColor Green
}

Write-Host "=== Dashboard Log Export ===" -ForegroundColor Cyan
Write-Host "Date: $date" -ForegroundColor Yellow
Write-Host ""

# Check if logged in
$loginCheck = ibmcloud target 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in to IBM Cloud. Logging in..." -ForegroundColor Yellow
    ibmcloud login --sso -r us-south
    ibmcloud target -g oidash
    ibmcloud ce project select --name python-appid-proj
}

# Export logs (get maximum available)
Write-Host "Exporting logs..." -ForegroundColor Yellow
ibmcloud ce application logs --name python-appid-app --tail 10000 > $logFile

if ($LASTEXITCODE -eq 0) {
    $lineCount = (Get-Content $logFile).Count
    $fileSize = (Get-Item $logFile).Length / 1KB
    
    Write-Host "✓ Logs exported successfully!" -ForegroundColor Green
    Write-Host "  File: $logFile" -ForegroundColor White
    Write-Host "  Lines: $lineCount" -ForegroundColor White
    Write-Host "  Size: $([math]::Round($fileSize, 2)) KB" -ForegroundColor White
    
    # Quick summary
    $logins = (Select-String -Path $logFile -Pattern "logged in").Count
    $ibmUsers = (Select-String -Path $logFile -Pattern "logged in" | Select-String "@ibm.com").Count
    $externalUsers = $logins - $ibmUsers
    
    Write-Host ""
    Write-Host "Quick Summary:" -ForegroundColor Cyan
    Write-Host "  Total logins: $logins" -ForegroundColor White
    Write-Host "  IBM users: $ibmUsers" -ForegroundColor White
    Write-Host "  External users: $externalUsers" -ForegroundColor White
} else {
    Write-Host "✗ Log export failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Export Complete ===" -ForegroundColor Green

# Made with Bob
