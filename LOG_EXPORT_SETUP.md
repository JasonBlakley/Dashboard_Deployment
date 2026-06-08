# Weekly Log Export Setup Guide

## Overview
This guide will help you set up automated weekly log exports for the dashboard. The script will run every Sunday at 11:59 PM and export all logs from the past week.

## Files Created
- `weekly-log-export.ps1` - The main export script
- `LOG_EXPORT_SETUP.md` - This setup guide (you're reading it)

## Step 1: Test the Script Manually

Before scheduling, let's test the script to make sure it works:

1. Open PowerShell as Administrator
2. Navigate to the script location:
   ```powershell
   cd "c:\Users\JasonBlakley\OneDrive - IBM\TicketingDashboard\Dashboard_Deployment"
   ```

3. Run the script:
   ```powershell
   .\weekly-log-export.ps1
   ```

4. Check the output:
   - Script should create `C:\DashboardLogs` directory
   - Should export logs and create 5 files:
     - `dashboard-logs-YYYY-MM-DD.txt` (full logs)
     - `logins-YYYY-MM-DD.txt` (login events)
     - `access-YYYY-MM-DD.txt` (dashboard access)
     - `graph-updates-YYYY-MM-DD.txt` (graph updates)
     - `weekly-summary-YYYY-MM-DD.txt` (summary report)

5. Review the summary file to see the statistics

## Step 2: Schedule the Script in Task Scheduler

### Option A: Using PowerShell (Recommended)

Run this PowerShell command as Administrator:

```powershell
# Create the scheduled task
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"c:\Users\JasonBlakley\OneDrive - IBM\TicketingDashboard\Dashboard_Deployment\weekly-log-export.ps1`""

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "11:59PM"

$principal = New-ScheduledTaskPrincipal -UserId "JasonBlakley" -LogonType Interactive -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "Dashboard Weekly Log Export" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Exports dashboard logs weekly for historical tracking"
```

### Option B: Using Task Scheduler GUI

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click "Create Basic Task" in the right panel
3. **Name:** Dashboard Weekly Log Export
4. **Description:** Exports dashboard logs weekly for historical tracking
5. Click "Next"

6. **Trigger:** Weekly
7. Click "Next"

8. **Start:** Today's date
9. **Start time:** 11:59 PM
10. **Recur every:** 1 week
11. **On:** Sunday
12. Click "Next"

13. **Action:** Start a program
14. Click "Next"

15. **Program/script:** `powershell.exe`
16. **Add arguments:** 
    ```
    -ExecutionPolicy Bypass -File "c:\Users\JasonBlakley\OneDrive - IBM\TicketingDashboard\Dashboard_Deployment\weekly-log-export.ps1"
    ```
17. Click "Next"

18. Check "Open the Properties dialog for this task when I click Finish"
19. Click "Finish"

20. In the Properties dialog:
    - Go to "General" tab
    - Check "Run with highest privileges"
    - Go to "Settings" tab
    - Check "Run task as soon as possible after a scheduled start is missed"
    - Uncheck "Stop the task if it runs longer than"
    - Click "OK"

## Step 3: Verify the Schedule

Check that the task is scheduled:

```powershell
Get-ScheduledTask -TaskName "Dashboard Weekly Log Export"
```

You should see the task listed with status "Ready".

## Step 4: Test the Scheduled Task

Don't wait until Sunday! Test it now:

```powershell
Start-ScheduledTask -TaskName "Dashboard Weekly Log Export"
```

Then check `C:\DashboardLogs` to verify files were created.

## What Happens Each Week

Every Sunday at 11:59 PM, the script will:

1. ✅ Export all logs from Code Engine (up to 50,000 lines)
2. ✅ Extract login events to separate file
3. ✅ Extract dashboard access events
4. ✅ Extract graph update events
5. ✅ Create a weekly summary with statistics:
   - Total logins
   - Unique users (IBM vs External)
   - Client access counts
6. ✅ Clean up logs older than 90 days
7. ✅ Display summary in console (if you're watching)

## Viewing Historical Logs

After the script runs for a few weeks, you can query historical data:

### Find all logins in the last 30 days:
```powershell
Get-ChildItem "C:\DashboardLogs" -Filter "logins-*.txt" | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-30) } | 
    Get-Content
```

### Count logins by user:
```powershell
Get-ChildItem "C:\DashboardLogs" -Filter "logins-*.txt" | 
    Get-Content | 
    Select-String "User (.*?) logged in" | 
    ForEach-Object { $_.Matches.Groups[1].Value } | 
    Group-Object | 
    Sort-Object Count -Descending | 
    Format-Table Name, Count -AutoSize
```

### Find external user logins:
```powershell
Get-ChildItem "C:\DashboardLogs" -Filter "logins-*.txt" | 
    Get-Content | 
    Select-String "logged in" | 
    Select-String -NotMatch "@ibm.com"
```

### View all weekly summaries:
```powershell
Get-ChildItem "C:\DashboardLogs" -Filter "weekly-summary-*.txt" | 
    Sort-Object Name -Descending | 
    ForEach-Object { 
        Write-Host "`n========================================" -ForegroundColor Cyan
        Get-Content $_.FullName 
    }
```

### Get monthly statistics:
```powershell
$month = "2026-04"  # Change to desired month
Get-ChildItem "C:\DashboardLogs" -Filter "weekly-summary-$month*.txt" | 
    Get-Content | 
    Select-String "Total Unique Users|IBM Users|External Users"
```

## Troubleshooting

### Script doesn't run on schedule
1. Check Task Scheduler History:
   - Open Task Scheduler
   - Find your task
   - Click "History" tab
   - Look for errors

2. Verify IBM Cloud CLI is logged in:
   ```powershell
   ibmcloud target
   ```
   If not logged in, the script will fail. You may need to run:
   ```powershell
   ibmcloud login --sso
   ```

3. Check execution policy:
   ```powershell
   Get-ExecutionPolicy
   ```
   Should be "RemoteSigned" or "Unrestricted"

### No login events found
- This is normal if no one logged in during the week
- Users stay logged in via session cookies
- Login events only occur during actual authentication

### Script runs but no files created
- Check if `C:\DashboardLogs` directory exists
- Verify you have write permissions to C:\
- Try running PowerShell as Administrator

## Manual Export Anytime

You don't have to wait for Sunday! Run the script manually anytime:

```powershell
cd "c:\Users\JasonBlakley\OneDrive - IBM\TicketingDashboard\Dashboard_Deployment"
.\weekly-log-export.ps1
```

## Modifying the Schedule

### Change to daily exports:
```powershell
$trigger = New-ScheduledTaskTrigger -Daily -At "11:59PM"
Set-ScheduledTask -TaskName "Dashboard Weekly Log Export" -Trigger $trigger
```

### Change to different day/time:
```powershell
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At "5:00PM"
Set-ScheduledTask -TaskName "Dashboard Weekly Log Export" -Trigger $trigger
```

### Disable the task:
```powershell
Disable-ScheduledTask -TaskName "Dashboard Weekly Log Export"
```

### Enable the task:
```powershell
Enable-ScheduledTask -TaskName "Dashboard Weekly Log Export"
```

### Remove the task:
```powershell
Unregister-ScheduledTask -TaskName "Dashboard Weekly Log Export" -Confirm:$false
```

## Storage Requirements

- Each weekly export: ~1-5 MB (depending on usage)
- 90 days of logs: ~13-65 MB
- Very minimal storage impact

## Next Steps

1. ✅ Test the script manually (Step 1)
2. ✅ Schedule the task (Step 2)
3. ✅ Verify it's scheduled (Step 3)
4. ✅ Test the scheduled task (Step 4)
5. ⏳ Wait for logs to accumulate
6. ⏳ After 30 days, you'll have 30 days of searchable history!

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the script output for error messages
3. Verify IBM Cloud CLI is working: `ibmcloud ce application get --name python-appid-app`
4. Check Task Scheduler history for execution errors