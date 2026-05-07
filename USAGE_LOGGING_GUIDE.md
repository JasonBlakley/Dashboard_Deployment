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

### View Real-Time Logs
To see logs as they happen (tail mode):
```bash
ibmcloud ce application logs --name python-appid-app --follow
```

### View Recent Logs
To see the last 100 log entries:
```bash
ibmcloud ce application logs --name python-appid-app --tail 100
```

### View Logs from Specific Time Period
To see logs from the last hour:
```bash
ibmcloud ce application logs --name python-appid-app --since 1h
```

Other time options:
- `--since 30m` (last 30 minutes)
- `--since 24h` (last 24 hours)
- `--since 7d` (last 7 days)

### Filter Logs
To see only dashboard access logs:
```bash
ibmcloud ce application logs --name python-appid-app --tail 500 | grep "Dashboard Access"
```

To see only graph update logs:
```bash
ibmcloud ce application logs --name python-appid-app --tail 500 | grep "Graph"
```

To see logs for a specific client:
```bash
ibmcloud ce application logs --name python-appid-app --tail 500 | grep "CAPITAL ONE"
```

## Usage Analysis Examples

### Count Total Dashboard Accesses
```bash
ibmcloud ce application logs --name python-appid-app --tail 1000 | grep "Dashboard Access" | wc -l
```

### See Which Clients Are Being Analyzed
```bash
ibmcloud ce application logs --name python-appid-app --tail 500 | grep "Graph 1 Update" | grep -o "Client: [^|]*" | sort | uniq -c
```

### See Which Date Filters Are Most Popular
```bash
ibmcloud ce application logs --name python-appid-app --tail 500 | grep "Date Filter" | grep -o "Date Filter: [^|]*" | sort | uniq -c
```

### See Which Product Groups Are Most Used
```bash
ibmcloud ce application logs --name python-appid-app --tail 500 | grep "Product Group" | grep -o "Product Group: [^|]*" | sort | uniq -c
```

## Log Retention

**Important:** Code Engine logs are retained for a limited time (typically 7-10 days). For long-term analysis:

1. **Export logs regularly:**
   ```bash
   ibmcloud ce application logs --name python-appid-app --tail 10000 > dashboard_logs_$(date +%Y%m%d).txt
   ```

2. **Schedule weekly exports** (create a script):
   ```bash
   #!/bin/bash
   # weekly_log_export.sh
   ibmcloud login --apikey $IBM_CLOUD_API_KEY
   ibmcloud target -g <your-resource-group>
   ibmcloud ce application logs --name python-appid-app --tail 10000 > ~/dashboard_logs/logs_$(date +%Y%m%d).txt
   ```

3. **Analyze exported logs** using standard text processing tools:
   ```bash
   # Count accesses per day
   grep "Dashboard Access" dashboard_logs_*.txt | cut -d' ' -f1 | sort | uniq -c
   
   # Most active users by IP
   grep "Dashboard Access" dashboard_logs_*.txt | grep -o "IP: [0-9.]*" | sort | uniq -c | sort -rn
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
3. Use grep to filter specific information

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