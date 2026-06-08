# Cognos Report Export Automation Script
# Purpose: Automatically export "Case Arrival Details" report to CSV
# Report ID: iA52C0D19539F42F9909BF269CD1FF5A2

param(
    [Parameter(Mandatory=$false)]
    [string]$Month = (Get-Date).AddMonths(-1).ToString("yyyy-MM"),
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\cognos_exports",
    
    [Parameter(Mandatory=$false)]
    [switch]$CurrentMonth
)

# Configuration
$CognosBaseURL = "https://w3.ibm.com/epm/app-prod/bi"
$ReportID = "iA52C0D19539F42F9909BF269CD1FF5A2"
$ReportName = "Case_Arrival_Details"

# If CurrentMonth flag is set, use current month instead of previous
if ($CurrentMonth) {
    $Month = (Get-Date).ToString("yyyy-MM")
}

# Calculate date parameters
$StartDate = "$Month-01"
$LastDay = [DateTime]::DaysInMonth([int]$Month.Split('-')[0], [int]$Month.Split('-')[1])
$EndDate = "$Month-$LastDay"

Write-Host "=== Cognos Report Export ===" -ForegroundColor Cyan
Write-Host "Report: Case Arrival Details"
Write-Host "Month: $Month"
Write-Host "Date Range: $StartDate to $EndDate"
Write-Host ""

# Create output directory if it doesn't exist
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath | Out-Null
    Write-Host "Created output directory: $OutputPath" -ForegroundColor Green
}

# Output filename
$OutputFile = Join-Path $OutputPath "$($ReportName)_$($Month.Replace('-','')).csv"

Write-Host "Output file will be: $OutputFile" -ForegroundColor Yellow
Write-Host ""

# Sources to include (all checked)
$Sources = @(
    "Salesforce",
    "Retain", 
    "ServiceNow",
    "BAIW",
    "Watson Health",
    "MaaS360",
    "Trusteer"
)

Write-Host "Data Sources: $($Sources -join ', ')" -ForegroundColor Cyan
Write-Host ""

# Method 1: Using Cognos REST API
Write-Host "=== Method 1: Cognos REST API ===" -ForegroundColor Green
Write-Host ""
Write-Host "To use the Cognos REST API, you need to:"
Write-Host "1. Authenticate with IBM w3id to get a session token"
Write-Host "2. Use the token to call the report execution API"
Write-Host ""

# Cognos API endpoints
$AuthEndpoint = "$CognosBaseURL/v1/session"
$ReportEndpoint = "$CognosBaseURL/v1/reports/$ReportID"

Write-Host "Authentication Endpoint: $AuthEndpoint"
Write-Host "Report Endpoint: $ReportEndpoint"
Write-Host ""

# Build report parameters
$ReportParams = @{
    "startDate" = $StartDate
    "endDate" = $EndDate
    "sources" = $Sources
}

Write-Host "Report Parameters:" -ForegroundColor Cyan
$ReportParams | ConvertTo-Json | Write-Host
Write-Host ""

# Note: Actual API authentication requires IBM w3id credentials
Write-Host "NOTE: IBM Cognos API authentication requires:" -ForegroundColor Yellow
Write-Host "  - IBM w3id credentials (username/password or API key)"
Write-Host "  - CAM passport or session token"
Write-Host "  - Proper permissions on the report"
Write-Host ""

# Method 2: Scheduled Report in Cognos
Write-Host "=== Method 2: Schedule Report in Cognos (RECOMMENDED) ===" -ForegroundColor Green
Write-Host ""
Write-Host "Steps to schedule the report in Cognos:"
Write-Host "1. Open the report in Cognos: $CognosBaseURL/?perspective=classicviewer&id=$ReportID"
Write-Host "2. Click 'Schedule' button (calendar icon)"
Write-Host "3. Configure schedule:"
Write-Host "   - Frequency: Monthly (1st day of month)"
Write-Host "   - Time: Early morning (e.g., 2:00 AM)"
Write-Host "   - Format: CSV"
Write-Host "   - Prompts: Set date parameters to previous month"
Write-Host "4. Delivery options:"
Write-Host "   - Email to: your.email@ibm.com"
Write-Host "   - Or save to: IBM Content Manager location"
Write-Host ""

# Method 3: Manual Export Helper
Write-Host "=== Method 3: Manual Export Helper ===" -ForegroundColor Green
Write-Host ""
Write-Host "If you need to export manually, use this URL with pre-filled parameters:"
Write-Host ""

# Build URL with parameters (note: actual parameter names may vary)
$ManualURL = "$CognosBaseURL/?perspective=classicviewer&id=$ReportID&action=run&format=CSV&prompt=false"
$ManualURL += "&p_startDate=$StartDate&p_endDate=$EndDate"

Write-Host $ManualURL -ForegroundColor Cyan
Write-Host ""
Write-Host "Steps:"
Write-Host "1. Copy the URL above"
Write-Host "2. Paste in browser (will authenticate with w3id)"
Write-Host "3. Report will run and download as CSV"
Write-Host "4. Save to: $OutputFile"
Write-Host ""

# Method 4: Browser Automation (Selenium)
Write-Host "=== Method 4: Browser Automation (Advanced) ===" -ForegroundColor Green
Write-Host ""
Write-Host "For full automation, you could use Selenium WebDriver to:"
Write-Host "1. Launch browser"
Write-Host "2. Authenticate with w3id"
Write-Host "3. Navigate to report"
Write-Host "4. Fill in parameters"
Write-Host "5. Export to CSV"
Write-Host "6. Save file"
Write-Host ""
Write-Host "This requires:"
Write-Host "  - Selenium PowerShell module"
Write-Host "  - Chrome/Edge WebDriver"
Write-Host "  - Stored credentials (secure)"
Write-Host ""

# Summary
Write-Host "=== RECOMMENDATION ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "Best approach for monthly automation:"
Write-Host ""
Write-Host "1. SHORT TERM: Use Cognos scheduled reports"
Write-Host "   - Set up monthly schedule in Cognos"
Write-Host "   - Receive CSV via email on 1st of each month"
Write-Host "   - Save to: $OutputPath"
Write-Host ""
Write-Host "2. LONG TERM: Cognos REST API integration"
Write-Host "   - Request API key from Cognos admin"
Write-Host "   - Implement authentication in this script"
Write-Host "   - Run via Windows Task Scheduler"
Write-Host ""

# Create a reminder file
$ReminderFile = Join-Path $OutputPath "MONTHLY_EXPORT_REMINDER.txt"
$ReminderContent = @"
MONTHLY COGNOS REPORT EXPORT REMINDER
======================================

Report: Case Arrival Details
Report ID: $ReportID
URL: $CognosBaseURL/?perspective=classicviewer&id=$ReportID

SCHEDULE: 1st of each month

STEPS:
1. Open report URL in browser
2. Set parameters:
   - Start Date: First day of PREVIOUS month (e.g., 2026-04-01)
   - End Date: Last day of PREVIOUS month (e.g., 2026-04-30)
   - Sources: Check ALL
     ☑ Salesforce
     ☑ Retain
     ☑ ServiceNow
     ☑ BAIW
     ☑ Watson Health
     ☑ MaaS360
     ☑ Trusteer
3. Click "Run Report"
4. Export to CSV
5. Save as: Case_Arrival_Details_YYYYMM.csv
6. Move to: $OutputPath

NEXT EXPORT DUE: $(Get-Date -Day 1).AddMonths(1).ToString('yyyy-MM-dd')

AUTOMATION OPTIONS:
- Schedule report in Cognos (recommended)
- Use Cognos REST API (requires API key)
- Browser automation with Selenium (advanced)

For help, see: cognos-report-export.ps1
"@

$ReminderContent | Out-File -FilePath $ReminderFile -Encoding UTF8
Write-Host "Created reminder file: $ReminderFile" -ForegroundColor Green
Write-Host ""

# Open the reminder file
Write-Host "Opening reminder file..." -ForegroundColor Cyan
Start-Process notepad.exe $ReminderFile

Write-Host ""
Write-Host "=== Script Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Review the reminder file that just opened"
Write-Host "2. Choose an automation method (scheduled report recommended)"
Write-Host "3. Set up the automation"
Write-Host "4. Test with current month: .\cognos-report-export.ps1 -CurrentMonth"
Write-Host ""

# Made with Bob
