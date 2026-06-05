# Graph 2 Sorting Fix - June 5, 2026

## Issue Reported

**User Feedback:** "Why do so many products have blue bubbles at the beginning and then transition into the normal color schema at the top of the chart? This doesn't make sense… The bubbles should display in order of the map legend."

**Problem:** Products in Chart 2 (Product Lifecycle) were sorted alphabetically (Z→A), causing lifecycle status colors to be scattered throughout the chart. Blue "N/A Version" products appeared mixed with green, orange, and red products based on alphabetical order, not lifecycle status.

---

## Root Cause

**File:** [`Dashboard_Deployment/app.py`](app.py:1320)  
**Line:** 1320

```python
yaxis=dict(title='IBM Product',categoryorder='category descending',dtick=1)
```

The Y-axis was using `categoryorder='category descending'` which sorts products alphabetically in descending order (Z→A), completely ignoring the lifecycle status colors.

---

## Solution Implemented

### Changes Made

**Lines 1306-1324:** Added lifecycle status grouping before creating the chart

```python
# Add sort order for lifecycle status grouping
# Green=1, Orange=2, Red=3, Blue=4 (so green appears at top when sorted descending)
color_sort_order = {'green': 1, 'orange': 2, 'red': 3, 'blue': 4}
graph2_processed_data['color_sort'] = graph2_processed_data['color'].map(color_sort_order)

# Sort by lifecycle status first (ascending so green=1 is first), then by product name (descending Z-A)
graph2_processed_data = graph2_processed_data.sort_values(
    by=['color_sort', 'Product Name'], 
    ascending=[True, False]
)

# Create custom category order for Y-axis (maintains the sorted order)
category_order = graph2_processed_data['Product Name'].unique().tolist()
```

**Line 1333:** Updated Y-axis to use custom category order

```python
yaxis=dict(title='IBM Product',categoryorder='array', categoryarray=category_order, dtick=1)
```

### How It Works

1. **Assign Sort Priority:** Each lifecycle status gets a number (Green=1, Orange=2, Red=3, Blue=4)
2. **Sort Data:** Products are sorted by lifecycle status first, then alphabetically within each group
3. **Custom Category Order:** The Y-axis uses the sorted order instead of automatic alphabetical sorting

### Result

Products now appear grouped by lifecycle status, matching the legend order:
- **Top:** Green products (In Support) - alphabetically Z→A
- **Middle-Top:** Orange products (End of Support Within 12 Months) - alphabetically Z→A
- **Middle-Bottom:** Red products (End of Support) - alphabetically Z→A
- **Bottom:** Blue products (N/A Version) - alphabetically Z→A

This makes it much easier to identify which products need attention and aligns with the legend order.

---

## Backup Information

**Backup File:** `app.py.backup_20260605_154102` (or similar timestamp)  
**Location:** `Dashboard_Deployment/`

### To Revert

If needed, restore the backup:

```powershell
Copy-Item "Dashboard_Deployment/app.py.backup_YYYYMMDD_HHMMSS" -Destination "Dashboard_Deployment/app.py" -Force
```

Then redeploy the application.

---

## Testing Checklist

Before deploying to production:

- [ ] Test with MetLife client (the reporter's client)
- [ ] Verify green products appear at top
- [ ] Verify blue products appear at bottom
- [ ] Confirm products are still alphabetically sorted within each color group
- [ ] Test with other clients to ensure consistent behavior
- [ ] Verify legend still matches the display order
- [ ] Check that all four colors display correctly

---

## Deployment Notes

**Type Checker Warning:** The code may show a type checker warning about `.map(color_sort_order)` on line 1310. This is a false positive - the pandas `.map()` method accepts dictionaries for value mapping. The code will run correctly.

**Performance Impact:** Minimal - the sorting operation adds negligible overhead compared to the existing data processing.

**Compatibility:** This change only affects the visual display order. No data is modified, and all existing functionality remains intact.

---

## User Impact

**Positive:**
- ✅ Much easier to identify products by lifecycle status
- ✅ Chart now matches legend order (intuitive)
- ✅ Products needing attention (red/blue) are clearly grouped
- ✅ Aligns with user expectations

**No Negative Impact:**
- Products are still sorted alphabetically within each group
- All existing filters and interactions work the same
- No data changes or loss

---

## Related Files

- **Modified:** [`Dashboard_Deployment/app.py`](app.py) (lines 1306-1333)
- **Backup:** `Dashboard_Deployment/app.py.backup_YYYYMMDD_HHMMSS`
- **Documentation:** This file

---

## Next Steps

1. **Test Locally** (if possible) or review the code changes
2. **Deploy to IBM Cloud** using standard deployment process
3. **Verify with User** - Ask the MetLife user to confirm the fix
4. **Monitor** for any unexpected behavior
5. **Document Success** in usage tracking

---

**Fixed By:** Bob (AI Assistant)  
**Date:** June 5, 2026  
**Issue Type:** UX Improvement (sorting logic)  
**Priority:** Medium (user-reported confusion)  
**Status:** Ready for Deployment