# Invalid Version String Fix Plan

## Problem Statement

The dashboard displays invalid version strings as blue bubbles in Chart 2 (Product Lifecycle Status). These invalid strings include:
- Instructional text: "(For older versions, please select the Cast Iron product)"
- EOS dates: "7.3 [EOS 30 Sep 2023 Need Service Extension]"
- Build information: "Version 10.1.16 Build: 607 Dec 17"
- Long descriptive strings: "Storage Scale System Data Management Edition v5.2.3"

## Current Impact

- **53 invalid version strings** identified in May 2026 data alone
- **App Connect Professional** has invalid version in 2024 historical data
- These appear as confusing blue bubbles that don't represent actual product versions
- Users cannot determine actual lifecycle status for these entries

## Solution Approach

### Option 1: Filter Invalid Versions (RECOMMENDED)
**What it does:**
- Detects and removes invalid version strings from the dataset
- Replaces invalid versions with `None`/`NaN`
- Chart 2 automatically excludes rows with null versions (existing behavior)

**Result:**
- ✅ Product remains visible in Charts 1 & 3
- ✅ Invalid versions don't appear as bubbles in Chart 2
- ✅ Only valid versions show lifecycle status
- ✅ No confusing blue bubbles for data quality issues

**Example:**
```
BEFORE:
- App Connect Professional: "(For older versions...)" → Blue bubble
- App Connect Professional: "7.5.5" → Proper lifecycle color

AFTER:
- App Connect Professional: "7.5.5" → Proper lifecycle color
(Invalid version filtered out, doesn't appear)
```

### Option 2: Replace with Placeholder (NOT RECOMMENDED)
- Replace invalid versions with "Unknown" or "N/A"
- Would still show as blue bubbles
- Doesn't solve the visual clutter problem

## Implementation Plan

### Step 1: Create Version Validation Function
Add to `app.py` after imports:

```python
def is_valid_version(version_str):
    """
    Check if a version string is valid.
    Returns True if valid, False if invalid.
    """
    if pd.isna(version_str) or version_str == '':
        return True  # Empty is acceptable (will be filtered by Chart 2)
    
    version_str = str(version_str).strip()
    version_lower = version_str.lower()
    
    # Invalid patterns
    invalid_patterns = [
        r'for older versions',
        r'please select',
        r'cast iron',
        r'\[eos\s+\d',  # EOS dates in brackets
        r'need service extension',
        r'out of support',
        r'service extension required',
        r'early ship program',
        r'best effort',
        r'build:\s*\d',  # Build numbers
    ]
    
    # Check length (versions shouldn't be sentences)
    if len(version_str) > 50:
        return False
    
    # Check word count (versions are typically short)
    if len(version_str.split()) > 5:
        return False
    
    # Check against invalid patterns
    for pattern in invalid_patterns:
        if re.search(pattern, version_lower):
            return False
    
    return True
```

### Step 2: Apply Cleaning Before Chart 2 Processing
In the `update_graph2()` function, add cleaning step:

```python
# After filtering data but before grouping for Chart 2
# Clean invalid versions
graph2_data['Product Version'] = graph2_data.apply(
    lambda row: row['Product Version'] if is_valid_version(row['Product Version']) else None,
    axis=1
)

# Remove rows with null versions (Chart 2 requires versions)
graph2_data = graph2_data[graph2_data['Product Version'].notna()]
```

### Step 3: Add Logging (Optional)
Track which versions are being filtered:

```python
invalid_versions = graph2_data[~graph2_data['Product Version'].apply(is_valid_version)]
if len(invalid_versions) > 0:
    logging.info(f"Filtered {len(invalid_versions)} invalid version strings from Chart 2")
```

## Testing Plan

1. **Before Fix**: Note current blue bubbles in Chart 2
2. **Apply Fix**: Implement version cleaning function
3. **Verify**:
   - App Connect Professional no longer shows "(For older versions...)" bubble
   - IBM i no longer shows "[EOS...Need Service Extension]" bubbles
   - Products still appear in Charts 1 & 3
   - Valid versions still show correct lifecycle colors
4. **Monitor**: Check dashboard logs for filtered versions

## Expected Results

### Products Affected (May 2026 Data)
- **IBM i**: 73 tickets with invalid versions will be filtered
- **Storage Scale**: 82 tickets with long descriptive versions
- **Verify Identity Governance**: 138 tickets with descriptive versions
- **53 total** invalid version patterns identified

### User Experience Improvement
- Cleaner Chart 2 with only meaningful version bubbles
- No confusion about lifecycle status
- Products remain visible across all charts
- Focus on actionable lifecycle information

## Rollback Plan

If issues arise:
1. Comment out the version cleaning code
2. Restart application
3. Dashboard returns to previous behavior
4. Investigate specific edge cases

## Future Improvements

1. **Data Quality at Source**: Work with Cognos team to prevent invalid versions
2. **Version Normalization**: Standardize version formats (e.g., "V.10.0.2" → "10.0.2")
3. **Monitoring Dashboard**: Track data quality metrics over time
4. **User Feedback**: Add tooltip explaining why some versions don't appear

## Conclusion

This fix improves dashboard usability by filtering out invalid version strings while maintaining product visibility. It's a targeted solution that addresses the root cause without removing valuable data.