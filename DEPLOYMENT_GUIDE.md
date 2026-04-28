# Customer Ticketing Dashboard - Deployment Guide

## Overview
This guide documents the deployment process for the Customer Ticketing Dashboard to IBM Cloud Code Engine, including common issues and solutions.

## Prerequisites
- IBM Cloud CLI installed and configured
- IBM Cloud Code Engine plugin installed
- Access to IBM Cloud account (Daniela Danev's Account)
- GitHub repository: https://github.com/JasonBlakley/Dashboard_Deployment.git

## Project Configuration
- **Project Name**: python-appid-proj
- **Application Name**: python-appid-app
- **Build Name**: python-appid-bld
- **Container Registry Namespace**: python-appid-icr-ns
- **Region**: us-south
- **Resource Group**: oidash

## Deployment Steps

### 1. Login and Set Context
```bash
ibmcloud login
ibmcloud target -g oidash
ibmcloud ce project select --name python-appid-proj
```

### 2. Check Current Application Status
```bash
ibmcloud ce application list
ibmcloud ce application get --name python-appid-app
```

### 3. Handle Container Registry Storage Quota Issues

**IMPORTANT**: The free tier has a 512 MB storage limit. Before building, clean up old images.

#### Check Current Quota
```bash
ibmcloud cr quota
```

#### List and Clean Up Old Images
```bash
# List all images
ibmcloud cr image-list --restrict python-appid-icr-ns

# List images including untagged ones
ibmcloud cr image-digests --restrict python-appid-icr-ns

# Check trash (deleted images still count against quota for 30 days)
ibmcloud cr trash-list

# Delete untagged images
ibmcloud cr image-rm us.icr.io/python-appid-icr-ns/python-appid-img@sha256:<digest>
```

#### If Quota Still Exceeded
The trash contains deleted images that still count against quota. You have two options:

**Option A: Restore and Use Existing Image**
```bash
# Restore the latest image from trash
ibmcloud cr image-restore us.icr.io/python-appid-icr-ns/python-appid-img@sha256:<latest-digest>

# Update application to use restored image
ibmcloud ce application update --name python-appid-app --image us.icr.io/python-appid-icr-ns/python-appid-img:latest
```

**Option B: Wait for Trash Expiration**
Images in trash expire after 30 days. If you can wait, they will automatically be removed.

### 4. Build New Container Image (If Space Available)
```bash
# Submit a new build
ibmcloud ce buildrun submit --build python-appid-bld --name dashboard-deploy-$(date +%y%m%d-%H%M%S)

# Monitor build progress
ibmcloud ce buildrun get --name <buildrun-name>
```

### 5. Update Application
```bash
# Update application with new image
ibmcloud ce application update --name python-appid-app --image us.icr.io/python-appid-icr-ns/python-appid-img:latest
```

### 6. Monitor Deployment
```bash
# Check application status
ibmcloud ce application get --name python-appid-app

# View events
ibmcloud ce application events --name python-appid-app

# Follow logs
ibmcloud ce application logs --name python-appid-app --follow

# Check specific instance logs
ibmcloud ce application logs --instance <instance-name> --all-containers
```

## Common Issues and Solutions

### Issue 1: Storage Quota Exceeded
**Error**: "The storage quota limit of the IBM Container Registry has been exceeded."

**Solution**:
1. Check trash: `ibmcloud cr trash-list`
2. Delete old untagged images: `ibmcloud cr image-digests --restrict python-appid-icr-ns`
3. If still over quota, restore latest image from trash and use it
4. Consider upgrading plan if needed (requires approval)

### Issue 2: Application Takes Long to Start
**Symptom**: Readiness probes failing with "connection refused" or "context deadline exceeded"

**Explanation**: The dashboard loads large CSV files from Cloud Object Storage on startup. This is normal and can take 5-10 minutes.

**What to Look For**:
- User-container logs showing CSV files being loaded
- Messages like "DtypeWarning: Columns have mixed types"
- Eventually the application will start listening on port 8050

### Issue 3: Old Revision Still Running
**Symptom**: Traffic not switching to new revision

**Solution**: Wait for the new revision to pass all health checks. Code Engine will automatically:
1. Start new revision
2. Wait for it to become ready (3/3 containers running)
3. Switch 100% traffic to new revision
4. Terminate old revision

### Issue 4: Build Configuration Needs Update
```bash
# View current build configuration
ibmcloud ce build get --name python-appid-bld

# Update build source or image tag if needed
ibmcloud ce build update --name python-appid-bld \
  --image us.icr.io/python-appid-icr-ns/python-appid-img:<new-tag>
```

## Application Configuration

### Environment Variables
The application requires these environment variables (configured via secrets):
- `APPID_CLIENT_ID` - App ID client ID
- `APPID_CLIENT_SECRET` - App ID client secret
- `APPID_OAUTH_SERVER_URL` - App ID OAuth server URL
- `APPID_REDIRECT_URI` - Redirect URI for authentication
- `IBM_CLOUD_APIKEY` - IBM Cloud API key
- `SESSION_SECRET_KEY` - Flask session secret
- `APPID_COS_API_KEY` - Cloud Object Storage API key

### Resource Allocation
- CPU: 12 cores
- Memory: 48 GB
- Ephemeral Storage: 10 GB
- Port: 8050
- Min Scale: 1
- Max Scale: 10

## Data Files Loaded on Startup
The application loads these CSV files from Cloud Object Storage:
- All_2023_Data_PID_Info.csv
- Merged_data_2024.csv
- Monthly files for 2025: Jan25, Feb25, March25, April25, May25, June25, July25, August25, September25, October25, November25, December25

## Verification

### Check Deployment Success
```bash
# Application should show:
# - Status Summary: Application deployed successfully
# - Latest revision with 100% traffic
# - Running Instances: 1 (or more)
# - All conditions OK: ConfigurationsReady, Ready, RoutesReady

ibmcloud ce application get --name python-appid-app
```

### Access the Dashboard
URL: https://python-appid-app.wt1yl0ero9k.us-south.codeengine.appdomain.cloud

The application uses IBM App ID for authentication. Users must:
1. Be authenticated via configured identity provider
2. Have appropriate roles assigned in App ID

## Troubleshooting Commands

```bash
# View all build runs
ibmcloud ce build get --name python-appid-bld

# View application revisions
ibmcloud ce revision list --application python-appid-app

# View secrets
ibmcloud ce secret list

# View registry credentials
ibmcloud ce registry list

# Check container registry namespaces
ibmcloud cr namespace-list

# View quota details
ibmcloud cr quota
```

## Quick Deployment Checklist

- [ ] Login to IBM Cloud and select project
- [ ] Check current application status
- [ ] Verify container registry quota
- [ ] Clean up old images if needed
- [ ] Build new image OR restore from trash
- [ ] Update application
- [ ] Monitor deployment (5-10 minutes for startup)
- [ ] Verify new revision is running with 100% traffic
- [ ] Test application URL

## Notes
- The free tier Container Registry has a 512 MB limit
- Deleted images remain in trash for 30 days and count against quota
- Application startup takes 5-10 minutes due to data loading
- Always check logs if deployment seems stuck
- The application will show readiness probe failures during startup - this is normal

## Last Updated
2026-04-28