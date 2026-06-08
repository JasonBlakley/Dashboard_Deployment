# Historical Logging Guide for Dashboard

## Current Logging Limitations

### IBM Cloud Code Engine Default Logging
- **Retention**: Logs are only kept in memory for currently running application instances
- **Access**: Via `ibmcloud ce application logs` command
- **Limitation**: When instances restart or are replaced, old logs are lost
- **Typical Retention**: Hours to a few days, depending on instance lifecycle

### What This Means
- You can see recent activity (last few hours/days)
- Historical logs beyond current instance lifetime are NOT available
- No built-in 30-day or long-term log retention

## Solutions for Historical Logging

### Option 1: IBM Log Analysis (Recommended for Enterprise)
IBM Cloud offers Log Analysis service for long-term log retention.

**Setup Steps:**
1. Create IBM Log Analysis instance in your IBM Cloud account
2. Configure Code Engine to send logs to Log Analysis
3. Set retention period (7, 14, 30, or more days)
4. Query historical logs through Log Analysis dashboard

**Cost:** Starts at ~$0.30/GB ingested + storage costs

**Benefits:**
- Long-term retention (30+ days)
- Advanced search and filtering
- Dashboards and alerts
- Export capabilities

**Documentation:**
https://cloud.ibm.com/docs/log-analysis

### Option 2: Export Logs to Cloud Object Storage (Cost-Effective)
Periodically export logs to IBM Cloud Object Storage for archival.

**Implementation:**
```powershell
# Daily export script (run via scheduled task)
$date = Get-Date -Format "yyyy-MM-dd"
$logFile = "dashboard-logs-$date.txt"

# Export logs
ibmcloud ce application logs --name python-appid-app --tail 10000 --timestamps > $logFile

# Upload to Cloud Object Storage (requires ibmcloud cos plugin)
ibmcloud cos upload --bucket dashboard-logs-archive --key "logs/$logFile" --file $logFile
```

**Benefits:**
- Very low cost (~$0.023/GB/month storage)
- Full control over retention
- Can process logs offline

**Limitations:**
- Requires manual setup and scheduling
- Not real-time
- Gaps if script doesn't run

### Option 3: Application-Level Logging to Database
Modify the application to write important events to a database.

**Implementation Example:**
```python
# Add to app.py
import sqlite3
from datetime import datetime

def log_to_db(event_type, user_email, details):
    conn = sqlite3.connect('dashboard_logs.db')
    c = conn.cursor()
    c.execute('''INSERT INTO logs (timestamp, event_type, user_email, details)
                 VALUES (?, ?, ?, ?)''',
              (datetime.now(), event_type, user_email, details))
    conn.commit()
    conn.close()

# In auth.py after line 70:
log_to_db('login', user_email, 'User logged in')
```

**Benefits:**
- Complete control
- Queryable with SQL
- Can store indefinitely

**Limitations:**
- Requires code changes
- Need to manage database
- Storage grows over time

### Option 4: Third-Party Logging Service
Use services like Datadog, Splunk, or Loggly.

**Benefits:**
- Professional features
- Easy setup
- Reliable retention

**Limitations:**
- Additional cost
- External dependency

## Current Workaround: Regular Log Exports

Since you just deployed the logging today, here's a practical approach:

### Weekly Log Export Script
Create a PowerShell script to run weekly:

```powershell
# weekly-log-export.ps1
$date = Get-Date -Format "yyyy-MM-dd"
$logDir = "C:\DashboardLogs"
$logFile = "$logDir\dashboard-logs-$date.txt"

# Create directory if it doesn't exist
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir
}

# Export logs with timestamps
ibmcloud ce application logs --name python-appid-app --tail 50000 --timestamps > $logFile

# Extract login events
$loginFile = "$logDir\logins-$date.txt"
Get-Content $logFile | Select-String "logged in" > $loginFile

Write-Host "Logs exported to $logFile"
Write-Host "Login events extracted to $loginFile"

# Optional: Keep only last 90 days
Get-ChildItem $logDir -Filter "*.txt" | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-90) } | 
    Remove-Item
```

**Schedule this script:**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Weekly, Sunday at 11:59 PM
4. Action: Start a program
5. Program: `powershell.exe`
6. Arguments: `-File "C:\path\to\weekly-log-export.ps1"`

### Monthly Login Report Script
```powershell
# monthly-login-report.ps1
$month = Get-Date -Format "yyyy-MM"
$reportFile = "C:\DashboardLogs\login-report-$month.csv"

# Collect all login files from the month
$loginFiles = Get-ChildItem "C:\DashboardLogs" -Filter "logins-*.txt" | 
    Where-Object { $_.Name -match $month }

# Parse and create CSV
$logins = @()
foreach ($file in $loginFiles) {
    $content = Get-Content $file.FullName
    foreach ($line in $content) {
        if ($line -match "(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}).*User (.*?) logged in") {
            $logins += [PSCustomObject]@{
                Timestamp = $matches[1]
                Email = $matches[2]
                Domain = ($matches[2] -split '@')[1]
            }
        }
    }
}

$logins | Export-Csv -Path $reportFile -NoTypeInformation
Write-Host "Monthly report created: $reportFile"
Write-Host "Total logins: $($logins.Count)"
Write-Host "Unique users: $(($logins | Select-Object -Unique Email).Count)"
```

## Recommendations

### For Your Use Case (Tracking External Users)
Given that you want to track external user access over time:

**Short-term (Next 30 days):**
1. Set up the weekly export script immediately
2. This will capture all logs going forward
3. Run it manually today to get a baseline

**Long-term (After 30 days):**
1. Evaluate if IBM Log Analysis is worth the cost
2. If budget allows: Set up Log Analysis with 30-day retention
3. If budget constrained: Continue with weekly exports + monthly reports

### Immediate Action Items
1. ✅ Login logging is already implemented (auth.py line 70)
2. ✅ Dashboard access logging is working (app.py)
3. ⏳ Set up weekly log export script (do this today)
4. ⏳ Test login logging by logging out and back in
5. ⏳ Decide on long-term logging strategy

## Viewing Historical Logs (Once Exports Start)

After you start exporting logs weekly, you can query them:

```powershell
# Find all logins in the last 30 days
Get-ChildItem "C:\DashboardLogs" -Filter "logins-*.txt" | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-30) } | 
    Get-Content | Select-String "logged in"

# Count logins by domain
Get-ChildItem "C:\DashboardLogs" -Filter "logins-*.txt" | 
    Get-Content | 
    Select-String "User (.*?)@(.*?) logged in" | 
    ForEach-Object { $_.Matches.Groups[2].Value } | 
    Group-Object | 
    Sort-Object Count -Descending

# Find specific user's logins
Get-ChildItem "C:\DashboardLogs" -Filter "logins-*.txt" | 
    Get-Content | 
    Select-String "user@example.com"
```

## Summary

**Current State:**
- Login logging is implemented and working
- Logs only available for current running instances (hours to days)
- No 30-day historical logs available yet

**To Get 30-Day History:**
- Start exporting logs weekly NOW
- After 30 days, you'll have 30 days of history
- Or set up IBM Log Analysis for immediate long-term retention

**Cost Comparison:**
- Weekly exports: Free (just storage space)
- IBM Log Analysis: ~$50-100/month (depending on volume)
- Cloud Object Storage: ~$1-5/month for log archives