# Dashboard Usage Logging Guide

## Overview
The dashboard now includes Flask-based request logging to track usage without requiring IBM Cloud monitoring services. All logs are written to stdout and can be viewed using IBM Cloud Code Engine CLI commands.

## What's Being Logged

### 1. Dashboard Access Logs
Every time someone accesses the dashboard, the following is logged:
- **Timestamp**: When the access occurred
- **IP Address**: The user's IP address
- **Path**: The specific dashboard path accessed
- **HTTP Method**: GET, POST, etc.

**Example Log Entry:**
```
2026-04-28 09:15:23 - INFO - Dashboard Access | IP: 192.168.1.100 | Path: /dashboard/ | Method: GET
```

### 2. Graph Update Logs
Each time a graph is updated (user changes filters, selects different client, etc.), the following is logged:

**Graph 1 (Severity Analysis):**
```
2026-04-28 09:16:45 - INFO - Graph 1 Update | Client: CAPITAL ONE FINANCIAL CORP | Date Filter: 6 Months | Product Group: All Products
```

**Graph 2 (End of Support Status):**
```
2026-04-28 09:17:12 - INFO - Graph 2 Update | Client: METLIFE | Date Filter: 1 year | Product Group: Hardware
```

**Graph 3 (Defect vs How-To Analysis):**
```
2026-04-28 09:18:30 - INFO - Graph 3 Update | Client: CAPITAL ONE FINANCIAL CORP | Date Filter: 3 Months | Product Group: Software
```

## How to View Logs

### Prerequisites
- IBM Cloud CLI installed
- Logged into IBM Cloud: `ibmcloud login`
- Target your resource group: `ibmcloud target -g <resource-group>`
- Select your Code Engine project: `ibmcloud ce project select --name python-appid-proj`

### View Real-Time Logs
To see logs as they happen (tail mode):
```powershell
ibmcloud ce application logs --name python-appid-app --follow
```

### View Recent Logs
To see the last 100 log entries:
```powershell
ibmcloud ce application logs --name python-appid-app --tail 100
```

### View Logs from Recent History
The current Code Engine CLI in this environment does **not** support `--since` for `application logs`.

Use a larger tail count instead:
```powershell
ibmcloud ce application logs --name python-appid-app --tail 2000
```

Approximate recent-history options:
- `--tail 500` for a smaller recent sample
- `--tail 2000` for more recent history
- `--tail 5000` if you need a broader window

### Filter Logs
These examples are for **PowerShell on Windows**. Use `Select-String` instead of `grep`.

To see only dashboard access logs:
```powershell
ibmcloud ce application logs --name python-appid-app --tail 500 | Select-String "Dashboard Access"
```

To see only graph update logs:
```powershell
ibmcloud ce application logs --name python-appid-app --tail 500 | Select-String "Graph"
```

To see logs for a specific client:
```powershell
ibmcloud ce application logs --name python-appid-app --tail 500 | Select-String "CAPITAL ONE"
```

## Usage Analysis Examples

### Count Total Dashboard Accesses
```powershell
(ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "Dashboard Access").Count
```

### See Which Clients Are Being Analyzed
```powershell
ibmcloud ce application logs --name python-appid-app --tail 500 |
    Select-String "Graph 1 Update" |
    ForEach-Object {
        if ($_ -match "Client: ([^|]+)") { $matches[1].Trim() }
    } |
    Group-Object |
    Sort-Object Count -Descending
```

### See Which Date Filters Are Most Popular
```powershell
ibmcloud ce application logs --name python-appid-app --tail 500 |
    Select-String "Date Filter" |
    ForEach-Object {
        if ($_ -match "Date Filter: ([^|]+)") { $matches[1].Trim() }
    } |
    Group-Object |
    Sort-Object Count -Descending
```

### See Which Product Groups Are Most Used
```powershell
ibmcloud ce application logs --name python-appid-app --tail 500 |
    Select-String "Product Group" |
    ForEach-Object {
        if ($_ -match "Product Group: ([^|]+)") { $matches[1].Trim() }
    } |
    Group-Object |
    Sort-Object Count -Descending
```

## Log Retention

**Important:** Code Engine logs are retained for a limited time (typically 7-10 days). For long-term analysis:

1. **Export logs regularly:**
   ```powershell
   $date = Get-Date -Format "yyyyMMdd"
   ibmcloud ce application logs --name python-appid-app --tail 10000 > "dashboard_logs_$date.txt"
   ```

2. **Schedule weekly exports** (create a script):
   ```powershell
   $date = Get-Date -Format "yyyyMMdd"
   $logDir = "C:\DashboardLogs"
   if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

   ibmcloud target -g <your-resource-group>
   ibmcloud ce project select --name python-appid-proj
   ibmcloud ce application logs --name python-appid-app --tail 10000 > "$logDir\logs_$date.txt"
   ```

3. **Analyze exported logs** using PowerShell:
   ```powershell
   # Count accesses per day
   Get-ChildItem . -Filter "dashboard_logs_*.txt" |
       Select-String "Dashboard Access" |
       Group-Object { $_.Line.Split(' ')[0] } |
       Sort-Object Name

   # Most active users by IP
   Get-ChildItem . -Filter "dashboard_logs_*.txt" |
       Select-String "Dashboard Access" |
       ForEach-Object {
           if ($_.Line -match "IP: ([0-9.]+)") { $matches[1] }
       } |
       Group-Object |
       Sort-Object Count -Descending
   ```

## Privacy Considerations

The logs include IP addresses. If this is a concern:
- IP addresses can help identify if the dashboard is being used
- They don't identify specific users (IBM App ID handles authentication separately)
- Consider your organization's data retention policies

## Troubleshooting

### No Logs Appearing
1. Verify the application is running:
   ```bash
   ibmcloud ce application get --name python-appid-app
   ```

2. Check if there are any application errors:
   ```bash
   ibmcloud ce application logs --name python-appid-app --tail 50
   ```

### Too Many Logs
If logs are overwhelming, you can:
1. Increase the tail number: `--tail 5000`
2. Export to file and analyze offline
3. Use `Select-String` in PowerShell to filter specific information

## Next Steps

After collecting usage data for a few weeks, you can:
1. Identify peak usage times
2. Determine which clients are most frequently analyzed
3. See which features (graphs, filters) are most valuable
4. Make data-driven decisions about dashboard improvements
5. Justify continued maintenance and enhancements

## Code Changes Made

The following changes were made to `app.py`:

1. **Added imports** (line ~36):
   ```python
   import logging
   from flask import request
   ```

2. **Added logging configuration** (after line 353):
   ```python
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger(__name__)
   
   @auth.flask.before_request
   def log_request():
       if request.path.startswith('/dashboard'):
           logger.info(f"Dashboard Access | IP: {request.remote_addr} | Path: {request.path} | Method: {request.method}")
   ```

3. **Added logging to callbacks**:
   - Graph 1 update function (line ~1036)
   - Graph 2 update function (line ~1209)
   - Graph 3 update function (line ~1431)

## Deployment

To deploy these changes:
```bash
# Commit changes
git add Dashboard_Deployment/app.py Dashboard_Deployment/USAGE_LOGGING_GUIDE.md
git commit -m "Add usage logging to track dashboard activity"
git push origin main

# Deploy to Code Engine
ibmcloud ce application update --name python-appid-app --build-source .
```

After deployment, logs will start appearing immediately as users access the dashboard.