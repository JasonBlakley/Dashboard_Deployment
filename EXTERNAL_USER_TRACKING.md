# Tracking External (Non-IBM) Dashboard Users

## Current Situation

The dashboard logs show all requests coming from `IP: 127.0.0.1` because:
1. The dashboard is behind IBM App ID authentication
2. Requests go through IBM Cloud's load balancer/proxy
3. The actual client IP is masked by the infrastructure

## How to Identify External Users

### Method 1: Check Login Events (BEST METHOD)

Look for login events in the logs. IBM users will have `@ibm.com` email addresses, external users will have other domains:

**Command to find all logins:**
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "logged in"
```

**Example output:**
```
INFO:root: User Jason.Blakley@ibm.com logged in          # IBM user
INFO:root: User john.doe@capitalone.com logged in        # External user (Capital One)
INFO:root: User jane.smith@metlife.com logged in         # External user (MetLife)
INFO:root: User bob.jones@axa.com logged in              # External user (AXA)
```

**Filter for external users only (non-IBM):**
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "logged in" | Select-String -NotMatch "@ibm.com"
```

### Method 2: Analyze Client Selection Patterns

External users typically view their own company's data. Look at which clients are being viewed:

**Command:**
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "Graph.*Update.*Client:"
```

**Example output:**
```
INFO:__main__:Graph 1 Update | Client: AXA | Date Filter: 6 Months | Product Group: None
INFO:__main__:Graph 2 Update | Client: CAPITAL ONE FINANCIAL CORP | Date Filter: 1 year | Product Group: Software
INFO:__main__:Graph 3 Update | Client: METLIFE | Date Filter: 3 Months | Product Group: Hardware
```

**Pattern Analysis:**
- If someone consistently views only ONE client (e.g., always "CAPITAL ONE"), they're likely from that company
- IBM users typically view multiple different clients

### Method 3: Correlate Login with Client Views

Combine both methods to identify external users:

1. **Export logs to file:**
```powershell
ibmcloud ce application logs --name python-appid-app --tail 5000 > dashboard_logs.txt
```

2. **Analyze in PowerShell:**
```powershell
# Find all logins
$logins = Select-String -Path dashboard_logs.txt -Pattern "logged in"

# Find all graph updates
$graphUpdates = Select-String -Path dashboard_logs.txt -Pattern "Graph.*Update.*Client:"

# Display together
Write-Host "=== LOGINS ===" -ForegroundColor Green
$logins | ForEach-Object { $_.Line }

Write-Host "`n=== CLIENT VIEWS ===" -ForegroundColor Green  
$graphUpdates | ForEach-Object { $_.Line }
```

3. **Look for patterns:**
   - Login timestamp: `2026-04-28 12:40:52`
   - Followed by views of specific client: `Client: CAPITAL ONE`
   - If email is `@capitalone.com` and they only view Capital One data → External user

## Weekly Usage Report Script

Create a PowerShell script to generate weekly reports:

```powershell
# weekly_usage_report.ps1
$date = Get-Date -Format "yyyy-MM-dd"
$logFile = "dashboard_logs_$date.txt"

# Get logs
ibmcloud ce application logs --name python-appid-app --tail 10000 > $logFile

# Extract logins
$allLogins = Select-String -Path $logFile -Pattern "logged in"
$ibmLogins = $allLogins | Select-String "@ibm.com"
$externalLogins = $allLogins | Select-String -NotMatch "@ibm.com"

# Extract client views
$clientViews = Select-String -Path $logFile -Pattern "Graph 1 Update.*Client:" | 
    ForEach-Object { 
        if ($_ -match "Client: ([^|]+)") { 
            $matches[1].Trim() 
        } 
    } | Group-Object | Sort-Object Count -Descending

# Generate report
$report = @"
=== DASHBOARD USAGE REPORT ===
Date: $date

TOTAL LOGINS: $($allLogins.Count)
- IBM Users: $($ibmLogins.Count)
- External Users: $($externalLogins.Count)

EXTERNAL USER LOGINS:
$($externalLogins | ForEach-Object { $_.Line } | Out-String)

TOP CLIENTS VIEWED:
$($clientViews | ForEach-Object { "$($_.Name): $($_.Count) views" } | Out-String)

DETAILED LOGS:
See $logFile for full details
"@

# Save report
$report | Out-File "usage_report_$date.txt"

Write-Host $report
Write-Host "`nReport saved to: usage_report_$date.txt" -ForegroundColor Green
```

## Real-Time Monitoring for External Users

To watch for external users in real-time:

```powershell
# Monitor for non-IBM logins
ibmcloud ce application logs --name python-appid-app --follow | Select-String "logged in" | Where-Object { $_ -notmatch "@ibm.com" }
```

This will show ONLY external user logins as they happen.

## Understanding the Current Logs

From your provided logs, I can see:
- **User:** Jason.Blakley@ibm.com (IBM user)
- **Activity:** Viewing AXA client data
- **Time:** Around 14:05 UTC (10:05 AM EDT)
- **Graphs viewed:** All 3 graphs (severity, EOS status, defect analysis)

**No external users detected in the provided logs** - only IBM internal usage so far.

## Tips for Identifying External Users

1. **Email domains to watch for:**
   - `@capitalone.com` - Capital One users
   - `@metlife.com` - MetLife users  
   - `@axa.com` - AXA users
   - Any non-`@ibm.com` domain

2. **Behavior patterns:**
   - External users typically:
     - View only their company's data
     - Access during business hours in their timezone
     - May have less frequent but more focused sessions
   
   - IBM users typically:
     - View multiple different clients
     - May access at various times
     - More exploratory behavior

3. **Authentication events:**
   - Look for `"User [email] logged in"` messages
   - These appear when someone authenticates via IBM App ID
   - Timestamp shows when they accessed the dashboard

## Next Steps

1. **Run weekly reports** to track usage trends
2. **Monitor for external logins** using the real-time command
3. **Correlate login times with client views** to understand usage patterns
4. **Export logs monthly** for long-term analysis (Code Engine only keeps logs ~7-10 days)

## Example Analysis

To answer "Did any external users access the dashboard this week?":

```powershell
# Get last 7 days of logs (if available)
ibmcloud ce application logs --name python-appid-app --tail 10000 > recent_logs.txt

# Check for external logins
$external = Select-String -Path recent_logs.txt -Pattern "logged in" | Select-String -NotMatch "@ibm.com"

if ($external.Count -gt 0) {
    Write-Host "YES - External users detected:" -ForegroundColor Green
    $external | ForEach-Object { $_.Line }
} else {
    Write-Host "NO - Only IBM users detected" -ForegroundColor Yellow
}