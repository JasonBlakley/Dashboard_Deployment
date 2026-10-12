# Security Incident Report — Exposed IBM Cloud API Key
**Date:** 2026-10-12  
**Reported By:** CSIRT (via GitGuardian)  
**GitGuardian Incident ID:** #2468528  
**Severity:** High  
**Status:** ✅ Fully Resolved  

---

## 1. Incident Summary

GitGuardian detected a valid IBM Cloud API key hardcoded in plain text within the public GitHub repository `JasonBlakley/Dashboard_Deployment`. The key was used by the OI Ticketing Dashboard application to authenticate against IBM Cloud Object Storage (COS), where dashboard data files are stored. GitGuardian confirmed the key was still active at the time of the report.

---

## 2. Exposed Credential Details

| Field | Value |
|---|---|
| Key (now revoked) | `IXlwNFSuZ9dl7CUr1LSlYs3gkBpwI2-fNdMCUne2Pb4C` |
| Credential Name | `oidash_app_creds` |
| COS Instance | `cloud-object-storage-kz` |
| COS Instance CRN | `crn:v1:bluemix:public:cloud-object-storage:global:a/6003dba678e9a506528e0dc3dad11d75:b75750b4-68a2-4113-af62-16c1e6e10bca::` |
| COS Endpoint | `https://s3.us-east.cloud-object-storage.appdomain.cloud` |
| IBM Cloud Account | Daniela Danev's Account (`6003dba678e9a506528e0dc3dad11d75`) |
| Resource Group | `oidash` |

---

## 3. Scope of Exposure

The key was found hardcoded in **10 files** across the repository:

| File | Line |
|---|---|
| `Dashboard_Deployment/app.py` | 42 |
| `Dashboard_Deployment/app.bak.py` | 42 |
| `Dashboard_Deployment/app.py.backup_20260605_154102` | 41 |
| `Dashboard_Deployment/app.py.backup_20260429_093412` | 41 |
| `upstream_compare/app.py` | 40 |
| `Files/2026/May/upload_may_data_to_cos.py` | 6 |
| `Files/2026/Apr/backup_cos_to_local.py` | 14 |
| `Files/2026/Apr/list_cos_files.py` | 8 |
| `Files/2026/Apr/create_2025_consolidated.py` | 23 |
| `Files/2026/Apr/create_2025_consolidated_local.py` | 23 |

The key was also present across **112 Git commits** in the repository history, meaning it was publicly accessible for an extended period.

---

## 4. Remediation Actions Taken

### 4.1 Credential Revocation
- The exposed credential `oidash_app_creds` was deleted from the `cloud-object-storage-kz` IBM Cloud COS instance via the IBM Cloud console on 2026-10-12.
- A new credential was created in its place and stored securely in the Code Engine secret `python-appid-app-secret` under the key `APPID_COS_API_KEY`.

### 4.2 Code Fix
All 10 affected files were updated to remove the hardcoded key. The production application (`app.py`) was changed to read the credential from an environment variable at runtime:

```python
# Before (insecure)
COS_API_KEY_ID = "IXlwNFSuZ9dl7CUr1LSlYs3gkBpwI2-fNdMCUne2Pb4C"

# After (secure)
COS_API_KEY_ID = os.environ.get("APPID_COS_API_KEY")
if not COS_API_KEY_ID:
    raise RuntimeError("APPID_COS_API_KEY environment variable is not set")
```

The environment variable is injected at runtime by IBM Code Engine from the `python-appid-app-secret` generic secret, which is managed through the IBM Cloud console and never stored in source code.

### 4.3 Git History Scrub
The exposed key was purged from all 112 commits in the repository history using `git-filter-repo`. The rewritten history was force-pushed to GitHub on 2026-10-12, eliminating all historical traces of the key from the public repository.

**Remediation commit:** `7108a9b` — *"security: remove hardcoded COS API key, read from APPID_COS_API_KEY env var"*

### 4.4 Redeployment
The application was rebuilt from source and redeployed to IBM Code Engine. The dashboard was confirmed operational with the new credential on 2026-10-12.

---

## 5. Impact Assessment

### Confirmed
- The COS bucket `oidash-app` contains IBM product lifecycle and ticketing dashboard data (CSV files). No customer PII is stored in this bucket.
- The exposed key had **Writer** access to the COS instance, meaning an unauthorized party could theoretically have read, written, or deleted files in the bucket.

### Runtime Log Review
Code Engine application logs were exported on 2026-10-12 (`dashboard_logs_audit.txt`, saved locally) and reviewed. No anomalous access patterns, unexpected IP addresses, or unauthorized COS operations were identified in the available log window.

### IBM Cloud Activity Tracker
A full audit of COS API calls via IBM Cloud Activity Tracker is recommended to cover the full exposure window. Filter by the service ID associated with the now-deleted `oidash_app_creds` credential.

---

## 6. Preventive Measures

| Measure | Status |
|---|---|
| All credentials read from environment variables | ✅ Implemented |
| Secrets stored in Code Engine secret (`python-appid-app-secret`) | ✅ In place |
| Git history scrubbed of exposed key | ✅ Completed |
| `.gitignore` review recommended to prevent future credential commits | ⚠️ Recommended |
| IBM Cloud Activity Tracker review for full exposure window | ⚠️ Recommended |
| Regular credential rotation policy | ⚠️ Recommended |

---

## 7. Contact

**Application Owner:** Jason Blakley  
**IBM Cloud Account:** Daniela Danev's Account  
**Repository:** https://github.com/JasonBlakley/Dashboard_Deployment  
**Code Engine Project:** `python-appid-proj` (region: `us-south`, resource group: `oidash`)
