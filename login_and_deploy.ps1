# IBM Cloud Login and Deployment Script for April 2026 Update
# Updated: May 1, 2026

Write-Host "=== IBM Cloud Dashboard Deployment ===" -ForegroundColor Cyan
Write-Host "Logging in to IBM Cloud..." -ForegroundColor Yellow

# Login with passcode - answer 'n' to browser prompt, provide passcode, select account 2
$passcode = "ZDqN1pqBR5"
Write-Output "n`n$passcode`n2" | ibmcloud login --sso -r us-south

if ($LASTEXITCODE -ne 0) {
    Write-Host "Login failed. Please check the passcode and try again." -ForegroundColor Red
    exit 1
}

Write-Host "`nLogin successful!" -ForegroundColor Green

# Target resource group
Write-Host "`nTargeting resource group 'oidash'..." -ForegroundColor Yellow
ibmcloud target -g oidash

# Select Code Engine project
Write-Host "`nSelecting Code Engine project 'python-appid-proj'..." -ForegroundColor Yellow
ibmcloud ce project select --name python-appid-proj

# Check current application status
Write-Host "`nChecking current application status..." -ForegroundColor Yellow
ibmcloud ce application get --name python-appid-app

# Submit new build
Write-Host "`nSubmitting new build..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyMMdd-HHmmss"
$buildname = "dashboard-deploy-$timestamp"
Write-Host "Build name: $buildname" -ForegroundColor Cyan

ibmcloud ce buildrun submit --build python-appid-bld --name $buildname

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build submission failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`nBuild submitted successfully!" -ForegroundColor Green
Write-Host "Build name: $buildname" -ForegroundColor Cyan
Write-Host "`nMonitoring build progress..." -ForegroundColor Yellow

# Monitor build (will check status every 10 seconds)
$maxAttempts = 60  # 10 minutes max
$attempt = 0
$buildComplete = $false

while (-not $buildComplete -and $attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 10
    $attempt++
    
    $buildStatus = ibmcloud ce buildrun get --name $buildname --output json | ConvertFrom-Json
    $status = $buildStatus.status.conditions[0].reason
    
    Write-Host "[$attempt/$maxAttempts] Build status: $status" -ForegroundColor Cyan
    
    if ($status -eq "Succeeded") {
        $buildComplete = $true
        Write-Host "`nBuild completed successfully!" -ForegroundColor Green
    }
    elseif ($status -eq "Failed") {
        Write-Host "`nBuild failed!" -ForegroundColor Red
        ibmcloud ce buildrun logs --name $buildname
        exit 1
    }
}

if (-not $buildComplete) {
    Write-Host "`nBuild timeout - please check status manually" -ForegroundColor Yellow
    Write-Host "Run: ibmcloud ce buildrun get --name $buildname" -ForegroundColor Cyan
    exit 1
}

# Update application with new image
Write-Host "`nUpdating application with new image..." -ForegroundColor Yellow
ibmcloud ce application update --name python-appid-app --image us.icr.io/python-appid-icr-ns/python-appid-img:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "Application update failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Deployment Complete! ===" -ForegroundColor Green
Write-Host "`nVerifying deployment..." -ForegroundColor Yellow
ibmcloud ce application get --name python-appid-app

Write-Host "`nApplication URL:" -ForegroundColor Cyan
ibmcloud ce application get --name python-appid-app --output json | ConvertFrom-Json | Select-Object -ExpandProperty status | Select-Object -ExpandProperty url

Write-Host "`nDeployment successful! The dashboard now includes April 2026 data." -ForegroundColor Green

# Made with Bob
