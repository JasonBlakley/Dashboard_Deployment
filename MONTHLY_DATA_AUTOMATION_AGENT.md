# Monthly Data Loading Automation Agent

## Overview

This document describes an automated agent solution for loading dashboard data monthly without requiring IBM Orchestrate. The solution uses IBM Cloud Functions (serverless) or Watson Studio scheduled jobs that can run in Daniela's environment.

## Current Manual Process

### Step 1: Export Cognos Reports (MANUAL - Cannot be fully automated)
1. **EPM Tickets Report**
   - Export from Cognos
   - Save as: `MMM_EPM_Tickets.csv`
   
2. **Solve Data Report**
   - Export from Cognos
   - Save as: `MMMM_YY_Solve.csv`
   - **Required:** Exclude `Concept Rank = 0` rows from the export
   - **Required:** Verify concept coverage looks normal before publishing merged data

### Step 2: Merge Data (CAN BE AUTOMATED)
- Combine EPM and Solve data
- Apply transformations
- Create: `MMMM_YYYY_merged.csv`

### Step 3: Upload to COS (CAN BE AUTOMATED)
- Upload merged file to IBM Cloud Object Storage

### Step 4: Deploy Dashboard (CAN BE AUTOMATED)
- Update app.py if needed
- Trigger Code Engine deployment

## Automation Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MONTHLY AUTOMATION FLOW                   │
└─────────────────────────────────────────────────────────────┘

MANUAL STEPS (You or Daniela):
┌──────────────────────┐
│ 1. Export Cognos     │
│    - EPM Report      │──┐
│    - Solve Report    │  │
└──────────────────────┘  │
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. Upload to Trigger Location                                │
│    - Box folder / Shared drive / Email attachment            │
│    - Or: Direct upload to COS "incoming" folder              │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
AUTOMATED STEPS (Agent):
┌──────────────────────────────────────────────────────────────┐
│ 3. IBM Cloud Function / Watson Studio Job (Scheduled)        │
│    ┌────────────────────────────────────────────────────┐   │
│    │ a. Detect new files in trigger location           │   │
│    │ b. Download EPM and Solve CSVs                     │   │
│    │ c. Run merge_monthly_data.py                       │   │
│    │ d. Upload merged file to COS                       │   │
│    │ e. Optionally: Trigger dashboard deployment       │   │
│    │ f. Send completion email notification             │   │
│    └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Dashboard Auto-Updates (Next Access)                      │
│    - Code Engine loads new data from COS                     │
│    - Users see updated dashboard                             │
└──────────────────────────────────────────────────────────────┘
```

## Solution Options

### Option A: IBM Cloud Functions (Serverless) - RECOMMENDED

**Best for:** Fully automated, no infrastructure management

**Setup:**
1. Create IBM Cloud Function action
2. Schedule with Cloud Functions trigger (cron)
3. Runs monthly on 2nd day of month at 3 AM

**Advantages:**
- ✅ No servers to manage
- ✅ Pay only when running
- ✅ Built-in scheduling
- ✅ Can use Daniela's IBM Cloud account
- ✅ Automatic scaling

**Disadvantages:**
- ❌ 10-minute execution limit (should be sufficient)
- ❌ Requires IBM Cloud Functions access

---

### Option B: Watson Studio Scheduled Job

**Best for:** If you already use Watson Studio

**Setup:**
1. Create Watson Studio project
2. Upload automation notebook
3. Schedule as job (monthly)

**Advantages:**
- ✅ Familiar Jupyter notebook interface
- ✅ Easy to test and debug
- ✅ Can use Daniela's Watson Studio
- ✅ Good for data processing

**Disadvantages:**
- ❌ Requires Watson Studio access
- ❌ More manual setup

---

### Option C: Code Engine Scheduled Job

**Best for:** Consistent with current deployment

**Setup:**
1. Create Code Engine job (not application)
2. Schedule with cron expression
3. Runs in same environment as dashboard

**Advantages:**
- ✅ Same platform as dashboard
- ✅ Consistent environment
- ✅ Built-in scheduling
- ✅ Can reuse existing credentials

**Disadvantages:**
- ❌ Slightly more complex than Functions
- ❌ Need to manage container image

---

### Option D: Hybrid - Semi-Automated Helper

**Best for:** Quick start, minimal setup

**Setup:**
1. Run PowerShell script locally
2. Script does all automation except Cognos export
3. Can be scheduled on your PC with Task Scheduler

**Advantages:**
- ✅ No cloud setup needed
- ✅ Quick to implement
- ✅ Easy to debug
- ✅ Works immediately

**Disadvantages:**
- ❌ Requires your PC to be on
- ❌ Not truly serverless
- ❌ Manual trigger needed

---

## Recommended Implementation: Option A + D Hybrid

### Phase 1: Immediate (This Week)
Use **Option D** - Semi-automated helper script
- You export Cognos reports manually
- Script automates merge + upload + deployment
- Takes 5 minutes instead of 30 minutes

### Phase 2: Next Month
Upgrade to **Option A** - IBM Cloud Functions
- Set up serverless function in Daniela's account
- You still export Cognos, but upload to trigger location
- Everything else is automatic

### Phase 3: Future (Optional)
Add Cognos API integration
- Fully automated end-to-end
- Zero manual steps

---

## Files Included

### 1. `monthly_data_agent.py`
Core automation logic:
- Merges EPM and Solve data
- Uploads to Cloud Object Storage
- Triggers dashboard deployment
- Sends email notifications

### 2. `run_monthly_automation.ps1`
PowerShell wrapper for local execution:
- Prompts for file locations
- Validates data
- Runs Python agent
- Provides progress updates

### 3. `cloud_function_handler.py`
IBM Cloud Functions wrapper:
- Handles serverless execution
- Monitors trigger location
- Executes automation
- Returns status

### 4. `deploy_automation_agent.sh`
Deployment script:
- Creates Cloud Function
- Sets up trigger
- Configures secrets
- Tests execution

### 5. `automation_config.json`
Configuration file:
- COS bucket names
- Email recipients
- File naming patterns
- Schedule settings

---

## Setup Instructions

### For Option D (Semi-Automated Helper)

1. **Install Python dependencies:**
   ```powershell
   cd Dashboard_Deployment
   pip install -r requirements.txt
   ```

2. **Configure settings:**
   Edit `automation_config.json` with your details

3. **Run the automation:**
   ```powershell
   # After exporting Cognos reports to Files/2026/May/
   powershell -ExecutionPolicy Bypass -File .\run_monthly_automation.ps1
   ```

4. **Schedule (optional):**
   - Open Task Scheduler
   - Create task: "Dashboard Monthly Update"
   - Trigger: Monthly, 2nd day, 9:00 AM
   - Action: Run `run_monthly_automation.ps1`
   - Note: You'll still need to export Cognos reports first

---

### For Option A (IBM Cloud Functions)

1. **Prerequisites:**
   - IBM Cloud account (use Daniela's)
   - IBM Cloud CLI installed
   - Cloud Functions plugin

2. **Login to IBM Cloud:**
   ```bash
   ibmcloud login
   ibmcloud target -g <resource-group>
   ```

3. **Deploy the function:**
   ```bash
   cd Dashboard_Deployment
   bash deploy_automation_agent.sh
   ```

4. **Configure trigger location:**
   - Option 1: COS bucket "incoming" folder
   - Option 2: Box folder (requires Box integration)
   - Option 3: Email attachment (requires email integration)

5. **Test the function:**
   ```bash
   ibmcloud fn action invoke monthly-data-agent --result
   ```

6. **Set up schedule:**
   ```bash
   # Runs on 2nd of each month at 3 AM
   ibmcloud fn trigger create monthly-trigger \
     --feed /whisk.system/alarms/alarm \
     --param cron "0 3 2 * *" \
     --param trigger_payload "{\"month\":\"auto\"}"
   
   ibmcloud fn rule create monthly-rule monthly-trigger monthly-data-agent
   ```

---

## Usage Workflow

### Monthly Process (Semi-Automated)

**On 1st of Month:**
1. Export EPM report from Cognos → Save to `Files/YYYY/MMM/MMM_EPM_Tickets.csv`
2. Export Solve report from Cognos → Save to `Files/YYYY/MMM/MMMM_YY_Solve.csv`

**On 2nd of Month (or when ready):**
3. Run automation script:
   ```powershell
   cd Dashboard_Deployment
   powershell -ExecutionPolicy Bypass -File .\run_monthly_automation.ps1
   ```

4. Script will:
   - ✅ Validate both files exist
   - ✅ Validate Solve concept quality and detect `Concept Rank = 0` rows
   - ✅ Merge the data
   - ✅ Upload to Cloud Object Storage
   - ✅ Optionally trigger dashboard deployment
   - ✅ Send you email confirmation

5. Verify dashboard shows new data

**Total time: ~5 minutes** (down from 30+ minutes)

---

### Monthly Process (Fully Automated with Cloud Functions)

**On 1st of Month:**
1. Export EPM report from Cognos
2. Export Solve report from Cognos
3. Upload both files to trigger location (COS "incoming" folder or Box)

**Automatic (2nd of Month at 3 AM):**
4. Cloud Function wakes up
5. Detects new files
6. Merges data
7. Uploads to COS
8. Triggers deployment
9. Sends email notification

**Total manual time: ~2 minutes** (just upload files)

---

## Configuration

### automation_config.json

```json
{
  "cos": {
    "bucket": "oidash-app",
    "incoming_folder": "incoming",
    "archive_folder": "archive"
  },
  "email": {
    "recipients": ["your.email@ibm.com"],
    "sender": "dashboard-automation@ibm.com",
    "subject_template": "Dashboard Data Updated - {month} {year}"
  },
  "files": {
    "epm_pattern": "{month}_EPM_Tickets.csv",
    "solve_pattern": "{month}_{year}_Solve.csv",
    "output_pattern": "{month}_{year}_merged.csv"
  },
  "deployment": {
    "auto_deploy": false,
    "code_engine_app": "python-appid-app",
    "code_engine_project": "python-appid-proj"
  },
  "schedule": {
    "day_of_month": 2,
    "hour": 3,
    "timezone": "America/New_York"
  }
}
```

---

## Monitoring and Alerts

### Email Notifications

You'll receive emails for:
- ✅ Successful data merge
- ✅ Successful COS upload
- ✅ Successful deployment
- ❌ Missing files
- ❌ Merge errors
- ❌ Upload failures

### Logs

**Local execution:**
- `Dashboard_Deployment/logs/automation_YYYYMMDD.log`

**Cloud Functions:**
- View in IBM Cloud console
- Or: `ibmcloud fn activation logs <activation-id>`

### Dashboard

Check dashboard shows:
- New month's data
- Correct record counts
- Updated "Last Updated" timestamp

---

## Troubleshooting

### Issue: Files not found
**Solution:**
- Check file names match pattern in config
- Verify files are in correct directory
- Check file permissions

### Issue: Merge fails
**Solution:**
- Verify CSV format is correct
- Check for encoding issues (UTF-16 vs UTF-8)
- Review error log for specific column issues
- If the error mentions concept quality or `Concept Rank = 0`, re-export the Solve report with `Concept Rank = 0` excluded
- Compare concept coverage with prior months using `concept_coverage_audit.py`

### Issue: COS upload fails
**Solution:**
- Verify COS credentials are set
- Check bucket name is correct
- Ensure you have write permissions

### Issue: Deployment doesn't trigger
**Solution:**
- Check `auto_deploy` setting in config
- Verify Code Engine credentials
- Manually trigger if needed

### Issue: Cloud Function times out
**Solution:**
- Check file sizes (very large files may need optimization)
- Increase timeout in function settings
- Consider splitting into multiple functions

---

## Cost Estimate

### Option D (Local Script)
- **Cost:** $0/month
- **Time:** 5 minutes/month manual

### Option A (Cloud Functions)
- **Cost:** ~$0.50/month
  - 1 execution/month
  - ~2 minutes runtime
  - Minimal memory usage
- **Time:** 2 minutes/month manual

### Option B (Watson Studio)
- **Cost:** Included in Watson Studio plan
- **Time:** 2 minutes/month manual

---

## Security Considerations

1. **Credentials:**
   - Store in IBM Cloud Secrets Manager
   - Never commit to Git
   - Rotate regularly

2. **Data:**
   - Files encrypted in transit (HTTPS)
   - Files encrypted at rest (COS)
   - Access logs enabled

3. **Access:**
   - Use service IDs, not personal credentials
   - Principle of least privilege
   - Regular access reviews

---

## Data Quality Guardrails

To prevent accidental publication of low-concept data:

1. **Solve export requirement**
   - Exclude `Concept Rank = 0` rows every month
2. **Automated validation**
   - `monthly_data_agent.py` now checks concept coverage before merge
   - It also detects Solve rows where `Concept Rank = 0`
3. **Threshold configuration**
   - Controlled in `automation_config.json` under `quality_checks`
4. **Historical audit**
   - Run `python concept_coverage_audit.py` to compare month-by-month concept coverage
   - Investigate any sudden drop versus normal monthly coverage

## Next Steps

1. **Choose your option** (recommend starting with Option D)
2. **Review the automation scripts** (next files to be created)
3. **Test with current month's data**
4. **Schedule for next month**
5. **Monitor first automated run**
6. **Upgrade to cloud-based solution** when ready

---

## Support

**For automation issues:**
- Check logs in `Dashboard_Deployment/logs/`
- Review this guide
- Contact: Dashboard team

**For Cognos export issues:**
- See: `COGNOS_AUTOMATION_GUIDE.md`
- Contact: Cognos support

**For IBM Cloud issues:**
- IBM Cloud documentation
- Contact: Daniela (for her environment)

---

*Created: 2026-05-06*
*Last Updated: 2026-05-06*