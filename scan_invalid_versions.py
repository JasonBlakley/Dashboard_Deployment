"""
Invalid Version Scanner
=======================
Scans all monthly ticket data files to identify invalid version strings that appear
as blue bubbles in the dashboard.

This script identifies:
1. Instructional text (e.g., "For older versions, please select...")
2. HTML tags or encoded HTML
3. Error messages
4. Non-version text patterns
5. Unusually long strings that aren't valid versions

Author: Bob
Date: June 2026
"""

import pandas as pd
import os
import re
from collections import defaultdict

# Patterns that indicate invalid version strings
INVALID_PATTERNS = [
    r'for older versions',
    r'please select',
    r'cast iron',
    r'<[^>]+>',  # HTML tags
    r'&[a-z]+;',  # HTML entities
    r'http[s]?://',  # URLs
    r'error',
    r'n/a',
    r'not applicable',
    r'see ',
    r'refer to',
    r'contact',
    r'\(.*\)',  # Text in parentheses that's too long
]

def is_invalid_version(version_str):
    """
    Check if a version string is invalid (not a real version number).
    
    Args:
        version_str: The version string to check
        
    Returns:
        tuple: (is_invalid, reason) where is_invalid is bool and reason is string
    """
    if pd.isna(version_str) or version_str == '':
        return False, "Empty/null (acceptable)"
    
    version_str = str(version_str).strip()
    version_lower = version_str.lower()
    
    # Check length - versions are typically short
    if len(version_str) > 50:
        return True, f"Too long ({len(version_str)} chars)"
    
    # Check against known invalid patterns
    for pattern in INVALID_PATTERNS:
        if re.search(pattern, version_lower):
            return True, f"Matches pattern: {pattern}"
    
    # Check if it contains too many words (versions shouldn't be sentences)
    word_count = len(version_str.split())
    if word_count > 5:
        return True, f"Too many words ({word_count})"
    
    return False, "Valid"

def scan_csv_file(filepath):
    """
    Scan a CSV file for invalid version strings.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        dict: Results containing invalid versions found
    """
    print(f"\nScanning: {filepath}")
    
    try:
        # Read CSV - assuming 'Product' column contains version
        df = pd.read_csv(filepath, low_memory=False)
        
        # Check if required columns exist
        if 'Product Version' not in df.columns or 'Product Name' not in df.columns:
            print(f"  [SKIP] Missing required columns")
            return None
        
        results = {
            'file': os.path.basename(filepath),
            'total_rows': len(df),
            'invalid_versions': [],
            'products_affected': set()
        }
        
        # Scan each unique product/version combination
        unique_combos = df[['Product Name', 'Product Version']].drop_duplicates()
        
        for idx, row in unique_combos.iterrows():
            product_name = row['Product Name']
            version = row['Product Version']
            
            is_invalid, reason = is_invalid_version(version)
            
            if is_invalid:
                # Count how many tickets have this invalid version
                ticket_count = len(df[(df['Product Name'] == product_name) & (df['Product Version'] == version)])
                
                results['invalid_versions'].append({
                    'product': product_name,
                    'version': str(version),
                    'reason': reason,
                    'ticket_count': ticket_count
                })
                results['products_affected'].add(product_name)
        
        print(f"  [OK] Found {len(results['invalid_versions'])} invalid version strings")
        print(f"  [OK] Affecting {len(results['products_affected'])} products")
        
        return results
        
    except Exception as e:
        print(f"  [ERROR] Error reading file: {e}")
        return None

def main():
    """Main execution function."""
    print("="*80)
    print("INVALID VERSION STRING SCANNER")
    print("="*80)
    print("\nThis script scans ticket data files for invalid version strings that")
    print("cause blue bubbles in the dashboard.")
    print()
    
    # Define directories to scan
    data_dirs = [
        '../Files/2026/Apr',
        '../Files/2026/Feb',
        '../Files/2026/Mar',
        '../Files/2026/May',
    ]
    
    all_results = []
    all_invalid_versions = {}
    
    # Scan each directory
    for data_dir in data_dirs:
        if not os.path.exists(data_dir):
            print(f"\n⚠️  Directory not found: {data_dir}")
            continue
            
        print(f"\n{'='*80}")
        print(f"Scanning directory: {data_dir}")
        print(f"{'='*80}")
        
        # Find all CSV files
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and 'merged' in f.lower()]
        
        for csv_file in csv_files:
            filepath = os.path.join(data_dir, csv_file)
            results = scan_csv_file(filepath)
            
            if results:
                all_results.append(results)
                
                # Aggregate invalid versions across all files
                for inv in results['invalid_versions']:
                    key = f"{inv['product']}|||{inv['version']}"
                    if key not in all_invalid_versions:
                        all_invalid_versions[key] = {
                            'products': set(),
                            'total_tickets': 0,
                            'reason': ''
                        }
                    all_invalid_versions[key]['products'].add(inv['product'])
                    all_invalid_versions[key]['total_tickets'] += inv['ticket_count']
                    all_invalid_versions[key]['reason'] = inv['reason']
    
    # Generate summary report
    print("\n" + "="*80)
    print("SUMMARY REPORT")
    print("="*80)
    
    if not all_invalid_versions:
        print("\n[OK] No invalid version strings found!")
        return
    
    print(f"\nTotal unique invalid version strings found: {len(all_invalid_versions)}")
    print(f"Total files scanned: {len(all_results)}")
    
    # Sort by ticket count (most impactful first)
    sorted_invalid = sorted(
        all_invalid_versions.items(),
        key=lambda x: x[1]['total_tickets'],
        reverse=True
    )
    
    print("\n" + "-"*80)
    print("TOP INVALID VERSION STRINGS (by ticket count)")
    print("-"*80)
    
    for idx, (key, data) in enumerate(sorted_invalid[:20], 1):
        product, version = key.split('|||')
        print(f"\n{idx}. Product: {product}")
        print(f"   Version: {version}")
        print(f"   Reason: {data['reason']}")
        print(f"   Total Tickets: {data['total_tickets']}")
    
    # Save detailed results to CSV
    output_file = 'invalid_versions_report.csv'
    print(f"\n{'='*80}")
    print(f"Saving detailed report to: {output_file}")
    print(f"{'='*80}")
    
    report_data = []
    for key, data in sorted_invalid:
        product, version = key.split('|||')
        report_data.append({
            'Product Name': product,
            'Invalid Version String': version,
            'Reason': data['reason'],
            'Total Tickets Affected': data['total_tickets']
        })
    
    report_df = pd.DataFrame(report_data)
    report_df.to_csv(output_file, index=False)
    print(f"[OK] Report saved successfully!")
    
    # Generate fix recommendations
    print("\n" + "="*80)
    print("FIX RECOMMENDATIONS")
    print("="*80)
    print("""
1. **Data Cleaning Function**: Add a version cleaning function to app.py that:
   - Detects and filters out invalid version strings
   - Replaces them with None/NaN so they don't appear in Chart 2
   - Logs these occurrences for data quality monitoring

2. **Specific Fixes Needed**:
   - App Connect Professional: Filter "(For older versions, please select the Cast Iron product)"
   - Add regex patterns to detect instructional text, HTML, and error messages
   - Set a maximum length threshold for version strings (e.g., 50 characters)

3. **Prevention**:
   - Work with Cognos data team to fix data quality at source
   - Add validation in the data export process
   - Document expected version format for each product

4. **Implementation Priority**:
   - HIGH: App Connect Professional (appears in multiple months)
   - MEDIUM: Any other products with >10 affected tickets
   - LOW: One-off occurrences that can be handled by general cleaning logic
""")
    
    print("\n" + "="*80)
    print("SCAN COMPLETE")
    print("="*80)

if __name__ == '__main__':
    main()

# Made with Bob
