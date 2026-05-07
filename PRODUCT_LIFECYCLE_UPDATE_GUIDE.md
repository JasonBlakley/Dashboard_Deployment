# Product Lifecycle Data Update Guide

## Overview

The dashboard determines product support status using **three JSON dictionary files** that are downloaded from Cloud Object Storage:

- **`Red_dict_May_25_final.json`** - Products at or past End of Support (EOS)
- **`Orange_dict_May_25_final.json`** - Products ending support within 12 months
- **`Green_dict_May_25_final.json`** - Products currently in support

## Current Issue

You mentioned that **version 11.2.4 is showing as "In Support" for MetLife, but it's actually out of support**. This means the lifecycle dictionaries are **outdated** (last updated May 2025).

## How It Works

### 1. Files Downloaded from COS (app.py lines 313-324)

```python
red = get_item('oidash-app','Red_dict_May_25_final.json')
orange = get_item('oidash-app','Orange_dict_May_25_final.json')
green = get_item('oidash-app','Green_dict_May_25_final.json')
```

### 2. Color Calculation Function (app.py line 528+)

The `calc_color()` function checks each product/version against these dictionaries:
- If found in **red** → "End of Support" (Red)
- If found in **orange** → "End of Support Within 12 Months" (Orange)
- If found in **green** → "In Support" (Green)
- If not found → "N/A Version" (Blue)

### 3. Lifecycle CSV File

Also uses: `ibm_product_lifecycle_list_May_25.csv` (line 359)

---

## How to Update Product Lifecycle Data

### Option 1: Quick Fix - Update Specific Product

If you just need to fix one product (like the 11.2.4 issue):

1. **Download the current dictionaries from COS:**
   ```powershell
   # You'll need to use IBM Cloud CLI or COS UI
   ibmcloud cos object-get --bucket oidash-app --key Red_dict_May_25_final.json red.json
   ibmcloud cos object-get --bucket oidash-app --key Green_dict_May_25_final.json green.json
   ```

2. **Edit the JSON files:**
   - Open `red.json` and `green.json`
   - Find the product entry for version 11.2.4
   - Move it from `green.json` to `red.json`

3. **Upload back to COS:**
   ```powershell
   ibmcloud cos object-put --bucket oidash-app --key Red_dict_May_25_final.json --body red.json
   ibmcloud cos object-put --bucket oidash-app --key Green_dict_May_25_final.json --body green.json
   ```

4. **Restart the dashboard** (it will download the updated files)

---

### Option 2: Complete Refresh - Get Latest IBM Lifecycle Data

For a comprehensive update with all current IBM product lifecycle information:

#### Step 1: Get Latest IBM Product Lifecycle Data

**Source:** IBM Product Lifecycle website or internal database

You need to obtain:
- Product names
- Version numbers
- End of Support dates
- Current status

#### Step 2: Create Updated Dictionaries

Create a Python script to generate the three JSON dictionaries:

```python
import pandas as pd
import json
from datetime import datetime, timedelta

# Load IBM product lifecycle data
lifecycle_df = pd.read_csv('ibm_product_lifecycle_list_CURRENT.csv')

# Initialize dictionaries
red_dict = {}    # EOS reached
orange_dict = {} # EOS within 12 months
green_dict = {}  # In support

# Current date
today = datetime.now()
twelve_months = today + timedelta(days=365)

# Process each product
for _, row in lifecycle_df.iterrows():
    product = row['IBM Product']
    version = row['Version']
    eos_date = pd.to_datetime(row['End of Support Date'])
    
    if pd.isna(eos_date):
        continue
    
    # Determine status
    if eos_date < today:
        # Past EOS - RED
        if product not in red_dict:
            red_dict[product] = []
        red_dict[product].append(version)
    elif eos_date < twelve_months:
        # EOS within 12 months - ORANGE
        if product not in orange_dict:
            orange_dict[product] = []
        orange_dict[product].append(version)
    else:
        # In support - GREEN
        if product not in green_dict:
            green_dict[product] = []
        green_dict[product].append(version)

# Save to JSON files
with open('Red_dict_May_26_final.json', 'w') as f:
    json.dump(red_dict, f, indent=2)

with open('Orange_dict_May_26_final.json', 'w') as f:
    json.dump(orange_dict, f, indent=2)

with open('Green_dict_May_26_final.json', 'w') as f:
    json.dump(green_dict, f, indent=2)

print("✓ Lifecycle dictionaries created")
```

#### Step 3: Upload to COS

```powershell
# Upload new dictionaries
ibmcloud cos object-put --bucket oidash-app --key Red_dict_May_26_final.json --body Red_dict_May_26_final.json
ibmcloud cos object-put --bucket oidash-app --key Orange_dict_May_26_final.json --body Orange_dict_May_26_final.json
ibmcloud cos object-put --bucket oidash-app --key Green_dict_May_26_final.json --body Green_dict_May_26_final.json
ibmcloud cos object-put --bucket oidash-app --key ibm_product_lifecycle_list_May_26.csv --body ibm_product_lifecycle_list_May_26.csv
```

#### Step 4: Update app.py

Change the file names in app.py (lines 313, 317, 321, 359):

```python
# OLD:
red = get_item('oidash-app','Red_dict_May_25_final.json')
orange = get_item('oidash-app','Orange_dict_May_25_final.json')
green = get_item('oidash-app','Green_dict_May_25_final.json')
product_lifecycle_data = pd.read_csv('ibm_product_lifecycle_list_May_25.csv')

# NEW:
red = get_item('oidash-app','Red_dict_May_26_final.json')
orange = get_item('oidash-app','Orange_dict_May_26_final.json')
green = get_item('oidash-app','Green_dict_May_26_final.json')
product_lifecycle_data = pd.read_csv('ibm_product_lifecycle_list_May_26.csv')
```

#### Step 5: Deploy Updated Dashboard

```bash
cd Dashboard_Deployment
git add app.py
git commit -m "Update product lifecycle data to May 2026"
git push

# Deploy to Code Engine
ibmcloud ce application update --name python-appid-app \
  --build-source https://github.com/JasonBlakley/Dashboard_Deployment.git \
  --build-commit main
```

---

## Recommended Update Schedule

### Quarterly Updates (Recommended)
- **When:** Every 3 months (e.g., Feb, May, Aug, Nov)
- **Why:** IBM product lifecycle dates don't change frequently
- **Effort:** ~30 minutes

### Monthly Updates (If needed)
- **When:** 1st of each month (along with data refresh)
- **Why:** Ensures most current status
- **Effort:** ~15 minutes (if automated)

---

## Automation Option

### Add to Monthly Data Agent

You can extend the monthly automation agent to also update lifecycle data:

```python
# In monthly_data_agent.py, add:

def update_lifecycle_data(self):
    """Update product lifecycle dictionaries"""
    self.logger.info("Updating product lifecycle data...")
    
    # Download latest IBM lifecycle data
    # Process into red/orange/green dictionaries
    # Upload to COS
    
    self.logger.info("✓ Lifecycle data updated")
```

---

## Troubleshooting

### Issue: Product showing wrong status

**Diagnosis:**
1. Check which dictionary file it's in
2. Verify the EOS date in IBM's lifecycle database
3. Check if dictionaries are outdated

**Solution:**
- Update the dictionaries using Option 1 or 2 above

### Issue: Product not found (shows as Blue/N/A)

**Diagnosis:**
- Product/version not in any dictionary
- Product name mismatch

**Solution:**
- Add the product to the appropriate dictionary
- Check for name variations (e.g., "IBM Db2" vs "Db2")

### Issue: All products showing outdated status

**Diagnosis:**
- Dictionary files are old (May 2025 in your case)

**Solution:**
- Perform a complete refresh (Option 2)

---

## Data Sources

### Where to Get IBM Product Lifecycle Data

1. **IBM Product Lifecycle Portal:**
   - Internal IBM tool
   - Most authoritative source

2. **IBM Support Portal:**
   - https://www.ibm.com/support/pages/lifecycle
   - Public lifecycle information

3. **Cognos Report:**
   - May have a lifecycle report available
   - Check with your Cognos admin

4. **Manual Tracking:**
   - Maintain a spreadsheet
   - Update based on IBM announcements

---

## File Format Examples

### Red Dictionary (EOS Reached)
```json
{
  "IBM Db2": ["10.5", "11.1"],
  "IBM WebSphere": ["8.5.5"],
  "IBM MQ": ["9.0"]
}
```

### Orange Dictionary (EOS Within 12 Months)
```json
{
  "IBM Db2": ["11.5.4"],
  "IBM WebSphere": ["9.0.5"]
}
```

### Green Dictionary (In Support)
```json
{
  "IBM Db2": ["11.5.8", "11.5.9"],
  "IBM WebSphere": ["9.0.5.12"],
  "IBM MQ": ["9.3"]
}
```

### Lifecycle CSV
```csv
IBM Product,Version,PID,End of Support Date,Status
IBM Db2,11.5.9,5737-J31,2027-04-30,In Support
IBM Db2,11.2.4,5737-J31,2024-09-30,End of Support
IBM WebSphere,9.0.5.12,5724-J08,2026-12-31,In Support
```

---

## Next Steps

1. **Immediate:** Check the current lifecycle files in COS to see what's there
2. **Short-term:** Update the specific product (11.2.4) causing issues
3. **Long-term:** Set up quarterly lifecycle data refresh process
4. **Optional:** Automate lifecycle updates in the monthly agent

---

## Support

**For lifecycle data questions:**
- IBM Product Lifecycle team
- Your IBM account representative

**For dashboard updates:**
- See: `DEPLOYMENT_GUIDE.md`
- This guide

**For automation:**
- See: `MONTHLY_DATA_AUTOMATION_AGENT.md`

---

*Created: 2026-05-06*
*Issue: MetLife 11.2.4 showing as "In Support" when it's actually EOS*
*Root Cause: Lifecycle dictionaries last updated May 2025*