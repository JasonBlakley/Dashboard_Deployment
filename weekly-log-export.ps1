# Weekly Dashboard Log Export Script
# This script exports Code Engine logs and extracts login events
# Schedule this to run weekly via Windows Task Scheduler

# Configuration
$logDir = "C:\DashboardLogs"
$appName = "python-appid-app"
$date = Get-Date -Format "yyyy-MM-dd"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Create log directory if it doesn't exist
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
    Write-Host "Created log directory: $logDir"
}

# Log file paths
$logFile = "$logDir\dashboard-logs-$date.txt"
$loginFile = "$logDir\logins-$date.txt"
$accessFile = "$logDir\access-$date.txt"
$graphFile = "$logDir\graph-updates-$date.txt"
$summaryFile = "$logDir\weekly-summary-$date.txt"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dashboard Log Export - $timestamp" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Export all logs with timestamps
Write-Host "Exporting logs from Code Engine..." -ForegroundColor Yellow
ibmcloud ce application logs --name $appName --tail 50000 --timestamps > $logFile
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error exporting logs" -ForegroundColor Red
    exit 1
}
Write-Host "Full logs exported to: $logFile" -ForegroundColor Green

# Extract login events
Write-Host "Extracting login events..." -ForegroundColor Yellow
$loginEvents = Get-Content $logFile | Select-String "logged in"
$loginEvents | Out-File $loginFile
Write-Host "Login events extracted: $($loginEvents.Count) logins found" -ForegroundColor Green

# Extract dashboard access events
Write-Host "Extracting dashboard access events..." -ForegroundColor Yellow
$accessEvents = Get-Content $logFile | Select-String "Dashboard Access"
$accessEvents | Out-File $accessFile
Write-Host "Access events extracted: $($accessEvents.Count) access events found" -ForegroundColor Green

# Extract graph update events
Write-Host "Extracting graph update events..." -ForegroundColor Yellow
$graphEvents = Get-Content $logFile | Select-String "Graph [123] Update"
$graphEvents | Out-File $graphFile
Write-Host "Graph updates extracted: $($graphEvents.Count) graph updates found" -ForegroundColor Green

# Create weekly summary
Write-Host "Creating weekly summary..." -ForegroundColor Yellow
$summary = "Dashboard Usage Summary - Week of $date`n"
$summary += "========================================`n`n"
$summary += "Export Time: $timestamp`n"
$summary += "Log File: $logFile`n`n"
$summary += "STATISTICS:`n"
$summary += "-----------`n"
$summary += "Total Log Lines: $(Get-Content $logFile | Measure-Object -Line | Select-Object -ExpandProperty Lines)`n"
$summary += "Login Events: $($loginEvents.Count)`n"
$summary += "Dashboard Access Events: $($accessEvents.Count)`n"
$summary += "Graph Update Events: $($graphEvents.Count)`n`n"
$summary += "UNIQUE USERS (Logins):`n"
$summary += "----------------------`n"

# Parse unique users from login events
$uniqueUsers = @()
foreach ($login in $loginEvents) {
    if ($login -match "User (.*?) logged in") {
        $email = $matches[1].Trim()
        if ($uniqueUsers -notcontains $email) {
            $uniqueUsers += $email
        }
    }
}

if ($uniqueUsers.Count -gt 0) {
    foreach ($user in $uniqueUsers | Sort-Object) {
        $domain = ($user -split '@')[1]
        if ($domain -ne "ibm.com") {
            $summary += "  - $user [EXTERNAL]`n"
        } else {
            $summary += "  - $user`n"
        }
    }
    $summary += "`nTotal Unique Users: $($uniqueUsers.Count)`n"
    
    # Count external vs internal
    $externalUsers = $uniqueUsers | Where-Object { ($_ -split '@')[1] -ne "ibm.com" }
    $internalUsers = $uniqueUsers | Where-Object { ($_ -split '@')[1] -eq "ibm.com" }
    $summary += "  IBM Users: $($internalUsers.Count)`n"
    $summary += "  External Users: $($externalUsers.Count)`n"
} else {
    $summary += "  No login events found this week`n"
}

# Add client access summary
$summary += "`nCLIENT ACCESS (Graph Updates):`n"
$summary += "------------------------------`n"
$clientAccess = @{}
foreach ($graph in $graphEvents) {
    if ($graph -match "Client: ([^|]+)") {
        $client = $matches[1].Trim()
        if ($clientAccess.ContainsKey($client)) {
            $clientAccess[$client]++
        } else {
            $clientAccess[$client] = 1
        }
    }
}

if ($clientAccess.Count -gt 0) {
    foreach ($client in $clientAccess.Keys | Sort-Object) {
        $summary += "  $client : $($clientAccess[$client]) views`n"
    }
} else {
    $summary += "  No client access data found`n"
}

$summary += "`n========================================`n"

# Save summary
$summary | Out-File $summaryFile
Write-Host "Weekly summary created: $summaryFile" -ForegroundColor Green

# Display summary
Write-Host ""
Write-Host $summary -ForegroundColor Cyan

# Clean up old logs (keep last 90 days)
Write-Host "Cleaning up old logs (keeping last 90 days)..." -ForegroundColor Yellow
$oldLogs = Get-ChildItem $logDir -Filter "*.txt" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-90) }

if ($oldLogs.Count -gt 0) {
    $oldLogs | Remove-Item -Force
    Write-Host "Removed $($oldLogs.Count) old log files" -ForegroundColor Green
} else {
    Write-Host "No old logs to remove" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Log export completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files created in $logDir" -ForegroundColor White
Write-Host "  - dashboard-logs-$date.txt (full logs)" -ForegroundColor Gray
Write-Host "  - logins-$date.txt (login events only)" -ForegroundColor Gray
Write-Host "  - access-$date.txt (dashboard access)" -ForegroundColor Gray
Write-Host "  - graph-updates-$date.txt (graph updates)" -ForegroundColor Gray
Write-Host "  - weekly-summary-$date.txt (summary report)" -ForegroundColor Gray
Write-Host ""

# Made with Bob
