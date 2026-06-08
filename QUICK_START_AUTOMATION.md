# Quick Start Guide - Monthly Data Automation

## 🚀 Get Started in 5 Minutes

This guide will help you set up the monthly data automation quickly.

---

## Option 1: Semi-Automated (Recommended to Start)

**Best for:** Quick setup, runs on your PC

### Step 1: One-Time Setup (2 minutes)

1. **Open PowerShell in the Dashboard_Deployment folder:**
   ```powershell
   cd Dashboard_Deployment
   ```

2. **Install Python dependencies:**
   ```powershell
   pip install pandas boto3 ibm-cos-sdk
   ```

3. **Edit configuration (optional):**
   - Open `automation_config.json`
   - Update your email address in the `recipients` array
   - Save the file

### Step 2: Monthly Usage (3 minutes)

**On the 1st of each month:**

1. **Export Cognos Reports:**
   - Export EPM report → Save to `Files/YYYY/MMM/MMM_EPM_Tickets.csv`
   - Export Solve report → Save to `Files/YYYY/MMM/MMMM_YY_Solve.csv`

2. **Run the automation:**
   ```powershell
   cd Dashboard_Deployment
   powershell -ExecutionPolicy Bypass -File .\run_monthly_automation.ps1
   ```

3. **Done!** The script will:
   - ✅ Find your files automatically
   - ✅ Merge the data
   - ✅ Upload to Cloud Object Storage
   - ✅ Show you a success message

---

## Option 2: Fully Automated (Cloud Functions)

**Best for:** Hands-off automation using Daniela's IBM Cloud

### Step 1: One-Time Setup (10 minutes)

1. **Login to IBM Cloud:**
   ```bash
   ibmcloud login
   ```

2. **Deploy the function:**
   ```bash
   cd Dashboard_Deployment
   bash deploy_cloud_function.sh
   ```

3. **Follow the prompts:**
   - Select namespace (or use default)
   - Enter your IBM Cloud API key
   - Choose schedule (recommend: 2nd of month at 3 AM)

### Step 2: Monthly Usage (2 minutes)

**On the 1st of each month:**

1. **Export Cognos Reports** (same as before)

2. **Upload to trigger location:**
   - Option A: Upload to COS "incoming" folder
   - Option B: Email as attachment (if configured)
   - Option C: Upload to Box folder (if configured)

3. **Done!** The Cloud Function will:
   - ✅ Automatically detect new files
   - ✅ Merge the data
   - ✅ Upload to COS
   - ✅ Send you an email notification

---

## Troubleshooting

### "Python not found"
**Solution:** Install Python 3.7+ from https://www.python.org/downloads/

### "Files not found"
**Solution:** Check file names match these patterns:
- EPM: `MMM_EPM_Tickets.csv` (e.g., `May_EPM_Tickets.csv`)
- Solve: `MMMM_YY_Solve.csv` (e.g., `May_26_Solve.csv`)

### "COS upload failed"
**Solution:** Set environment variable:
```powershell
$env:IBM_CLOUD_APIKEY = "your-api-key-here"
```

### "Script won't run"
**Solution:** Allow PowerShell scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## What Gets Automated?

### ✅ Automated:
- Data merging (EPM + Solve)
- File upload to Cloud Object Storage
- Dashboard deployment (optional)
- Email notifications (optional)

### ❌ Still Manual:
- Exporting Cognos reports (cannot be automated without API access)
- Initial file placement

---

## Monthly Checklist

- [ ] 1st of month: Export EPM report from Cognos
- [ ] 1st of month: Export Solve report from Cognos
- [ ] 1st of month: Save files to correct location
- [ ] 2nd of month: Run automation script (or wait for Cloud Function)
- [ ] 2nd of month: Verify dashboard shows new data
- [ ] Archive previous month's files (optional)

---

## Time Savings

| Task | Before | After | Savings |
|------|--------|-------|---------|
| Export reports | 10 min | 10 min | 0 min |
| Merge data | 15 min | 0 min | 15 min |
| Upload to COS | 5 min | 0 min | 5 min |
| Deploy dashboard | 10 min | 0 min | 10 min |
| **Total** | **40 min** | **10 min** | **30 min** |

---

## Next Steps

1. ✅ Choose your option (1 or 2)
2. ✅ Complete the one-time setup
3. ✅ Test with current month's data
4. ✅ Set calendar reminder for next month
5. ✅ Upgrade to Option 2 when ready

---

## Support

**Need help?**
- See full documentation: `MONTHLY_DATA_AUTOMATION_AGENT.md`
- Check logs: `Dashboard_Deployment/logs/`
- Review Cognos guide: `COGNOS_AUTOMATION_GUIDE.md`

---

## Files Created

After setup, you'll have:
```
Dashboard_Deployment/
├── monthly_data_agent.py              # Core automation logic
├── run_monthly_automation.ps1         # PowerShell wrapper
├── automation_config.json             # Configuration
├── deploy_cloud_function.sh           # Cloud deployment script
├── MONTHLY_DATA_AUTOMATION_AGENT.md   # Full documentation
└── QUICK_START_AUTOMATION.md          # This file
```

---

**Ready to start?** Choose Option 1 above and follow the steps! 🎉

*Last Updated: 2026-05-06*