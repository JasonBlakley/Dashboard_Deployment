"""
Blue Bubble Analysis Script
Identifies products and versions that don't match lifecycle dictionaries
"""

import pandas as pd
import json
import os
import sys

# Add Dashboard_Deployment to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from product_name_mappings import get_mapped_product_name, normalize_version

# Change to Dashboard_Deployment directory
os.chdir(os.path.dirname(__file__))

# Load lifecycle dictionaries from Files/2026/Product Lifecycle
print("Loading lifecycle dictionaries...")
with open('../Files/2026/Product Lifecycle/Red_dict_May_26_final.json', 'r') as f:
    red = json.load(f)
with open('../Files/2026/Product Lifecycle/Orange_dict_May_26_final.json', 'r') as f:
    orange = json.load(f)
with open('../Files/2026/Product Lifecycle/Green_dict_May_26_final.json', 'r') as f:
    green = json.load(f)

print(f"Loaded {len(red)} red products, {len(orange)} orange products, {len(green)} green products")

# Load the most recent data file
print("\nLoading May 2026 data...")
may_data = pd.read_csv('../Files/2026/May/May_2026_merged.csv', low_memory=False)
may_data.rename(columns={'Global Buying Group Name_x': 'Global Buying Group Name', 'Product_x': 'Product'}, inplace=True)

print(f"Loaded {len(may_data):,} records from May 2026")

# Get unique product/version combinations
print("\nAnalyzing unique product/version combinations...")
product_versions = may_data[['Product Name', 'Product']].drop_duplicates()
print(f"Found {len(product_versions)} unique product/version combinations")

# Function to check if a product/version matches lifecycle data
def check_lifecycle_match(product_name, version):
    """Check if product/version matches any lifecycle dictionary"""
    
    # Handle NaN or non-string product names
    if pd.isna(product_name):
        product_name = ""
    
    # Apply product name mapping
    mapped_product = get_mapped_product_name(str(product_name))
    prod_string_lower = str(mapped_product).lower()
    
    # Normalize version
    version_str = str(version).strip() if pd.notna(version) else ""
    normalized_versions = normalize_version(version_str)  # Returns a list
    
    # Try multiple version formats
    versions_to_try = [version_str.lower()] + normalized_versions
    if '.' in version_str:
        versions_to_try.append(version_str.split('.')[0])
    versions_to_try = [v for v in versions_to_try if v]  # Remove empty strings
    
    # Check exact matches in all dictionaries
    found_in = []
    matched_version = None
    
    for dict_name, lifecycle_dict in [('red', red), ('orange', orange), ('green', green)]:
        if prod_string_lower in lifecycle_dict:
            # Skip if lifecycle_dict value is None or not a list
            if lifecycle_dict[prod_string_lower] is None or not isinstance(lifecycle_dict[prod_string_lower], list):
                continue
            for ver in versions_to_try:
                if ver in [v.lower() for v in lifecycle_dict[prod_string_lower] if v is not None]:
                    found_in.append(dict_name)
                    matched_version = ver
                    break
    
    # Check substring matches
    if not found_in:
        for dict_name, lifecycle_dict in [('red', red), ('orange', orange), ('green', green)]:
            for key in lifecycle_dict.keys():
                if prod_string_lower in key.lower() or key.lower() in prod_string_lower:
                    # Skip if lifecycle_dict[key] is None or not a list
                    if lifecycle_dict[key] is None or not isinstance(lifecycle_dict[key], list):
                        continue
                    for ver in versions_to_try:
                        if ver in [v.lower() for v in lifecycle_dict[key] if v is not None]:
                            found_in.append(f"{dict_name} (substring: {key})")
                            matched_version = ver
                            break
                if found_in:
                    break
    
    return {
        'original_product': product_name,
        'mapped_product': mapped_product,
        'version': version_str,
        'normalized_versions': ', '.join(normalized_versions),
        'found_in': ', '.join(found_in) if found_in else 'NOT FOUND',
        'matched_version': matched_version if matched_version else 'N/A',
        'is_blue': len(found_in) == 0
    }

# Analyze all product/version combinations
print("\nAnalyzing matches...")
results = []
for idx, row in product_versions.iterrows():
    result = check_lifecycle_match(row['Product Name'], row['Product'])
    results.append(result)
    
    if idx % 100 == 0:
        print(f"  Processed {idx}/{len(product_versions)} combinations...")

# Create results DataFrame
results_df = pd.DataFrame(results)

# Summary statistics
total_combinations = len(results_df)
blue_bubbles = results_df[results_df['is_blue'] == True]
matched = results_df[results_df['is_blue'] == False]

print("\n" + "="*80)
print("ANALYSIS SUMMARY")
print("="*80)
print(f"Total unique product/version combinations: {total_combinations}")
print(f"Matched to lifecycle data: {len(matched)} ({len(matched)/total_combinations*100:.1f}%)")
print(f"NOT matched (blue bubbles): {len(blue_bubbles)} ({len(blue_bubbles)/total_combinations*100:.1f}%)")

# Show products with most blue bubbles
print("\n" + "="*80)
print("TOP 20 PRODUCTS WITH UNMATCHED VERSIONS (Blue Bubbles)")
print("="*80)
blue_by_product = blue_bubbles.groupby('original_product').size().sort_values(ascending=False).head(20)
for product, count in blue_by_product.items():
    print(f"{product}: {count} unmatched version(s)")

# Show all unmatched combinations
print("\n" + "="*80)
print("ALL UNMATCHED PRODUCT/VERSION COMBINATIONS")
print("="*80)
print(f"{'Product Name':<50} {'Version':<15} {'Mapped To':<50}")
print("-"*115)
for idx, row in blue_bubbles.sort_values('original_product').iterrows():
    print(f"{row['original_product']:<50} {row['version']:<15} {row['mapped_product']:<50}")

# Save detailed results to CSV
output_file = 'blue_bubble_analysis_results.csv'
results_df.to_csv(output_file, index=False)
print(f"\n✓ Detailed results saved to: {output_file}")

# Save just the unmatched ones to a separate file
unmatched_file = 'unmatched_products_versions.csv'
blue_bubbles.to_csv(unmatched_file, index=False)
print(f"✓ Unmatched products saved to: {unmatched_file}")

# Check if specific products are in lifecycle dictionaries
print("\n" + "="*80)
print("CHECKING SPECIFIC PRODUCTS IN LIFECYCLE DICTIONARIES")
print("="*80)

test_products = ['aix', 'aix standard edition', 'ibm aix', 'websphere', 'ibm mq', 'sterling']
for test_prod in test_products:
    found = []
    for dict_name, lifecycle_dict in [('red', red), ('orange', orange), ('green', green)]:
        if test_prod in lifecycle_dict:
            found.append(f"{dict_name} (exact)")
        else:
            # Check substring
            for key in lifecycle_dict.keys():
                if test_prod in key.lower():
                    found.append(f"{dict_name} (in '{key}')")
                    break
    
    if found:
        print(f"'{test_prod}': Found in {', '.join(found)}")
    else:
        print(f"'{test_prod}': NOT FOUND in any dictionary")

print("\n" + "="*80)
print("Analysis complete!")
print("="*80)

# Made with Bob
