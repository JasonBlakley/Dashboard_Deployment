# Product Matching Fix - June 9, 2026

## Problem Summary

The dashboard was experiencing product matching issues where products were showing as "N/A Version" (blue bubbles) even when they had valid lifecycle data. The root cause was **missing the lowercase conversion** of the mapped product name before dictionary lookups.

## Root Cause Identified

**Issue**: The `calc_color()` function was missing the `prod_string_lower` variable definition after applying product name mappings, causing undefined variable errors and preventing proper dictionary lookups.

**Location**: `app.py` line 553

**Problem**: After calling `get_mapped_product_name()`, the code needed to create a lowercase version for dictionary lookups, but this variable was missing.

## The Fix

### Added Missing Lowercase Variable
```python
# BEFORE (missing prod_string_lower)
original_product = x["Product Name"]
mapped_product = get_mapped_product_name(original_product)
prod_string = mapped_product  # Only had original case
# prod_string_lower was MISSING!

# AFTER (correct)
original_product = x["Product Name"]
mapped_product = get_mapped_product_name(original_product)
prod_string = mapped_product  # Keep original case for reference
prod_string_lower = mapped_product.lower()  # Lowercase for ALL dict lookups
```

### Ensured Consistent Lowercase Usage

All dictionary lookups now correctly use `prod_string_lower`:

1. **Exact match lookups** (lines 581-593):
```python
if prod_string_lower in red:
    for ver in versions_to_try:
        if ver in red[prod_string_lower]:
            return "red"
```

2. **Substring matching** (lines 597-689):
```python
for oname in orange:
    if prod_string_lower in oname.lower():
        orange_products.append(oname)
if len(orange_products) > 0:
    shortest_name = detect_shortest_string(orange_products, prod_string_lower)
```

3. **Helper function calls**:
```python
detect_shortest_string(orange_products, prod_string_lower)  # Not prod_string!
```

## Why Lowercase Matters

The lifecycle dictionaries (red.json, orange.json, green.json) have **lowercase keys** after being processed through the dictionary manipulation code (lines 370-500). For example:
- "AIX Standard Edition" becomes "aix standard edition" 
- "IBM MQ" becomes "ibm mq"
- "WebSphere Application Server" becomes "websphere application server"

Therefore, all lookups MUST use lowercase product names to match these keys.

## Verification

Run this PowerShell command to verify the fix:
```powershell
Select-String -Path "Dashboard_Deployment/app.py" -Pattern "if prod_string in red:"
```

**Expected result**: No matches found (meaning we're using `prod_string_lower` correctly)

## Impact

### Products Now Correctly Matched
These products (and many others) should now match correctly:
- **AIX** → "aix standard edition" in lifecycle dict
- **IBM MQ** → "ibm mq" in lifecycle dict  
- **WebSphere Application Server** → "websphere application server" in lifecycle dict
- **IBM Sterling B2B Integrator** → "ibm sterling b2b integrator" in lifecycle dict
- **IBM Security QRadar SIEM** → "ibm security qradar siem" in lifecycle dict

### Expected Results
- Fewer "N/A Version" (blue) bubbles in Graph 2
- More accurate red/orange/green lifecycle status indicators
- Better product name matching across all variations

## Testing Recommendations

1. **Check AIX products**: Should now show correct lifecycle status instead of blue
2. **Check Sterling products**: Verify Connect:Direct, B2B Integrator, File Gateway match correctly
3. **Check WebSphere products**: Ensure Application Server, Liberty, etc. match
4. **Check Security products**: QRadar, Guardium, zSecure should match
5. **Monitor blue bubbles**: Any remaining blues should be investigated for new mapping needs

## Files Modified

1. **Dashboard_Deployment/app.py**
   - Line 554: Added `prod_string_lower = mapped_product.lower()`
   - Lines 581-593: Verified exact match lookups use `prod_string_lower`
   - Lines 597-689: Verified substring matching uses `prod_string_lower`
   - All `detect_shortest_string()` calls pass `prod_string_lower`

2. **Dashboard_Deployment/product_name_mappings.py**
   - No changes needed - mappings work correctly

## Related Documentation

- `product_name_mappings.py` - Contains the mapping table from ticket names to lifecycle names
- `FINAL_DIAGNOSIS_AND_FIX.md` - Previous lifecycle data format fixes
- `MAY_2026_DEPLOYMENT_COMPLETE.md` - May 2026 data deployment notes

## Notes

- The lifecycle dictionaries have lowercase keys after processing
- Product name mappings in `product_name_mappings.py` return proper case, which we then lowercase
- Version strings are always compared in lowercase for flexibility
- The `process_blues()` function (lines 707+) uses pidname which is already lowercase, so it wasn't affected by this issue

---
*Fix applied by Bob on June 9, 2026*
*Corrected after feedback from Claude*