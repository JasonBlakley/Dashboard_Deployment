# Restart Dashboard Application to Load May 2026 Data
# This forces the application to reload all data from Cloud Object Storage

Write-Host "=== Restarting Dashboard Application ===" -ForegroundColor Cyan
Write-Host "This will reload all data including May 2026..." -ForegroundColor Yellow

# Login with passcode
$passcode = "vdmt5Qr2BW"
Write-Host "`nLogging in to IBM Cloud..." -ForegroundColor Yellow
Write-Output "n`n$passcode`n2" | ibmcloud login --sso -r us-south

if ($LASTEXITCODE -ne 0) {
    Write-Host "Login failed. Please check the passcode and try again." -ForegroundColor Red
    exit 1
}

Write-Host "Login successful!" -ForegroundColor Green

# Target resource group
Write-Host "`nTargeting resource group 'oidash'..." -ForegroundColor Yellow
ibmcloud target -g oidash

# Select Code Engine project
Write-Host "`nSelecting Code Engine project 'python-appid-proj'..." -ForegroundColor Yellow
ibmcloud ce project select --name python-appid-proj

# Get current application status
Write-Host "`nCurrent application status:" -ForegroundColor Yellow
ibmcloud ce application get --name python-appid-app

# Restart the application by updating it (this triggers a restart)
Write-Host "`nRestarting application to reload data..." -ForegroundColor Yellow
ibmcloud ce application update --name python-appid-app --env-from-secret python-appid-secret --env-from-configmap python-appid-cm

if ($LASTEXITCODE -ne 0) {
    Write-Host "Application restart failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Application Restart Initiated ===" -ForegroundColor Green
Write-Host "`nWaiting for application to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check new status
Write-Host "`nNew application status:" -ForegroundColor Yellow
ibmcloud ce application get --name python-appid-app

Write-Host "`nApplication URL:" -ForegroundColor Cyan
ibmcloud ce application get --name python-appid-app --output json | ConvertFrom-Json | Select-Object -ExpandProperty status | Select-Object -ExpandProperty url

Write-Host "`n=== Restart Complete ===" -ForegroundColor Green
Write-Host "The dashboard should now include May 2026 data." -ForegroundColor Green
Write-Host "Please verify by checking the date range in the dashboard." -ForegroundColor Yellow

# Made with Bob