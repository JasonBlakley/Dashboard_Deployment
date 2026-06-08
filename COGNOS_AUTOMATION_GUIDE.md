# Cognos Report Automation Guide

## Overview

This guide explains how to automate the monthly export of the "Case Arrival Details" Cognos report that feeds the Ticketing Dashboard.

**Report Details:**
- **Name:** Case Arrival Details
- **Report ID:** iA52C0D19539F42F9909BF269CD1FF5A2
- **URL:** https://w3.ibm.com/epm/app-prod/bi/?perspective=classicviewer&id=iA52C0D19539F42F9909BF269CD1FF5A2
- **Frequency:** Monthly (1st of each month)
- **Format:** CSV

## Current Manual Process

1. Open report URL in browser
2. Authenticate with IBM w3id
3. Set parameters:
   - **Start Date:** First day of previous month (e.g., 2026-04-01)
   - **End Date:** Last day of previous month (e.g., 2026-04-30)
   - **Sources:** Check ALL boxes
     - ☑ Salesforce
     - ☑ Retain
     - ☑ ServiceNow
     - ☑ BAIW
     - ☑ Watson Health
     - ☑ MaaS360
     - ☑ Trusteer
4. Click "Run Report"
5. Export to CSV
6. Save as: `Case_Arrival_Details_YYYYMM.csv`
7. Upload to Cloud Object Storage or update dashboard

## Automation Options

### Option 1: Cognos Scheduled Reports (RECOMMENDED)

**Best for:** Reliable monthly automation with minimal setup

**Steps:**

1. **Open the report in Cognos:**
   ```
   https://w3.ibm.com/epm/app-prod/bi/?perspective=classicviewer&id=iA52C0D19539F42F9909BF269CD1FF5A2
   ```

2. **Click the Schedule button** (calendar icon in toolbar)

3. **Configure the schedule:**
   - **Name:** Case Arrival Details - Monthly Export
   - **Frequency:** Monthly
   - **Day:** 1st of the month
   - **Time:** 2:00 AM (or preferred time)
   - **Time Zone:** Your local timezone

4. **Set report options:**
   - **Format:** CSV
   - **Prompts:** 
     - Start Date: Use prompt macro `_first_of_month(-1)` (previous month start)
     - End Date: Use prompt macro `_last_of_month(-1)` (previous month end)
     - Sources: Select all (Salesforce, Retain, ServiceNow, BAIW, Watson Health, MaaS360, Trusteer)

5. **Configure delivery:**
   - **Method:** Email
   - **To:** Your IBM email address
   - **Subject:** Case Arrival Details - {RUN_DATE}
   - **Attachment:** Include report as CSV

6. **Save the schedule**

**Advantages:**
- ✅ No additional infrastructure needed
- ✅ Reliable (runs on Cognos servers)
- ✅ Email notification when complete
- ✅ Can be modified easily in Cognos UI

**Disadvantages:**
- ❌ Requires manual download from email
- ❌ Need to upload to Cloud Object Storage separately

---

### Option 2: Cognos REST API

**Best for:** Full automation with direct integration

**Requirements:**
- IBM w3id credentials or API key
- PowerShell script (provided: `cognos-report-export.ps1`)
- Windows Task Scheduler

**Steps:**

1. **Request API access:**
   - Contact Cognos administrator
   - Request API key or service account credentials
   - Get permissions for report access

2. **Configure authentication:**
   ```powershell
   # Store credentials securely
   $credential = Get-Credential
   $credential | Export-Clixml -Path "C:\Secure\cognos-creds.xml"
   ```

3. **Test the script:**
   ```powershell
   cd Dashboard_Deployment
   powershell -ExecutionPolicy Bypass -File .\cognos-report-export.ps1 -CurrentMonth
   ```

4. **Schedule with Task Scheduler:**
   - Open Task Scheduler
   - Create new task: "Cognos Monthly Export"
   - Trigger: Monthly, 1st day, 3:00 AM
   - Action: Run PowerShell script
   - Command: `powershell.exe -ExecutionPolicy Bypass -File "C:\Path\To\cognos-report-export.ps1"`

**Advantages:**
- ✅ Fully automated
- ✅ Can integrate with Cloud Object Storage upload
- ✅ No manual intervention needed
- ✅ Customizable error handling

**Disadvantages:**
- ❌ Requires API access setup
- ❌ More complex initial configuration
- ❌ Needs credential management

---

### Option 3: Browser Automation (Selenium)

**Best for:** When API access is not available but full automation is needed

**Requirements:**
- Selenium WebDriver for PowerShell
- Chrome or Edge browser
- WebDriver executable

**Setup:**

1. **Install Selenium module:**
   ```powershell
   Install-Module Selenium -Scope CurrentUser
   ```

2. **Download WebDriver:**
   - Chrome: https://chromedriver.chromium.org/
   - Edge: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

3. **Create automation script:**
   ```powershell
   # See cognos-selenium-automation.ps1 (to be created)
   ```

**Advantages:**
- ✅ Works without API access
- ✅ Can handle complex authentication flows
- ✅ Fully automated

**Disadvantages:**
- ❌ More fragile (UI changes break automation)
- ❌ Requires browser and WebDriver maintenance
- ❌ Slower than API approach

---

### Option 4: Manual with Helper Script

**Best for:** Occasional exports or testing

**Usage:**

Run the helper script to get pre-filled URLs:

```powershell
cd Dashboard_Deployment
powershell -ExecutionPolicy Bypass -File .\cognos-report-export.ps1
```

The script will:
1. Calculate the correct date range (previous month)
2. Generate a URL with parameters
3. Open a reminder file with instructions
4. Create the output directory structure

Then:
1. Copy the generated URL
2. Paste in browser
3. Report runs automatically
4. Save the downloaded CSV to the suggested location

**Advantages:**
- ✅ Simple and quick
- ✅ No setup required
- ✅ Good for testing

**Disadvantages:**
- ❌ Still requires manual steps
- ❌ Not truly automated

---

## Recommended Approach

### Phase 1: Immediate (This Month)
Use **Option 1: Cognos Scheduled Reports**
- Set up the schedule in Cognos (15 minutes)
- Receive email with CSV on 1st of each month
- Manually upload to Cloud Object Storage

### Phase 2: Short Term (Next Quarter)
Enhance with **Option 2: Cognos REST API**
- Request API access from Cognos admin
- Implement PowerShell automation
- Schedule with Task Scheduler
- Automate upload to Cloud Object Storage

### Phase 3: Long Term (Future)
Full integration:
- API pulls data directly
- Automatic upload to COS
- Dashboard auto-refreshes
- Email notification on completion

---

## File Locations

```
Dashboard_Deployment/
├── cognos-report-export.ps1          # Helper script
├── cognos_exports/                    # Output directory
│   ├── Case_Arrival_Details_202603.csv
│   ├── Case_Arrival_Details_202604.csv
│   └── MONTHLY_EXPORT_REMINDER.txt
└── COGNOS_AUTOMATION_GUIDE.md        # This file
```

---

## Troubleshooting

### Issue: Report parameters not working
**Solution:** Check parameter names in Cognos. They may be different from `p_startDate` and `p_endDate`. View the report's prompt definitions in Cognos.

### Issue: Authentication fails
**Solution:** 
- Verify IBM w3id credentials are correct
- Check if MFA is required (may need to use API key instead)
- Ensure you have permissions to run the report

### Issue: Scheduled report doesn't run
**Solution:**
- Check Cognos schedule status in "My Schedules"
- Verify email address is correct
- Check spam/junk folder
- Review Cognos logs for errors

### Issue: CSV format is incorrect
**Solution:**
- Verify export format is set to CSV (not Excel or PDF)
- Check delimiter settings (comma vs semicolon)
- Ensure all columns are included in export

---

## Monthly Checklist

On the 1st of each month:

- [ ] Check email for scheduled report (if using Option 1)
- [ ] Download CSV file
- [ ] Verify data looks correct (spot check)
- [ ] Rename file to: `Case_Arrival_Details_YYYYMM.csv`
- [ ] Upload to Cloud Object Storage bucket: `oidash-app`
- [ ] Update dashboard data source (if needed)
- [ ] Verify dashboard displays new data
- [ ] Archive previous month's file

---

## Support

**Cognos Issues:**
- Cognos Support Portal: https://w3.ibm.com/epm/support
- Email: cognos-support@ibm.com

**Dashboard Issues:**
- See: `DEPLOYMENT_GUIDE.md`
- Contact: Dashboard team

**Script Issues:**
- Review: `cognos-report-export.ps1`
- Check logs in: `cognos_exports/`

---

## Next Steps

1. **Choose your automation method** (Option 1 recommended to start)
2. **Set up the automation** following the steps above
3. **Test with current month** to verify it works
4. **Document any customizations** you make
5. **Set calendar reminder** for 2nd of month to verify export completed

---

## Additional Resources

- Cognos REST API Documentation: https://www.ibm.com/docs/en/cognos-analytics/latest?topic=api-rest
- IBM w3id Authentication: https://w3.ibm.com/tools/sso/
- PowerShell Scheduling: https://docs.microsoft.com/en-us/powershell/module/scheduledtasks/

---

*Last Updated: 2026-04-28*