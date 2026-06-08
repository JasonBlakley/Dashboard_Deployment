	
service-key-cpzpj# IBM Cloud API Key Setup for Autonomous Deployments

**Date:** June 5, 2026  
**Purpose:** Enable Bob (AI Assistant) to perform autonomous deployments without interactive SSO login

---

## Step 1: Create IBM Cloud API Key

### Via IBM Cloud Console (Recommended)

1. **Log in to IBM Cloud Console:**
   - Go to: https://cloud.ibm.com
   - Log in with your IBM credentials

2. **Navigate to API Keys:**
   - Click your profile icon (top right)
   - Select **"Manage"** → **"Access (IAM)"**
   - In left sidebar, click **"API keys"**
   - Or go directly to: https://cloud.ibm.com/iam/apikeys

3. **Create New API Key:**
   - Click **"Create"** button
   - **Name:** `dashboard-deployment-key` (or your preferred name)
   - **Description:** `API key for autonomous dashboard deployments via Bob AI`
   - Click **"Create"**

4. **Download and Save the API Key:**
   - ⚠️ **CRITICAL:** The API key is shown only once!
   - Click **"Download"** to save as JSON file
   - Or click **"Copy"** to copy the key
   - Store securely - you cannot retrieve it later

### Via IBM Cloud CLI (Alternative)

```bash
# Login first
ibmcloud login --sso -r us-south

# Create API key
ibmcloud iam api-key-create dashboard-deployment-key -d "API key for autonomous dashboard deployments"

# The API key will be displayed - copy it immediately!
```

---

## Step 2: Store API Key Securely

### Option A: Environment Variable (Recommended for Local Development)

**Windows PowerShell:**
```powershell
# Set for current session
$env:IBM_CLOUD_API_KEY = "your-api-key-here"

# Set permanently (User level)
[System.Environment]::SetEnvironmentVariable('IBM_CLOUD_API_KEY', 'your-api-key-here', 'User')

# Verify
echo $env:IBM_CLOUD_API_KEY
```

**Windows Command Prompt:**
```cmd
# Set for current session
set IBM_CLOUD_API_KEY=your-api-key-here

# Set permanently
setx IBM_CLOUD_API_KEY "your-api-key-here"
```

### Option B: Secure Configuration File

Create a file: `Dashboard_Deployment/.env` (this file is gitignored)

```bash
IBM_CLOUD_API_KEY=your-api-key-here
```

**Add to .gitignore:**
```
.env
*.key
*_credentials.json
```

### Option C: Windows Credential Manager (Most Secure)

```powershell
# Store in Windows Credential Manager
cmdkey /generic:IBM_CLOUD_API_KEY /user:dashboard-deployment /pass:your-api-key-here

# Retrieve later
$cred = cmdkey /list:IBM_CLOUD_API_KEY
```

---

## Step 3: Update Deployment Script

Create new file: `Dashboard_Deployment/deploy_with_apikey.ps1`

```powershell
# IBM Cloud Deployment Script with API Key Authentication
# Updated: June 5, 2026

Write-Host "=== IBM Cloud Dashboard Deployment ===" -ForegroundColor Cyan

# Check for API key
if (-not $env:IBM_CLOUD_API_KEY) {
    Write-Host "ERROR: IBM_CLOUD_API_KEY environment variable not set!" -ForegroundColor Red
    Write-Host "Please set it using: `$env:IBM_CLOUD_API_KEY = 'your-api-key'" -ForegroundColor Yellow
    exit 1
}

Write-Host "Logging in to IBM Cloud with API key..." -ForegroundColor Yellow
ibmcloud login --apikey $env:IBM_CLOUD_API_KEY -r us-south -g oidash

if ($LASTEXITCODE -ne 0) {
    Write-Host "Login failed. Please check your API key." -ForegroundColor Red
    exit 1
}

Write-Host "`nLogin successful!" -ForegroundColor Green

# Select Code Engine project
Write-Host "`nSelecting Code Engine project..." -ForegroundColor Yellow
ibmcloud ce project select --name python-appid-proj

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
Write-Host "Monitoring build progress..." -ForegroundColor Yellow

# Monitor build
$maxAttempts = 60
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
    Write-Host "`nBuild timeout - check status manually" -ForegroundColor Yellow
    exit 1
}

# Update application
Write-Host "`nUpdating application..." -ForegroundColor Yellow
ibmcloud ce application update --name python-appid-app --image us.icr.io/python-appid-icr-ns/python-appid-img:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "Application update failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Deployment Complete! ===" -ForegroundColor Green
ibmcloud ce application get --name python-appid-app

Write-Host "`nApplication URL:" -ForegroundColor Cyan
Write-Host "https://python-appid-app.wt1yl0ero9k.us-south.codeengine.appdomain.cloud" -ForegroundColor Green
```

---

## Step 4: Test the Setup

```powershell
# Test login with API key
ibmcloud login --apikey $env:IBM_CLOUD_API_KEY -r us-south

# Verify access
ibmcloud target
ibmcloud ce project list
```

---

## Step 5: Enable Bob to Use API Key

Once the API key is set as an environment variable, Bob can use it for deployments:

```powershell
# Bob will run:
ibmcloud login --apikey $env:IBM_CLOUD_API_KEY -r us-south -g oidash
ibmcloud ce project select --name python-appid-proj
ibmcloud ce buildrun submit --build python-appid-bld --name dashboard-deploy-$(Get-Date -Format 'yyMMdd-HHmmss')
```

---

## Security Best Practices

1. **Never commit API keys to Git**
   - Add `.env`, `*.key`, `*_credentials.json` to `.gitignore`

2. **Rotate API keys regularly**
   - Create new key every 90 days
   - Delete old keys after rotation

3. **Use least privilege**
   - API key should only have permissions needed for Code Engine deployments

4. **Monitor API key usage**
   - Check IBM Cloud Activity Tracker for API key usage
   - Review in IAM console: https://cloud.ibm.com/iam/apikeys

5. **Revoke if compromised**
   - Immediately delete the API key from IBM Cloud Console
   - Create a new one

---

## Required Permissions for API Key

The API key needs these IAM roles:

- **Code Engine:** Editor or Administrator
- **Container Registry:** Reader (to pull images)
- **Resource Group (oidash):** Viewer

To verify/set permissions:
1. Go to: https://cloud.ibm.com/iam/apikeys
2. Click on your API key
3. Click **"Access policies"**
4. Ensure proper roles are assigned

---

## Troubleshooting

### "API key is invalid"
- Verify the API key is correct (no extra spaces)
- Check if the API key was deleted in IBM Cloud Console
- Create a new API key

### "Insufficient permissions"
- Check IAM roles for the API key
- Ensure access to resource group `oidash`
- Verify Code Engine permissions

### "Cannot find project"
- Ensure logged into correct region: `us-south`
- Verify resource group: `oidash`
- Check project name: `python-appid-proj`

---

## Next Steps

After setting up the API key:

1. Set the environment variable: `$env:IBM_CLOUD_API_KEY = "your-key"`
2. Test the connection: `ibmcloud login --apikey $env:IBM_CLOUD_API_KEY -r us-south`
3. Run deployment: `.\Dashboard_Deployment\deploy_with_apikey.ps1`
4. Bob can now perform autonomous deployments!

---

**Created by:** Bob (AI Assistant)  
**Last Updated:** June 5, 2026