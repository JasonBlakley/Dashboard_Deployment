# Check Current Dashboard Usage
# This script checks recent logs to see if anyone is actively using the dashboard

Write-Host "=== Checking Dashboard Usage ===" -ForegroundColor Cyan
Write-Host ""

# Check local log files for recent activity
$logFiles = @(
    "dashboard_logs.txt",
    "dashboard_logs_2026-05-12.txt",
    "dashboard_logs_2026-04-28.txt"
)

$recentActivity = $false
$cutoffTime = (Get-Date).AddHours(-2)  # Check last 2 hours

Write-Host "Checking local log files for activity in the last 2 hours..." -ForegroundColor Yellow
Write-Host "Cutoff time: $cutoffTime" -ForegroundColor Gray
Write-Host ""

foreach ($logFile in $logFiles) {
    if (Test-Path $logFile) {
        Write-Host "Checking $logFile..." -ForegroundColor Gray
        
        # Get last 100 lines and filter out health checks
        $recentLines = Get-Content $logFile -Tail 100 | Where-Object { 
            $_ -notmatch "/health" -and 
            $_ -match "Dashboard Access|Graph.*Update|POST.*dashboard" 
        }
        
        if ($recentLines) {
            Write-Host "  Found $(($recentLines | Measure-Object).Count) dashboard interactions (excluding health checks)" -ForegroundColor Yellow
            Write-Host "  Most recent activity:" -ForegroundColor Yellow
            $recentLines | Select-Object -Last 3 | ForEach-Object {
                Write-Host "    $_" -ForegroundColor White
            }
            $recentActivity = $true
        } else {
            Write-Host "  No recent dashboard activity found" -ForegroundColor Green
        }
        Write-Host ""
    }
}

Write-Host "=" * 70 -ForegroundColor Cyan
if ($recentActivity) {
    Write-Host "⚠️  CAUTION: Recent dashboard activity detected" -ForegroundColor Yellow
    Write-Host "   Users may be actively using the dashboard." -ForegroundColor Yellow
    Write-Host "   Consider deploying during off-hours or notifying users." -ForegroundColor Yellow
} else {
    Write-Host "✓ No recent user activity detected" -ForegroundColor Green
    Write-Host "  Safe to proceed with deployment." -ForegroundColor Green
}
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Offer to check live logs if IBM Cloud CLI is available
Write-Host "Would you like to check live application logs from IBM Cloud? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "`nAttempting to check live logs..." -ForegroundColor Yellow
    Write-Host "Note: This requires IBM Cloud CLI login" -ForegroundColor Gray
    Write-Host ""
    
    # Check if logged in
    $loginCheck = ibmcloud target 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Not logged in to IBM Cloud. Run this to login:" -ForegroundColor Yellow
        Write-Host "  .\Dashboard_Deployment\login_and_deploy.ps1" -ForegroundColor Cyan
    } else {
        Write-Host "Fetching last 50 log entries..." -ForegroundColor Yellow
        ibmcloud ce application logs -n python-appid-app --tail 50 | Where-Object {
            $_ -notmatch "/health" -and 
            $_ -match "Dashboard Access|Graph.*Update|POST.*dashboard"
        }
    }
}

Write-Host "`nUsage check complete." -ForegroundColor Cyan

# Made with Bob