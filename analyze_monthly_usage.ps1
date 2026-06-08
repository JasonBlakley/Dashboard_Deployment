# Monthly Dashboard Usage Analysis Script
# Analyzes all log files for a given month

param(
    [Parameter(Mandatory=$false)]
    [string]$Month = (Get-Date -Format "yyyy-MM")
)

$logDir = "Dashboard_Logs"
$reportFile = "usage_report_$Month.txt"

Write-Host "=== Monthly Usage Analysis ===" -ForegroundColor Cyan
Write-Host "Month: $Month" -ForegroundColor Yellow
Write-Host ""

# Find all log files for the month
$logFiles = Get-ChildItem -Path $logDir -Filter "dashboard_logs_$Month-*.txt" -ErrorAction SilentlyContinue

if ($logFiles.Count -eq 0) {
    Write-Host "No log files found for $Month" -ForegroundColor Red
    Write-Host "Looking in: $logDir" -ForegroundColor Yellow
    Write-Host "Expected pattern: dashboard_logs_$Month-*.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found $($logFiles.Count) log files" -ForegroundColor Green
Write-Host ""

# Combine all logs
$allLogs = @()
foreach ($file in $logFiles) {
    $allLogs += Get-Content $file.FullName
}

Write-Host "Total log lines: $($allLogs.Count)" -ForegroundColor White
Write-Host ""

# Extract login events
$loginLines = $allLogs | Select-String "logged in"
$uniqueUsers = @{}
$dailyLogins = @{}

foreach ($line in $loginLines) {
    # Extract email
    if ($line -match "User ([^\s]+) logged in") {
        $email = $matches[1]
        
        # Count unique users
        if (-not $uniqueUsers.ContainsKey($email)) {
            $uniqueUsers[$email] = 0
        }
        $uniqueUsers[$email]++
        
        # Extract date from log line
        if ($line -match "^(\d{4}-\d{2}-\d{2})") {
            $date = $matches[1]
            if (-not $dailyLogins.ContainsKey($date)) {
                $dailyLogins[$date] = 0
            }
            $dailyLogins[$date]++
        }
    }
}

# Separate IBM vs External users
$ibmUsers = @{}
$externalUsers = @{}

foreach ($user in $uniqueUsers.Keys) {
    if ($user -match "@ibm.com$") {
        $ibmUsers[$user] = $uniqueUsers[$user]
    } else {
        $externalUsers[$user] = $uniqueUsers[$user]
    }
}

# Calculate averages
$avgLoginsPerDay = if ($dailyLogins.Count -gt 0) { [math]::Round($loginLines.Count / $dailyLogins.Count, 2) } else { 0 }

# Generate report
$report = @"
================================================================================
DASHBOARD USAGE REPORT
Month: $Month
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
================================================================================

SUMMARY
-------
Total Unique Users: $($uniqueUsers.Count)
  - IBM Users: $($ibmUsers.Count)
  - External Users: $($externalUsers.Count)

Total Logins: $($loginLines.Count)
  - IBM Logins: $(($loginLines | Select-String "@ibm.com").Count)
  - External Logins: $(($loginLines | Select-String -NotMatch "@ibm.com").Count)

Active Days: $($dailyLogins.Count)
Average Logins per Day: $avgLoginsPerDay

================================================================================
DAILY BREAKDOWN
================================================================================

"@

# Add daily stats
foreach ($date in ($dailyLogins.Keys | Sort-Object)) {
    $report += "$date : $($dailyLogins[$date]) logins`n"
}

$report += @"

================================================================================
IBM USERS (Top 10 by login count)
================================================================================

"@

if ($ibmUsers.Count -gt 0) {
    foreach ($user in ($ibmUsers.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 10)) {
        $report += "$($user.Name) : $($user.Value) logins`n"
    }
} else {
    $report += "No IBM users detected this month.`n"
}

if ($externalUsers.Count -gt 0) {
    $report += @"

================================================================================
EXTERNAL USERS
================================================================================

"@
    foreach ($user in ($externalUsers.GetEnumerator() | Sort-Object Value -Descending)) {
        $report += "$($user.Name) : $($user.Value) logins`n"
    }
} else {
    $report += @"

================================================================================
EXTERNAL USERS
================================================================================

No external users detected this month.

"@
}

# Extract graph usage
$graphUpdates = $allLogs | Select-String "Graph.*Update"
$clientViews = @{}

foreach ($line in $graphUpdates) {
    if ($line -match "Client: ([^|]+)") {
        $client = $matches[1].Trim()
        if (-not $clientViews.ContainsKey($client)) {
            $clientViews[$client] = 0
        }
        $clientViews[$client]++
    }
}

if ($clientViews.Count -gt 0) {
    $report += @"

================================================================================
TOP CLIENTS ANALYZED (Top 15)
================================================================================

"@
    foreach ($client in ($clientViews.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 15)) {
        $report += "$($client.Name) : $($client.Value) views`n"
    }
}

$report += @"

================================================================================
END OF REPORT
================================================================================
"@

# Save report
$report | Out-File $reportFile -Encoding UTF8

# Display report
Write-Host $report
Write-Host ""
Write-Host "Report saved to: $reportFile" -ForegroundColor Green

# Made with Bob
