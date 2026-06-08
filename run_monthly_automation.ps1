# Monthly Data Automation - PowerShell Wrapper
# This script provides an easy-to-use interface for running the monthly data automation

param(
    [string]$EPMFile = "",
    [string]$SolveFile = "",
    [string]$ConfigFile = "automation_config.json",
    [switch]$AutoDetect = $true,
    [switch]$Help
)

# Display help
if ($Help) {
    Write-Host @"
Monthly Data Automation Script
==============================

Usage:
    .\run_monthly_automation.ps1 [options]

Options:
    -EPMFile <path>      Path to EPM tickets CSV file
    -SolveFile <path>    Path to Solve data CSV file
    -ConfigFile <path>   Path to configuration file (default: automation_config.json)
    -AutoDetect          Automatically detect files (default: enabled)
    -Help                Show this help message

Examples:
    # Auto-detect files for previous month
    .\run_monthly_automation.ps1

    # Specify files manually
    .\run_monthly_automation.ps1 -EPMFile "Files/2026/May/May_EPM_Tickets.csv" -SolveFile "Files/2026/May/May_26_Solve.csv"

"@
    exit 0
}

# Banner
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                    MONTHLY DATA AUTOMATION AGENT                               " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found. Please install Python 3.7 or higher." -ForegroundColor Red
    exit 1
}

# Check if required Python packages are installed
Write-Host ""
Write-Host "[2/6] Checking Python dependencies..." -ForegroundColor Yellow
$requiredPackages = @("pandas", "boto3", "botocore")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    $installed = python -c "import $package" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingPackages += $package
        Write-Host "  ✗ Missing: $package" -ForegroundColor Red
    } else {
        Write-Host "  ✓ Found: $package" -ForegroundColor Green
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host ""
    Write-Host "Missing packages detected. Install them with:" -ForegroundColor Yellow
    Write-Host "  pip install $($missingPackages -join ' ')" -ForegroundColor White
    
    $response = Read-Host "Would you like to install them now? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "Installing packages..." -ForegroundColor Yellow
        pip install $($missingPackages -join ' ')
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ✗ Installation failed" -ForegroundColor Red
            exit 1
        }
        Write-Host "  ✓ Packages installed successfully" -ForegroundColor Green
    } else {
        Write-Host "Cannot proceed without required packages." -ForegroundColor Red
        exit 1
    }
}

# Check for configuration file
Write-Host ""
Write-Host "[3/6] Checking configuration..." -ForegroundColor Yellow
if (Test-Path $ConfigFile) {
    Write-Host "  ✓ Configuration file found: $ConfigFile" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Configuration file not found: $ConfigFile" -ForegroundColor Yellow
    Write-Host "  Creating default configuration..." -ForegroundColor Yellow
    
    $defaultConfig = @{
        cos = @{
            bucket = "oidash-app"
            incoming_folder = "incoming"
            archive_folder = "archive"
        }
        email = @{
            recipients = @()
            sender = "dashboard-automation@ibm.com"
            subject_template = "Dashboard Data Updated - {month} {year}"
        }
        files = @{
            epm_pattern = "{month}_EPM_Tickets.csv"
            solve_pattern = "{month}_{year}_Solve.csv"
            output_pattern = "{month}_{year}_merged.csv"
        }
        deployment = @{
            auto_deploy = $false
            code_engine_app = "python-appid-app"
            code_engine_project = "python-appid-proj"
        }
    }
    
    $defaultConfig | ConvertTo-Json -Depth 10 | Out-File $ConfigFile -Encoding UTF8
    Write-Host "  ✓ Default configuration created" -ForegroundColor Green
}

# Check for input files
Write-Host ""
Write-Host "[4/6] Locating input files..." -ForegroundColor Yellow

if ($AutoDetect -and [string]::IsNullOrEmpty($EPMFile) -and [string]::IsNullOrEmpty($SolveFile)) {
    # Calculate previous month
    $lastMonth = (Get-Date).AddMonths(-1)
    $monthFull = $lastMonth.ToString("MMMM")
    $monthAbbr = $lastMonth.ToString("MMM")
    $year = $lastMonth.ToString("yyyy")
    $yearShort = $lastMonth.ToString("yy")
    
    Write-Host "  Searching for $monthFull $year data..." -ForegroundColor White
    
    # Search for files
    $basePath = "Files\$year\$monthAbbr"
    
    if (Test-Path $basePath) {
        # Look for EPM file
        $epmPatterns = @(
            "$basePath\${monthAbbr}_EPM_Tickets.csv",
            "$basePath\${monthAbbr}_EPM_tickets.csv",
            "$basePath\${monthFull}_EPM_Tickets.csv"
        )
        
        foreach ($pattern in $epmPatterns) {
            if (Test-Path $pattern) {
                $EPMFile = $pattern
                Write-Host "  ✓ Found EPM file: $EPMFile" -ForegroundColor Green
                break
            }
        }
        
        # Look for Solve file
        $solvePatterns = @(
            "$basePath\${monthFull}_${yearShort}_Solve.csv",
            "$basePath\${monthAbbr}_${yearShort}_Solve.csv",
            "$basePath\${monthFull}_${year}_Solve.csv"
        )
        
        foreach ($pattern in $solvePatterns) {
            if (Test-Path $pattern) {
                $SolveFile = $pattern
                Write-Host "  ✓ Found Solve file: $SolveFile" -ForegroundColor Green
                break
            }
        }
    } else {
        Write-Host "  ⚠ Directory not found: $basePath" -ForegroundColor Yellow
    }
}

# Validate files exist
if ([string]::IsNullOrEmpty($EPMFile) -or -not (Test-Path $EPMFile)) {
    Write-Host ""
    Write-Host "  ✗ EPM file not found or not specified" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure you have exported the EPM report from Cognos and saved it to:" -ForegroundColor Yellow
    Write-Host "  Files\$year\$monthAbbr\${monthAbbr}_EPM_Tickets.csv" -ForegroundColor White
    Write-Host ""
    Write-Host "Or specify the file path manually:" -ForegroundColor Yellow
    Write-Host "  .\run_monthly_automation.ps1 -EPMFile <path>" -ForegroundColor White
    Write-Host ""
    exit 1
}

if ([string]::IsNullOrEmpty($SolveFile) -or -not (Test-Path $SolveFile)) {
    Write-Host ""
    Write-Host "  ✗ Solve file not found or not specified" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure you have exported the Solve report from Cognos and saved it to:" -ForegroundColor Yellow
    Write-Host "  Files\$year\$monthAbbr\${monthFull}_${yearShort}_Solve.csv" -ForegroundColor White
    Write-Host ""
    Write-Host "Or specify the file path manually:" -ForegroundColor Yellow
    Write-Host "  .\run_monthly_automation.ps1 -SolveFile <path>" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Check environment variables
Write-Host ""
Write-Host "[5/6] Checking environment variables..." -ForegroundColor Yellow
$envVars = @("IBM_CLOUD_APIKEY", "APPID_COS_API_KEY")
$foundEnvVar = $false

foreach ($var in $envVars) {
    if ([Environment]::GetEnvironmentVariable($var)) {
        Write-Host "  ✓ Found: $var" -ForegroundColor Green
        $foundEnvVar = $true
        break
    }
}

if (-not $foundEnvVar) {
    Write-Host "  ⚠ No COS API key found in environment variables" -ForegroundColor Yellow
    Write-Host "  Upload to Cloud Object Storage will be skipped" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  To enable COS upload, set one of these environment variables:" -ForegroundColor White
    Write-Host "    - IBM_CLOUD_APIKEY" -ForegroundColor White
    Write-Host "    - APPID_COS_API_KEY" -ForegroundColor White
}

# Run the automation
Write-Host ""
Write-Host "[6/6] Running automation agent..." -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$pythonArgs = @(
    "monthly_data_agent.py",
    "--epm-file", $EPMFile,
    "--solve-file", $SolveFile,
    "--config", $ConfigFile
)

python @pythonArgs

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "✓ AUTOMATION COMPLETED SUCCESSFULLY" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Verify the merged file was created" -ForegroundColor White
    Write-Host "  2. Check if file was uploaded to Cloud Object Storage" -ForegroundColor White
    Write-Host "  3. Verify dashboard displays the new data" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✗ AUTOMATION FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the log file in the 'logs' directory for details." -ForegroundColor Yellow
    Write-Host ""
}

exit $exitCode

# Made with Bob