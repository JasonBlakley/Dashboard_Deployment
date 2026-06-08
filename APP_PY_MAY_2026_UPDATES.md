# app.py Updates for May 2026 Deployment

**Date:** June 4, 2026  
**Status:** ✅ COMPLETE - Ready for Deployment

---

## Changes Made to app.py

### 1. Lifecycle File Update (Lines 152-156)
**Changed FROM:**
```python
lifecycle_data_cloud = get_item('oidash-app','ibm_product_lifecycle_list_May_25.csv')
lifecycle_data = lifecycle_data_cloud['Body'].read()
with open('ibm_product_lifecycle_list_May_25.csv','wb') as file:
    file.write(lifecycle_data)
```

**Changed TO:**
```python
lifecycle_data_cloud = get_item('oidash-app','ibm_product_lifecycle_list_May_26_FIXED.csv')
lifecycle_data = lifecycle_data_cloud['Body'].read()
with open('ibm_product_lifecycle_list_May_26_FIXED.csv','wb') as file:
    file.write(lifecycle_data)
```

---

### 2. May 2026 Data Download Added (Lines 247-250)
**Added:**
```python
may26_merged = get_item('oidash-app','May_2026_merged.csv')
may26_merged_new = may26_merged['Body'].read()
with open('May_2026_merged.csv','wb') as file:
    file.write(may26_merged_new)
```

---

### 3. May 2026 Data Loading Added (Lines 286-289)
**Added:**
```python
may_26_merged = pd.read_csv('May_2026_merged.csv', low_memory=False)
may_26_merged.rename(columns= {'Global Buying Group Name_x' : 'Global Buying Group Name', 'Product_x' : 'Product' }, inplace= True)
may_26_merged['Date'] = pd.to_datetime(may_26_merged['Month'])
```

**Updated record count print statement:**
```python
print(f"✓ Loaded {len(january_26_merged) + len(february_26_merged) + len(march_26_merged) + len(april_26_merged) + len(may_26_merged):,} records from 2026")
```

---

### 4. May 2026 Data Concatenation (Lines 293-301)
**Changed FROM:**
```python
all_data = pd.concat([
    all_data_24,
    all_data_25,
    january_26_merged,
    february_26_merged,
    march_26_merged,
    april_26_merged
], ignore_index=True)
```

**Changed TO:**
```python
all_data = pd.concat([
    all_data_24,
    all_data_25,
    january_26_merged,
    february_26_merged,
    march_26_merged,
    april_26_merged,
    may_26_merged
], ignore_index=True)
```

---

### 5. Lifecycle Dictionary Updates (Lines 322-332)
**Changed FROM:**
```python
red = get_item('oidash-app','Red_dict_May_25_final.json')
orange = get_item('oidash-app','Orange_dict_May_25_final.json')
green = get_item('oidash-app','Green_dict_May_25_final.json')
```

**Changed TO:**
```python
red = get_item('oidash-app','Red_dict_May_26_final.json')
orange = get_item('oidash-app','Orange_dict_May_26_final.json')
green = get_item('oidash-app','Green_dict_May_26_final.json')
```

---

### 6. Lifecycle CSV Reference Update (Line 368)
**Changed FROM:**
```python
product_lifecycle_data = pd.read_csv('ibm_product_lifecycle_list_May_25.csv')
```

**Changed TO:**
```python
product_lifecycle_data = pd.read_csv('ibm_product_lifecycle_list_May_26_FIXED.csv')
```

---

## Files Required in Cloud Storage (oidash-app bucket)

Ensure these files are uploaded to the `oidash-app` bucket before deployment:

### New/Updated Files:
1. ✅ `May_2026_merged.csv` (184.7 MB, 180,981 records)
2. ✅ `ibm_product_lifecycle_list_May_26_FIXED.csv`
3. ✅ `Red_dict_May_26_final.json`
4. ✅ `Orange_dict_May_26_final.json`
5. ✅ `Green_dict_May_26_final.json`

### Existing Files (should remain):
- `Merged_data_2024.csv`
- `Merged_data_2025.csv`
- `January_26_merged.csv`
- `February_2026_merged.csv`
- `March_2026_merged.csv`
- `April_2026_merged.csv`
- `All_2023_Data_PID_Info.csv`

---

## Expected Data Load

After deployment, the dashboard will load:
- **2024 Data:** Full year merged file
- **2025 Data:** Full year merged file
- **2026 Data:** January through May (5 months)
- **Total Expected Records:** ~500,000+ records
- **Date Range:** 2024-01-01 through 2026-05-31

---

## Deployment Verification Steps

After deployment, verify:

1. ✅ Dashboard loads without errors
2. ✅ Date range shows through May 2026
3. ✅ May 2026 data appears in filters and graphs
4. ✅ Product lifecycle colors (Red/Orange/Green) display correctly
5. ✅ Total record count is approximately 500K+
6. ✅ Performance is acceptable (3-5 minute initial load)
7. ✅ All filters work correctly with May data

---

## Notes

- Type checking warnings in the IDE are pre-existing and do not affect runtime functionality
- The app uses a health check server on port 8051 for container readiness probes
- Data loading takes 3-5 minutes on first startup
- All changes are backward compatible with existing functionality

---

## Rollback Instructions

If issues occur, revert these changes:
1. Change lifecycle file back to `ibm_product_lifecycle_list_May_25.csv`
2. Change dictionaries back to `*_May_25_final.json`
3. Remove May 2026 data loading sections
4. Remove `may_26_merged` from concatenation

---

**Status:** ✅ All updates complete and ready for deployment