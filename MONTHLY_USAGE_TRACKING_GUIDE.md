# Monthly Dashboard Usage Tracking Guide

## Overview
This guide provides a complete solution for tracking dashboard usage month-by-month, including automated log collection, analysis scripts, and reporting templates.

---

## Problem with Current Approach

**IBM Cloud Code Engine logs are only retained for 7-10 days**, so we need to:
1. Export logs regularly (weekly or daily)
2. Store them locally or in cloud storage
3. Analyze them monthly to generate usage reports

---

## Solution: Automated Weekly Log Export

### Step 1: Create Weekly Export Script

Save this as `Dashboard_Deployment/export_weekly_logs.ps1`:

```powershell
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
```

### Step 2: Schedule Weekly Exports

**Option A: Windows Task Scheduler**
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Dashboard Log Export"
4. Trigger: Weekly (every Monday at 9 AM)
5. Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\path\to\export_weekly_logs.ps1"`

**Option B: Manual Weekly Run**
```powershell
cd Dashboard_Deployment
./export_weekly_logs.ps1
```

---

## Monthly Usage Analysis Script

### Create Analysis Script

Save this as `Dashboard_Deployment/analyze_monthly_usage.ps1`:

```powershell
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
$logFiles = Get-ChildItem -Path $logDir -Filter "dashboard_logs_$Month-*.txt"

if ($logFiles.Count -eq 0) {
    Write-Host "No log files found for $Month" -ForegroundColor Red
    Write-Host "Looking in: $logDir" -ForegroundColor Yellow
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
Average Logins per Day: $([math]::Round($loginLines.Count / $dailyLogins.Count, 2))

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

foreach ($user in ($ibmUsers.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 10)) {
    $report += "$($user.Name) : $($user.Value) logins`n"
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
```

---

## Usage Workflow

### Weekly (Every Monday)
```powershell
# Export last week's logs
cd Dashboard_Deployment
./export_weekly_logs.ps1
```

### Monthly (First of each month)
```powershell
# Analyze previous month
cd Dashboard_Deployment
./analyze_monthly_usage.ps1 -Month "2026-05"
```

---

## Alternative: Daily Export (More Granular)

For more detailed tracking, export logs daily:

```powershell
# Daily export script (export_daily_logs.ps1)
$date = Get-Date -Format "yyyy-MM-dd"
$logFile = "Dashboard_Logs/dashboard_logs_$date.txt"

ibmcloud ce application logs --name python-appid-app --tail 1000 > $logFile
Write-Host "Exported logs to $logFile"
```

Schedule this to run every day at midnight.

---

## Storage Recommendations

### Local Storage
```
Dashboard_Logs/
├── dashboard_logs_2026-05-01.txt
├── dashboard_logs_2026-05-08.txt
├── dashboard_logs_2026-05-15.txt
├── dashboard_logs_2026-05-22.txt
└── dashboard_logs_2026-05-29.txt
```

### Cloud Storage (Optional)
Upload monthly archives to IBM Cloud Object Storage:

```powershell
# Archive and upload monthly logs
$month = "2026-05"
$archiveFile = "dashboard_logs_$month.zip"

# Compress logs
Compress-Archive -Path "Dashboard_Logs/dashboard_logs_$month-*.txt" -DestinationPath $archiveFile

# Upload to COS
ibmcloud cos object-put --bucket oidash-app --key "usage_logs/$archiveFile" --body $archiveFile
```

---

## Quick Analysis Commands

### Users per day (current logs)
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | 
    Select-String "logged in" | 
    ForEach-Object { 
        if ($_ -match "^(\d{4}-\d{2}-\d{2})") { $matches[1] } 
    } | 
    Group-Object | 
    Sort-Object Name | 
    Format-Table Name, Count -AutoSize
```

### Users per month (from exported logs)
```powershell
Get-Content Dashboard_Logs/dashboard_logs_2026-05-*.txt | 
    Select-String "logged in" | 
    ForEach-Object { 
        if ($_ -match "User ([^\s]+)") { $matches[1] } 
    } | 
    Group-Object | 
    Measure-Object | 
    Select-Object Count
```

### External users this month
```powershell
Get-Content Dashboard_Logs/dashboard_logs_2026-05-*.txt | 
    Select-String "logged in" | 
    Select-String -NotMatch "@ibm.com" | 
    ForEach-Object { 
        if ($_ -match "User ([^\s]+)") { $matches[1] } 
    } | 
    Sort-Object -Unique
```

---

## Sample Monthly Report Output

```
================================================================================
DASHBOARD USAGE REPORT
Month: 2026-05
Generated: 2026-06-01 09:00:00
================================================================================

SUMMARY
-------
Total Unique Users: 8
  - IBM Users: 6
  - External Users: 2

Total Logins: 47
  - IBM Logins: 42
  - External Logins: 5

Active Days: 18
Average Logins per Day: 2.61

================================================================================
DAILY BREAKDOWN
================================================================================

2026-05-01 : 3 logins
2026-05-02 : 2 logins
2026-05-03 : 4 logins
2026-05-06 : 2 logins
2026-05-07 : 3 logins
...

================================================================================
IBM USERS (Top 10 by login count)
================================================================================

Darshan.Patil@ibm.com : 15 logins
Brian.Christensen@ibm.com : 12 logins
Jason.Blakley@ibm.com : 8 logins
...

================================================================================
EXTERNAL USERS
================================================================================

john.doe@capitalone.com : 3 logins
jane.smith@metlife.com : 2 logins

================================================================================
TOP CLIENTS ANALYZED (Top 15)
================================================================================

CAPITAL ONE FINANCIAL CORP : 45 views
METLIFE : 32 views
AXA : 28 views
...
```

---

## Best Practices

1. **Export Weekly**: Don't wait until logs expire (7-10 days)
2. **Automate**: Use Task Scheduler for hands-off operation
3. **Archive Monthly**: Compress and store old logs
4. **Review Quarterly**: Look for trends and patterns
5. **Share Reports**: Send monthly summaries to stakeholders

---

## Troubleshooting

### Logs Missing
- Check if Task Scheduler ran successfully
- Verify IBM Cloud login hasn't expired
- Increase `--tail` value if needed

### Analysis Script Errors
- Ensure log files exist in Dashboard_Logs directory
- Check file naming matches pattern: `dashboard_logs_YYYY-MM-DD.txt`
- Verify PowerShell execution policy allows scripts

---

**Last Updated**: May 12, 2026  
**Next Steps**: Set up weekly export automation