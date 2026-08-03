# Dashboard Deploy Mode - User Guide

## Overview

The **Dashboard Deploy** mode is a custom mode designed specifically for your monthly Ticketing Dashboard deployment workflow. It automates the entire process from data merging to Code Engine deployment.

## When to Use This Mode

Use the Dashboard Deploy mode when you have:
- ✅ New monthly EPM tickets CSV file
- ✅ New monthly Solve tickets CSV file
- ✅ Files placed in the appropriate `Files/2026/[Month]/` directory
- ✅ Ready to deploy the new month's data to production

## How to Activate

1. **Open the mode selector** in Bob
2. **Select "🚀 Dashboard Deploy"** from the list
3. **Tell Bob you're ready to deploy**, for example:
   - "I have the June 2026 files ready to deploy"
   - "Deploy the new monthly data for June"
   - "Let's process and deploy June 2026 tickets"

## What the Mode Does Automatically

The Dashboard Deploy mode follows an 8-step workflow:

### Step 1: Validate Input Files ✓
- Confirms month/year
- Checks both CSV files exist
- Verifies files aren't empty or corrupted

### Step 2: Merge Data 🔄
- Runs `merge_[month]_data.py`
- Creates `[Month]_2026_merged.csv`
- Validates row counts
- Scans for data quality issues

### Step 3: Upload to Cloud Object Storage ☁️
- Runs `upload_[month]_data_to_cos.py`
- Uploads to IBM COS bucket 'oidash-app'
- Verifies upload success

### Step 4: Update Dashboard Code 💻
- Updates `app.py` if needed for new month
- Ensures data loading includes new month

### Step 5: Commit to GitHub 📝
- Stages all changes
- Creates descriptive commit message
- Pushes to main branch
- Verifies push succeeded

### Step 6: Deploy to Code Engine 🚀
- Triggers Code Engine deployment
- Monitors deployment logs
- Waits for completion

### Step 7: Verify Deployment ✅
- Accesses dashboard URL
- Checks new month in filters
- Verifies data loads correctly
- Tests Chart 2
- Checks for errors

### Step 8: Document Deployment 📄
- Creates deployment summary
- Notes any issues
- Records timestamp
- Updates tracking files

## Example Usage

```
You: "I have the June 2026 files ready. The EPM file has 15,234 tickets 
     and the Solve file has 8,456 tickets. They're in Files/2026/Jun/"

Bob: [Switches to Dashboard Deploy mode]
     "Starting June 2026 deployment workflow...
     
     Step 1: Validating input files...
     ✓ Found Jun_EPM_tickets.csv (15,234 rows)
     ✓ Found Jun_26_Solve.csv (8,456 rows)
     
     Step 2: Merging data files...
     [Runs merge script]
     ✓ Created June_2026_merged.csv (23,690 rows)
     
     [Continues through all 8 steps...]
     
     Deployment Complete! ✅
     - New data uploaded to COS
     - Code pushed to GitHub (commit abc123)
     - Dashboard deployed to Code Engine
     - Verification passed
     
     Deployment Summary: [link to summary document]"
```

## What You Need to Provide

When starting a deployment, provide:
1. **Month and Year**: "June 2026"
2. **File Location**: Where you placed the files (usually Files/2026/Jun/)
3. **Confirmation**: That both files are ready

Optional but helpful:
- Expected row counts
- Any known data quality issues
- Special instructions for this month

## Safety Features

The mode includes several safety checks:

### Automatic Validation
- File existence and size checks
- Data quality scanning
- Row count verification
- Column name validation

### Failure Handling
- Stops at first error
- Provides clear error messages
- Suggests rollback if needed
- Documents failures

### Rollback Support
If something goes wrong:
1. Mode stops immediately
2. Previous month's data remains accessible
3. You receive rollback instructions
4. Failure is documented for review

## Common Issues the Mode Handles

The mode automatically detects and handles:
- ❌ File encoding problems (UTF-8 vs other)
- ❌ Column name mismatches
- ❌ Missing or extra columns
- ❌ Invalid version strings (like we just fixed!)
- ❌ COS authentication failures
- ❌ Git merge conflicts
- ❌ Code Engine timeouts
- ❌ Memory issues with large files

## Monthly Workflow

Your simplified monthly process:

### Before (Manual Process):
1. Download EPM and Solve files
2. Place in correct folder
3. Run merge script manually
4. Check for errors
5. Run upload script manually
6. Update app.py if needed
7. Commit to Git manually
8. Deploy to Code Engine manually
9. Verify deployment manually
10. Document everything manually

### After (With Dashboard Deploy Mode):
1. Download EPM and Solve files
2. Place in correct folder
3. Tell Bob: "Deploy June 2026 data"
4. ☕ Wait while Bob does steps 3-10 automatically
5. Review deployment summary

## Tips for Best Results

### Preparation
- ✅ Download both files before starting
- ✅ Check file names match expected pattern
- ✅ Verify files aren't corrupted
- ✅ Have your IBM Cloud credentials ready

### During Deployment
- ✅ Stay available for questions
- ✅ Monitor progress messages
- ✅ Don't interrupt the process
- ✅ Note any warnings or issues

### After Deployment
- ✅ Review the deployment summary
- ✅ Test the dashboard yourself
- ✅ Check a few key clients
- ✅ Verify Chart 2 shows new month

## Troubleshooting

### Mode Not Available?
- Restart VS Code to load the new mode
- Check that `.bob/custom_modes.yaml` exists
- Verify you're in the correct workspace

### Deployment Fails?
- Check the error message carefully
- Review the step where it failed
- Don't manually continue - let Bob handle rollback
- Document the issue for future reference

### Need to Rollback?
- Bob will provide specific rollback instructions
- Previous month's data remains in COS
- Git history allows reverting commits
- Code Engine can redeploy previous version

## Advanced Features

### Data Quality Checks
The mode automatically:
- Scans for invalid version strings
- Checks for missing required fields
- Validates date formats
- Identifies duplicate records
- Reports data quality metrics

### Deployment Reports
Each deployment generates:
- Summary document with all steps
- Data quality report
- Error log (if any issues)
- Verification checklist
- Timestamp and commit hash

### Integration with Existing Tools
The mode uses your existing:
- Python merge scripts
- COS upload scripts
- Git repository
- Code Engine configuration
- IBM Cloud credentials

## Getting Help

If you need assistance:
1. **During Deployment**: Bob will guide you through issues
2. **After Deployment**: Review the deployment summary document
3. **For Mode Issues**: Check this guide or ask Bob in any mode
4. **For Dashboard Issues**: Use regular Code or Ask modes

## Future Enhancements

Potential improvements for the mode:
- Automated testing before deployment
- Slack/email notifications on completion
- Rollback automation
- Performance metrics tracking
- Automated lifecycle file updates
- Integration with Cognos for direct file fetch

## Summary

The Dashboard Deploy mode transforms your monthly deployment from a 10-step manual process into a simple conversation with Bob. It ensures consistency, reduces errors, and documents everything automatically.

**Next time you have monthly data ready, just say:**
> "Bob, I have the [Month] 2026 files ready to deploy"

And let the automation handle the rest! 🚀

---

**Created**: June 12, 2026  
**Mode Slug**: `dashboard-deploy`  
**Mode Icon**: 🚀  
**Version**: 1.0