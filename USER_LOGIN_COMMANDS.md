# Dashboard User Login & Usage Commands

Quick reference for checking who's accessing the dashboard and how they're using it.

---

## Check Recent Logins

### View all recent logins (last 1000 log entries)
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "logged in"
```

### View only external (non-IBM) user logins
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "logged in" | Select-String -NotMatch "@ibm.com"
```

### View only IBM user logins
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "logged in" | Select-String "@ibm.com"
```

### Get unique users who logged in recently
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "logged in" | ForEach-Object { if ($_ -match "User (.*?) logged in") { $matches[1] } } | Sort-Object -Unique
```

---

## Check Dashboard Usage

### See what clients users are viewing
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "Graph.*Update.*Client:"
```

### Count views by client
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "Graph 1 Update.*Client:" | ForEach-Object { if ($_ -match "Client: ([^|]+)") { $matches[1].Trim() } } | Group-Object | Sort-Object Count -Descending | Format-Table Name, Count
```

### See all activity for a specific user
```powershell
# Replace with actual email
$userEmail = "Jason.Blakley@ibm.com"
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String $userEmail
```

---

## Export Logs for Analysis

### Export last 5000 log entries to file
```powershell
ibmcloud ce application logs --name python-appid-app --tail 5000 > dashboard_logs_$(Get-Date -Format 'yyyy-MM-dd').txt
```

### Export and analyze in one command
```powershell
# Export logs
$logFile = "dashboard_logs_$(Get-Date -Format 'yyyy-MM-dd').txt"
ibmcloud ce application logs --name python-appid-app --tail 5000 > $logFile

# Analyze logins
Write-Host "`n=== LOGIN SUMMARY ===" -ForegroundColor Cyan
$logins = Select-String -Path $logFile -Pattern "logged in"
Write-Host "Total logins: $($logins.Count)"

$ibmLogins = $logins | Select-String "@ibm.com"
Write-Host "IBM users: $($ibmLogins.Count)"

$externalLogins = $logins | Select-String -NotMatch "@ibm.com"
Write-Host "External users: $($externalLogins.Count)"

# Show unique users
Write-Host "`n=== UNIQUE USERS ===" -ForegroundColor Cyan
$logins | ForEach-Object { if ($_ -match "User (.*?) logged in") { $matches[1] } } | Sort-Object -Unique
```

---

## Real-Time Monitoring

### Watch for logins in real-time
```powershell
ibmcloud ce application logs --name python-appid-app --follow | Select-String "logged in"
```

### Watch for external user logins only
```powershell
ibmcloud ce application logs --name python-appid-app --follow | Select-String "logged in" | Where-Object { $_ -notmatch "@ibm.com" }
```

### Watch for specific client views
```powershell
# Replace with client name
$clientName = "CAPITAL ONE"
ibmcloud ce application logs --name python-appid-app --follow | Select-String "Client: $clientName"
```

---

## Check Users with Dashboard Access (App ID)

### Get all users with roles (who can access dashboard)
```powershell
$env:TENANT_ID="85831e0f-ac91-43d8-ad79-54b378e57a82"
$token = (ibmcloud iam oauth-tokens --output json | ConvertFrom-Json).iam_token
$headers = @{ "Authorization" = $token }

# Get first 100 users
$response = Invoke-RestMethod -Uri "https://us-south.appid.cloud.ibm.com/management/v4/$env:TENANT_ID/users?startIndex=1&count=100" -Headers $headers -Method Get

# Check each user for roles
$usersWithAccess = @()
foreach ($user in $response.users) {
    try {
        $rolesResponse = Invoke-RestMethod -Uri "https://us-south.appid.cloud.ibm.com/management/v4/$env:TENANT_ID/users/$($user.id)/roles" -Headers $headers -Method Get -ErrorAction SilentlyContinue
        if ($rolesResponse.roles -and $rolesResponse.roles.Count -gt 0) {
            $usersWithAccess += [PSCustomObject]@{
                Email = $user.email
                Roles = ($rolesResponse.roles.name -join ", ")
            }
        }
    } catch { }
}

$usersWithAccess | Format-Table -AutoSize
Write-Host "`nTotal users with access: $($usersWithAccess.Count)"
```

### Quick check: How many users have access?
```powershell
$csv = Import-Csv "dashboard_users_with_access.csv"
Write-Host "Users with dashboard access: $($csv.Count)"
$csv | Select-Object -First 10 | Format-Table
```

---

## Weekly Usage Report

### Generate weekly summary
```powershell
$date = Get-Date -Format "yyyy-MM-dd"
$logFile = "dashboard_logs_$date.txt"

# Get logs
ibmcloud ce application logs --name python-appid-app --tail 10000 > $logFile

# Extract logins
$allLogins = Select-String -Path $logFile -Pattern "logged in"
$ibmLogins = $allLogins | Select-String "@ibm.com"
$externalLogins = $allLogins | Select-String -NotMatch "@ibm.com"

# Extract unique users
$uniqueUsers = $allLogins | ForEach-Object { 
    if ($_ -match "User (.*?) logged in") { $matches[1] } 
} | Sort-Object -Unique

# Extract client views
$clientViews = Select-String -Path $logFile -Pattern "Graph 1 Update.*Client:" | 
    ForEach-Object { 
        if ($_ -match "Client: ([^|]+)") { $matches[1].Trim() } 
    } | Group-Object | Sort-Object Count -Descending

# Generate report
$report = @"
=== DASHBOARD USAGE REPORT ===
Date: $date

TOTAL LOGINS: $($allLogins.Count)
- IBM Users: $($ibmLogins.Count)
- External Users: $($externalLogins.Count)

UNIQUE USERS: $($uniqueUsers.Count)
$($uniqueUsers | Out-String)

TOP CLIENTS VIEWED:
$($clientViews | ForEach-Object { "$($_.Name): $($_.Count) views" } | Out-String)

EXTERNAL USER LOGINS:
$($externalLogins | ForEach-Object { $_.Line } | Out-String)
"@

# Display and save
Write-Host $report
$report | Out-File "usage_report_$date.txt"
Write-Host "`nReport saved to: usage_report_$date.txt" -ForegroundColor Green
```

---

## Common Scenarios

### "Did anyone access the dashboard today?"
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "logged in" | Select-Object -First 10
```

### "Who viewed Capital One data this week?"
```powershell
ibmcloud ce application logs --name python-appid-app --tail 5000 | Select-String "Client: CAPITAL ONE"
```

### "Has [specific user] logged in recently?"
```powershell
$userEmail = "john.doe@ibm.com"
ibmcloud ce application logs --name python-appid-app --tail 2000 | Select-String $userEmail | Select-String "logged in"
```

### "What's the most viewed client?"
```powershell
ibmcloud ce application logs --name python-appid-app --tail 5000 | Select-String "Graph 1 Update.*Client:" | ForEach-Object { if ($_ -match "Client: ([^|]+)") { $matches[1].Trim() } } | Group-Object | Sort-Object Count -Descending | Select-Object -First 5
```

---

## Troubleshooting

### No logs showing up
```powershell
# Check if application is running
ibmcloud ce application get --name python-appid-app

# Check application status
ibmcloud ce application list
```

### Need more history
```powershell
# Increase tail count (max ~10000)
ibmcloud ce application logs --name python-appid-app --tail 10000 > large_log_export.txt
```

### Want to see all log types (not just logins)
```powershell
# View all logs
ibmcloud ce application logs --name python-appid-app --tail 1000
```

---

## Scheduled Monitoring

### Set up weekly log export (Windows Task Scheduler)

1. Save this as `weekly-dashboard-logs.ps1`:
```powershell
$date = Get-Date -Format "yyyy-MM-dd"
$logDir = "C:\DashboardLogs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir }

ibmcloud ce application logs --name python-appid-app --tail 10000 > "$logDir\logs-$date.txt"

# Generate summary
$logins = Select-String -Path "$logDir\logs-$date.txt" -Pattern "logged in"
$summary = @"
Dashboard Logs - $date
Total Logins: $($logins.Count)
Unique Users: $(($logins | ForEach-Object { if ($_ -match "User (.*?) logged in") { $matches[1] } } | Sort-Object -Unique).Count)
"@

$summary | Out-File "$logDir\summary-$date.txt"
```

2. Create scheduled task:
   - Open Task Scheduler
   - Create Basic Task: "Weekly Dashboard Logs"
   - Trigger: Weekly, Monday, 9:00 AM
   - Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\Path\To\weekly-dashboard-logs.ps1"`

---

## Quick Reference Card

```powershell
# Most common commands:

# Recent logins
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "logged in"

# External users only
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "logged in" | Select-String -NotMatch "@ibm.com"

# Client views
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "Graph.*Update.*Client:"

# Export logs
ibmcloud ce application logs --name python-appid-app --tail 5000 > logs.txt

# Real-time monitoring
ibmcloud ce application logs --name python-appid-app --follow | Select-String "logged in"
```

---

*Last Updated: 2026-04-28*