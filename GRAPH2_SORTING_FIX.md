# Graph 2 Sorting Fix - June 5, 2026

## Issue Reported
MetLife user reported that Chart 2 (Product Lifecycle Status) shows blue "N/A Version" bubbles scattered throughout the chart instead of being grouped by lifecycle status.

## Root Cause
The Y-axis was using `categoryorder='category descending'` which sorts alphabetically (Z→A) rather than by lifecycle status priority. This caused products to be mixed together regardless of their lifecycle status (Green/Orange/Red/Blue).

## Solution Implemented
Modified the Graph 2 generation logic to:
1. Add a color sort priority field (Green=1, Orange=2, Red=3, Blue=4)
2. Sort products by lifecycle status first, then alphabetically within each group
3. Use a custom category array for Y-axis ordering

## Code Changes
**File:** `Dashboard_Deployment/app.py`
**Lines:** 1306-1333
**Backup:** `app.py.backup_20260605_154102`

```python
# Add sort order for lifecycle status grouping
color_sort_order = {'green': 1, 'orange': 2, 'red': 3, 'blue': 4}
graph2_processed_data['color_sort'] = graph2_processed_data['color'].map(color_sort_order)

# Sort by lifecycle status first, then by product name
graph2_processed_data = graph2_processed_data.sort_values(
    by=['color_sort', 'Product Name'], 
    ascending=[True, False]
)

# Create custom category order for Y-axis
category_order = graph2_processed_data['Product Name'].unique().tolist()

# Update Y-axis with custom category order
yaxis=dict(
    title='IBM Product',
    categoryorder='array', 
    categoryarray=category_order, 
    dtick=1
)
```

## Deployment History

### Initial Deployment Attempt (Failed)
- **Build:** dashboard-graph2-fix-260605-154951
- **Status:** Build succeeded, but deployment failed
- **Error:** `Property probe_readiness.interval has an invalid value: too low`
- **Cause:** Revision 00049 had TCP readiness probe without proper interval configuration

### Readiness Probe Fix
- **Command:** Updated readiness probe configuration via CLI
- **Configuration:**
  - Type: HTTP
  - Path: /health
  - Port: 8051
  - Initial Delay: 10 seconds
  - Interval: 30 seconds
  - Timeout: 5 seconds
  - Failure Threshold: 10

### Successful Deployment
- **Revision:** python-appid-app-00050
- **Deployed:** June 5, 2026 at 15:53 EDT
- **Status:** Running successfully
- **Traffic:** 100% routed to new revision
- **Instances:** 1 running instance (3/3 containers healthy)
- **Previous Revision:** 00049 terminated

## Expected Behavior After Fix
Chart 2 will now display products grouped by lifecycle status:
- 🟢 **Green (In Support)** - Top section
- 🟠 **Orange (End of Support Within 12 Months)** - Middle-top section
- 🔴 **Red (End of Support)** - Middle-bottom section
- 🔵 **Blue (N/A Version)** - Bottom section

Within each color group, products are sorted alphabetically (Z→A).

## Testing Checklist
- [x] Code changes applied
- [x] Backup created
- [x] Git commit and push
- [x] Build triggered and succeeded
- [x] Readiness probe configured
- [x] Deployment successful
- [ ] User verification - MetLife user to confirm fix resolves issue

## Rollback Instructions
If issues arise, rollback to revision 00049:
```bash
ibmcloud ce application update --name python-appid-app --image us.icr.io/python-appid-icr-ns/python-appid-img@sha256:f32e5a46c534427853bc262726c10ef817262c738b3a2c1a7176bdb74c215ef3
```

Or restore from backup:
```bash
cp Dashboard_Deployment/app.py.backup_20260605_154102 Dashboard_Deployment/app.py
```

## Related Documentation
- `AUTOMATION_VALUE_ANALYSIS.md` - Cost savings analysis
- `PROJECT_TAKEOVER_SUMMARY.md` - Project transformation overview
- `DEPLOYMENT_GUIDE.md` - Standard deployment procedures

## Notes
- This fix addresses a UX issue that made the chart difficult to interpret
- No data processing changes - only visualization sorting
- Deployment took ~6 minutes from probe fix to running status
- Old revision (00049) automatically terminated after traffic switch