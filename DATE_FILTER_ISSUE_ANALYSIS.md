# Date Filter Issue Analysis

## Problem Statement
The date dropdown filter (Previous 3 Months, Previous 6 Months, Previous 1 Year) is not working correctly for all three graphs:
- **Previous 3 Months**: Working correctly ✓
- **Previous 6 Months**: Showing January 2026 through March 2026 (incorrect - should show Oct 2025 through March 2026)
- **Previous 1 Year**: Likely incorrect as well

## Root Cause Analysis

### Current Implementation
The date filtering logic has TWO separate implementations:

#### 1. In `graph_data_prep()` function (lines 837-953)
```python
if start_interval:
    # start_interval is the number of months to include
    # For "last N months", go back N-1 months to include N complete months
    start_date = latest_date - relativedelta(months=start_interval - 1)
    data_filtered_by_date = filtered_data_by_client[(filtered_data_by_client['Date'] <= latest_date) & (filtered_data_by_client['Date'] >= start_date)]
```

#### 2. In each `update_graphX()` callback (for date label calculation)
```python
if interval_months != None:
    from dateutil.relativedelta import relativedelta
    # Calculate start date: for "last N months", go back N-1 months
    # Example: "last 3 months" from March = go back 2 months to January (Jan, Feb, Mar = 3 months)
    client_start_date = client_latest_date - relativedelta(months=interval_months - 1)
    # Get actual min date from filtered data to ensure accuracy
    date_filtered_data = client_filtered_data[(client_filtered_data['Date'] <= client_latest_date) & (client_filtered_data['Date'] >= client_start_date)]
    actual_start_date = date_filtered_data['Date'].min()
```

### The Problem
**The date label calculation in each graph callback is NOT using the filtered data from `graph_data_prep()`!**

Instead, it's:
1. Re-filtering the data independently
2. Using `client_filtered_data` (which is filtered by client/CMR but NOT by the date interval)
3. Calculating the date range from this unfiltered data

This means:
- The graph shows data filtered by `graph_data_prep()` (correct)
- But the date label is calculated from a different filter (incorrect)

### Why "Previous 3 Months" Works
It works by coincidence because:
- Current date: April 2026
- Latest data: March 2026
- 3 months back from March = January 2026
- This happens to match what's in the data

### Why "Previous 6 Months" Shows Wrong Dates
- Current date: April 2026
- Latest data: March 2026
- The label calculation uses `client_filtered_data` which includes ALL months
- It calculates: March 2026 - 5 months = October 2025
- But then it filters this data and gets min date
- However, the filter is applied to the WRONG dataset (one that wasn't filtered by `graph_data_prep`)

## Solution

### Option 1: Pass Filtered Data to Callbacks (Recommended)
Modify `graph_data_prep()` to return both the processed data AND the date-filtered raw data, then use that for date label calculation.

### Option 2: Standardize Date Calculation
Move the date label calculation into `graph_data_prep()` and return it along with the processed data.

### Option 3: Fix the Date Label Calculation
Ensure the date label calculation uses the SAME filtering logic as `graph_data_prep()`:
- Use the same `start_interval` value
- Apply it to the same base dataset
- Calculate dates from the actually filtered data

## Recommended Fix

### Step 1: Modify `graph_data_prep()` to return date range info
```python
def graph_data_prep(selected_client, data, graph_num, start_interval=None, product_type=None, cmr_numbers=None):
    # ... existing code ...
    
    # Calculate date range for labels
    if start_interval:
        start_date = latest_date - relativedelta(months=start_interval - 1)
        actual_start_date = data_filtered_by_date['Date'].min()
        actual_end_date = data_filtered_by_date['Date'].max()
    else:
        actual_start_date = data_filtered_by_date['Date'].min()
        actual_end_date = data_filtered_by_date['Date'].max()
    
    date_info = {
        'start_date': actual_start_date,
        'end_date': actual_end_date,
        'start_month': calendar.month_name[actual_start_date.month],
        'start_year': actual_start_date.year,
        'end_month': calendar.month_name[actual_end_date.month],
        'end_year': actual_end_date.year
    }
    
    return client_defects_data, date_info
```

### Step 2: Update all three graph callbacks
```python
def update_graph1(...):
    # ... existing code ...
    
    graph1_processed_data, date_info = graph_data_prep(...)
    
    # Use date_info for label
    date_label = f"{date_info['start_month']} {date_info['start_year']} through {date_info['end_month']} {date_info['end_year']}"
    
    # ... rest of code ...
```

### Step 3: Apply same fix to update_graph2() and update_graph3()

## Testing Plan
1. Test "Previous 3 Months" - should still work
2. Test "Previous 6 Months" - should show correct 6-month range
3. Test "Previous 1 Year" - should show correct 12-month range
4. Test with different clients to ensure consistency
5. Test with CMR filter combinations
6. Test "Clear Filters" to ensure it resets properly

## Files to Modify
- `Dashboard_Deployment/app.py`
  - Function: `graph_data_prep()` (lines 837-953)
  - Function: `update_graph1()` (lines 1000-1167)
  - Function: `update_graph2()` (lines 1169-1387)
  - Function: `update_graph3()` (lines 1388-1550)

## Current Date: April 28, 2026
Latest data available: March 2026

Expected behavior:
- **Previous 3 Months**: January 2026 - March 2026 ✓
- **Previous 6 Months**: October 2025 - March 2026 (currently broken)
- **Previous 1 Year**: April 2025 - March 2026 (likely broken)