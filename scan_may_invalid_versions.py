"""
Quick Invalid Version Scanner for May 2026
==========================================
Scans May 2026 data to identify invalid version strings.
"""

import pandas as pd
import re

# Patterns that indicate invalid version strings
INVALID_PATTERNS = [
    r'for older versions',
    r'please select',
    r'cast iron',
    r'<[^>]+>',  # HTML tags
    r'&[a-z]+;',  # HTML entities
]

def is_invalid_version(version_str):
    """Check if a version string is invalid."""
    if pd.isna(version_str) or version_str == '':
        return False, "Empty/null"
    
    version_str = str(version_str).strip()
    version_lower = version_str.lower()
    
    # Check length
    if len(version_str) > 50:
        return True, f"Too long ({len(version_str)} chars)"
    
    # Check against known invalid patterns
    for pattern in INVALID_PATTERNS:
        if re.search(pattern, version_lower):
            return True, f"Matches pattern: {pattern}"
    
    # Check if it contains too many words
    word_count = len(version_str.split())
    if word_count > 5:
        return True, f"Too many words ({word_count})"
    
    return False, "Valid"

print("="*80)
print("Scanning May 2026 data for invalid version strings...")
print("="*80)

# Read May 2026 data
filepath = '../Files/2026/May/May_2026_merged.csv'
print(f"\nReading: {filepath}")

df = pd.read_csv(filepath, low_memory=False)
print(f"Total rows: {len(df)}")

# Get unique product/version combinations
unique_combos = df[['Product Name', 'Product Version']].drop_duplicates()
print(f"Unique product/version combinations: {len(unique_combos)}")

# Scan for invalid versions
invalid_versions = []

for idx, row in unique_combos.iterrows():
    product_name = row['Product Name']
    version = row['Product Version']
    
    is_invalid, reason = is_invalid_version(version)
    
    if is_invalid:
        # Count tickets
        ticket_count = len(df[(df['Product Name'] == product_name) & (df['Product Version'] == version)])
        
        invalid_versions.append({
            'Product': product_name,
            'Version': str(version),
            'Reason': reason,
            'Tickets': ticket_count
        })

print(f"\n{'='*80}")
print(f"RESULTS")
print(f"{'='*80}")

if not invalid_versions:
    print("\n[OK] No invalid version strings found!")
else:
    print(f"\nFound {len(invalid_versions)} invalid version strings:\n")
    
    # Sort by ticket count
    invalid_versions.sort(key=lambda x: x['Tickets'], reverse=True)
    
    for idx, inv in enumerate(invalid_versions, 1):
        print(f"{idx}. Product: {inv['Product']}")
        print(f"   Version: {inv['Version']}")
        print(f"   Reason: {inv['Reason']}")
        print(f"   Tickets Affected: {inv['Tickets']}")
        print()
    
    # Save to CSV
    import pandas as pd
    report_df = pd.DataFrame(invalid_versions)
    report_df.to_csv('may_2026_invalid_versions.csv', index=False)
    print(f"[OK] Report saved to: may_2026_invalid_versions.csv")

print(f"\n{'='*80}")
print("SCAN COMPLETE")
print(f"{'='*80}")

# Made with Bob
