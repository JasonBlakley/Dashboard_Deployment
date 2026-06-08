# Dashboard Usage Tracking - Quick Reference Guide

## Quick Commands to Check Dashboard Usage

### Step 1: Login to IBM Cloud
```powershell
ibmcloud login --sso -r us-south
```
- Open the URL provided in your browser
- Authenticate with IBM Keypass
- Select account **2** (Daniela Danev's Account)

### Step 2: Target Resource Group
```powershell
ibmcloud target -g oidash
```

### Step 3: Select Code Engine Project
```powershell
ibmcloud ce project select --name python-appid-proj
```

---

## Check Who's Using the Dashboard Today

### See All Recent Logins
```powershell
ibmcloud ce application logs --name python-appid-app --tail 100 | Select-String "logged in"
```

### See Dashboard Access
```powershell
ibmcloud ce application logs --name python-appid-app --tail 100 | Select-String "Dashboard Access"
```

### Check for External (Non-IBM) Users
```powershell
ibmcloud ce application logs --name python-appid-app --tail 100 | Select-String "logged in" | Select-String -NotMatch "@ibm.com"
```

### Count Total Accesses
```powershell
ibmcloud ce application logs --name python-appid-app --tail 500 | Select-String "Dashboard Access" | Measure-Object | Select-Object -ExpandProperty Count
```

### Filter Out Internal System Calls
```powershell
ibmcloud ce application logs --name python-appid-app --tail 500 | Select-String "Dashboard Access" | Select-String -NotMatch "_dash-update-component"
```

---

## Real-Time Monitoring

### Watch Activity as it Happens
```powershell
ibmcloud ce application logs --name python-appid-app --follow
```
Press `Ctrl+C` to stop monitoring

---

## Export Logs for Analysis

### Save Today's Logs to File
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 > dashboard_logs_$(Get-Date -Format "yyyy-MM-dd").txt
```

### Analyze Saved Logs
```powershell
# View all logins
Select-String -Path "dashboard_logs_*.txt" -Pattern "logged in"

# View external users only
Select-String -Path "dashboard_logs_*.txt" -Pattern "logged in" | Select-String -NotMatch "@ibm.com"

# Count accesses
(Select-String -Path "dashboard_logs_*.txt" -Pattern "Dashboard Access").Count
```

---

## Common Usage Patterns

### Example: Check if Anyone Used Dashboard Today
```powershell
# Login
ibmcloud login --sso -r us-south
ibmcloud target -g oidash
ibmcloud ce project select --name python-appid-proj

# Check logins
ibmcloud ce application logs --name python-appid-app --tail 500 | Select-String "logged in"
```

**Sample Output:**
```
INFO:root: User Darshan.Patil@ibm.com logged in
INFO:root: User Brian.Christensen@ibm.com logged in
```

### Example: Check for External Client Usage
```powershell
ibmcloud ce application logs --name python-appid-app --tail 1000 | Select-String "logged in" | Select-String -NotMatch "@ibm.com"
```

**If external users accessed:**
```
INFO:root: User john.doe@capitalone.com logged in
INFO:root: User jane.smith@metlife.com logged in
```

**If no external users:**
```
(No output - only IBM users)
```

---

## Understanding the Logs

### Log Entry Types

1. **User Login**
   ```
   INFO:root: User Jason.Blakley@ibm.com logged in
   ```
   - Shows when someone authenticates
   - Email domain indicates IBM vs external user

2. **Dashboard Access**
   ```
   INFO:__main__:Dashboard Access | IP: 127.0.0.1 | Path: /dashboard/ | Method: GET
   ```
   - Shows page loads
   - IP is usually 127.0.0.1 (internal proxy)

3. **Graph Updates**
   ```
   INFO:__main__:Graph 1 Update | Client: CAPITAL ONE | Date Filter: 6 Months
   ```
   - Shows which clients are being analyzed
   - Shows filter selections

### What to Look For

- **IBM Users**: Email ends with `@ibm.com`
- **External Users**: Email ends with client domain (e.g., `@capitalone.com`)
- **Real Activity**: Look for "logged in" messages, not just "_dash-update-component"
- **Active Sessions**: Multiple graph updates from same user

---

## Troubleshooting

### "No user logged in to IBM cloud"
**Solution:** Run `ibmcloud login --sso -r us-south`

### "Option 'since' provided but not defined"
**Solution:** Use `--tail` instead of `--since`:
```powershell
ibmcloud ce application logs --name python-appid-app --tail 100
```

### No Logs Appearing
**Check application status:**
```powershell
ibmcloud ce application get --name python-appid-app
```

### Too Many Logs
**Increase tail number or export to file:**
```powershell
ibmcloud ce application logs --name python-appid-app --tail 5000 > logs.txt
```

---

## Key Information

- **Application Name**: python-appid-app
- **Project**: python-appid-proj
- **Resource Group**: oidash
- **Region**: us-south
- **Dashboard URL**: https://python-appid-app.wt1yl0ero9k.us-south.codeengine.appdomain.cloud/dashboard/

---

## Quick Copy-Paste Commands

**Complete check (all in one):**
```powershell
# Login and check usage
ibmcloud login --sso -r us-south
ibmcloud target -g oidash
ibmcloud ce project select --name python-appid-proj
ibmcloud ce application logs --name python-appid-app --tail 500 | Select-String "logged in"
```

**Export and analyze:**
```powershell
# Export logs
ibmcloud ce application logs --name python-appid-app --tail 1000 > dashboard_logs.txt

# View logins
Select-String -Path dashboard_logs.txt -Pattern "logged in"

# View external users
Select-String -Path dashboard_logs.txt -Pattern "logged in" | Select-String -NotMatch "@ibm.com"
```

---

**Last Updated**: May 12, 2026  
**For detailed information**, see: USAGE_LOGGING_GUIDE.md and EXTERNAL_USER_TRACKING.md