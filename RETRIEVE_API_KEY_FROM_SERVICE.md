# Retrieve API Key from Service Binding

**Service:** python-appid  
**Service Key:** service-key-cpzpj  
**Purpose:** Extract API key for autonomous deployments

---

## Quick Steps to Get API Key

### Option 1: Via IBM Cloud Console (Easiest)

1. **Go to IBM Cloud Console:**
   - https://cloud.ibm.com

2. **Navigate to App ID Service:**
   - Click **"Resource list"** (left sidebar)
   - Under **"Security"**, find **"python-appid"**
   - Click on it

3. **View Service Credentials:**
   - Click **"Service credentials"** tab
   - Find **"service-key-cpzpj"**
   - Click **"View credentials"** or the dropdown arrow
   - Look for `"apikey":` field
   - Copy the API key value

### Option 2: Via IBM Cloud CLI

```powershell
# 1. Login first (you'll need to do this interactively)
ibmcloud login --sso -r us-south

# 2. Target the resource group
ibmcloud target -g oidash

# 3. Get the service key details
ibmcloud resource service-key service-key-cpzpj --output json

# 4. Look for the "apikey" field in the JSON output
```

### Option 3: From Code Engine Secret

The API key is already stored in Code Engine as a secret. To view it:

```powershell
# 1. Login
ibmcloud login --sso -r us-south

# 2. Select Code Engine project
ibmcloud ce project select --name python-appid-proj

# 3. Get secret details
ibmcloud ce secret get --name python-appid-app-secret --output json

# 4. Look for IBM_CLOUD_APIKEY in the data section
```

---

## What to Do with the API Key

Once you have the API key:

### Set as Environment Variable (Recommended)

**PowerShell:**
```powershell
# Set for current session
$env:IBM_CLOUD_API_KEY = "paste-your-api-key-here"

# Verify it's set
echo $env:IBM_CLOUD_API_KEY

# Set permanently (optional)
[System.Environment]::SetEnvironmentVariable('IBM_CLOUD_API_KEY', 'paste-your-api-key-here', 'User')
```

### Test the API Key

```powershell
# Test login with the API key
ibmcloud login --apikey $env:IBM_CLOUD_API_KEY -r us-south -g oidash

# If successful, you'll see:
# "Targeted resource group oidash"
# "API endpoint: https://cloud.ibm.com"
```

---

## Enable Bob for Autonomous Deployments

After setting the environment variable, Bob can use it:

```powershell
# Bob will run these commands automatically:
ibmcloud login --apikey $env:IBM_CLOUD_API_KEY -r us-south -g oidash
ibmcloud ce project select --name python-appid-proj
ibmcloud ce buildrun submit --build python-appid-bld --name dashboard-deploy-$(Get-Date -Format 'yyMMdd-HHmmss')
# ... monitor build and update application
```

---

## Security Notes

- ✅ This API key already exists and is used by your application
- ✅ It has the correct permissions for Code Engine
- ✅ No need to create a new key
- ⚠️ Keep the API key secure - don't commit to Git
- ⚠️ Only share with Bob via environment variable

---

## Next Steps

1. Retrieve the API key using one of the methods above
2. Set it as environment variable: `$env:IBM_CLOUD_API_KEY = "your-key"`
3. Let Bob know it's ready
4. Bob will proceed with the May 2026 deployment automatically

---

**Created:** June 5, 2026  
**For:** Autonomous dashboard deployments