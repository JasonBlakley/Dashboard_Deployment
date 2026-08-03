#!/usr/bin/env python3
"""
Lifecycle Match Report Generator
=================================
Replicates the exact logic from app.py's calc_color() function to analyze
product/version combinations and generate detailed matching reports.

This script helps diagnose lifecycle matching issues by showing exactly how
each product/version is matched (or not matched) against the lifecycle dictionaries.

Author: Bob
Date: June 12, 2026
"""

import pandas as pd
import json
import re
import sys
from collections import defaultdict
from datetime import datetime

# Import the product name mappings and normalize_version function
from product_name_mappings import get_mapped_product_name, normalize_version


def load_lifecycle_dictionaries():
    """
    Load and preprocess lifecycle dictionaries exactly as app.py does.
    Returns lowercase dictionaries ready for matching.
    """
    print("Loading lifecycle dictionaries...")
    
    # Load the three lifecycle dictionaries
    with open('../Files/2026/Product Lifecycle/Red_dict_May_26_final.json', 'r', encoding='utf-8') as f:
        red = json.load(f)
    
    with open('../Files/2026/Product Lifecycle/Orange_dict_May_26_final.json', 'r', encoding='utf-8') as f:
        orange = json.load(f)
    
    with open('../Files/2026/Product Lifecycle/Green_dict_May_26_final.json', 'r', encoding='utf-8') as f:
        green = json.load(f)
    
    print(f"  Red: {len(red)} products")
    print(f"  Orange: {len(orange)} products")
    print(f"  Green: {len(green)} products")
    
    # Apply all the transformations from app.py (lines 392-525)
    # PowerVM / VIOS
    if 'PowerVM VIOS Enterprise Edition' in red:
        red['PowerVM / VIOS'] = red['PowerVM VIOS Enterprise Edition']
        del red['PowerVM VIOS Enterprise Edition']
    if 'PowerVM VIOS Enterprise Edition' in green:
        green['PowerVM / VIOS'] = green['PowerVM VIOS Enterprise Edition']
        del green['PowerVM VIOS Enterprise Edition']
    if 'PowerVM VIOS Enterprise Edition' in orange:
        orange['PowerVM / VIOS'] = orange['PowerVM VIOS Enterprise Edition']
        del orange['PowerVM VIOS Enterprise Edition']
    
    # QRadar
    if 'IBM QRadar' in red:
        red['IBM QRadar on Cloud'] = red['IBM QRadar']
        del red['IBM QRadar']
    if 'IBM QRadar' in green:
        green['IBM QRadar on Cloud'] = green['IBM QRadar']
        del green['IBM QRadar']
    if 'IBM QRadar' in orange:
        orange['IBM QRadar on Cloud'] = orange['IBM QRadar']
        del orange['IBM QRadar']
    
    # Content Manager OnDemand
    if 'Content Manager OnDemand for z/OS' in red:
        red['Content Manager OnDemand'] = red['Content Manager OnDemand for z/OS']
        del red['Content Manager OnDemand for z/OS']
    if 'Content Manager OnDemand for z/OS' in green:
        green['Content Manager OnDemand'] = green['Content Manager OnDemand for z/OS']
        del green['Content Manager OnDemand for z/OS']
    if 'Content Manager OnDemand for z/OS' in orange:
        orange['Content Manager OnDemand'] = orange['Content Manager OnDemand for z/OS']
        del orange['Content Manager OnDemand for z/OS']
    
    # Tivoli Management Services
    if 'IBM Tivoli Management Services on z/OS' in red:
        red['Tivoli Management Services for z/OS'] = red['IBM Tivoli Management Services on z/OS']
        del red['IBM Tivoli Management Services on z/OS']
    if 'IBM Tivoli Management Services on z/OS' in green:
        green['Tivoli Management Services for z/OS'] = green['IBM Tivoli Management Services on z/OS']
        del green['IBM Tivoli Management Services on z/OS']
    if 'IBM Tivoli Management Services on z/OS' in orange:
        orange['Tivoli Management Services for z/OS'] = orange['IBM Tivoli Management Services on z/OS']
        del orange['IBM Tivoli Management Services on z/OS']
    
    # Sterling Connect:Direct
    if 'IBM Sterling Connect:Direct for z/OS' in green:
        green['Sterling Connect Direct for z/OS'] = green['IBM Sterling Connect:Direct for z/OS']
        del green['IBM Sterling Connect:Direct for z/OS']
    
    # Netcool
    if 'Tivoli Netcool/OMNIbus' in red:
        red['Netcool/OMNIbus'] = red['Tivoli Netcool/OMNIbus']
    if 'Tivoli Netcool/Impact' in red:
        red['Netcool/Impact'] = red['Tivoli Netcool/Impact']
    
    # Cloud Pak for Data
    if 'IBM Cloud Pak for Data' in green:
        green['IBM Cloud Pak for Data'].extend([f'4.{i}.x' for i in range(30)])
    
    # SevOne
    if 'IBM SevOne Network Performance Management' in green:
        green['IBM SevOne Network Performance Management'].extend([f'6.{i}.x' for i in range(30)])
    
    # Cloudera
    if 'Cloudera Data Platform Private Cloud Plus Add-on with IBM' in red:
        red['Cloudera CDP Private Cloud'] = red['Cloudera Data Platform Private Cloud Plus Add-on with IBM']
    if 'Cloudera Data Platform Private Cloud Plus Add-on with IBM' in orange:
        orange['Cloudera CDP Private Cloud'] = orange['Cloudera Data Platform Private Cloud Plus Add-on with IBM']
    if 'Cloudera Data Platform Private Cloud Plus Add-on with IBM' in green:
        green['Cloudera CDP Private Cloud'] = green['Cloudera Data Platform Private Cloud Plus Add-on with IBM']
    
    # Aspera
    if 'IBM Aspera Faspex' in red:
        red['Aspera'] = red['IBM Aspera Faspex']
    if 'IBM Aspera Faspex' in green:
        green['Aspera'] = green['IBM Aspera Faspex']
    if 'IBM Aspera Faspex' in orange:
        orange['Aspera'] = orange['IBM Aspera Faspex']
    
    # AIX - merge both AIX Standard Edition and IBM AIX 7 Standard Edition
    if 'AIX Standard Edition' in red:
        red['AIX'] = list(red['AIX Standard Edition'])
    if 'AIX Standard Edition' in green:
        green['AIX'] = list(green['AIX Standard Edition'])
    if 'AIX Standard Edition' in orange:
        orange['AIX'] = list(orange['AIX Standard Edition'])
    
    if 'IBM AIX 7 Standard Edition' in green:
        green.setdefault('AIX', []).extend(green['IBM AIX 7 Standard Edition'])
    if 'IBM AIX 7 Standard Edition' in red:
        red.setdefault('AIX', []).extend(red['IBM AIX 7 Standard Edition'])
    if 'IBM AIX 7 Standard Edition' in orange:
        orange.setdefault('AIX', []).extend(orange['IBM AIX 7 Standard Edition'])
    
    # Aspera HSTE
    if 'IBM Aspera High-Speed Transfer Endpoint (HSTE)' in red:
        red['Aspera'] = red['IBM Aspera High-Speed Transfer Endpoint (HSTE)']
    if 'IBM Aspera High-Speed Transfer Endpoint (HSTE)' in green:
        green['Aspera'] = green['IBM Aspera High-Speed Transfer Endpoint (HSTE)']
    if 'IBM Aspera High-Speed Transfer Endpoint (HSTE)' in orange:
        orange['Aspera'] = orange['IBM Aspera High-Speed Transfer Endpoint (HSTE)']
    
    # Netcool Impact
    if 'Tivoli Netcool/Impact' in red:
        red['Netcool/Impact'] = red['Tivoli Netcool/Impact']
    if 'Tivoli Netcool/Impact' in green:
        green['Netcool/Impact'] = green['Tivoli Netcool/Impact']
    if 'Tivoli Netcool/Impact' in orange:
        orange['Netcool/Impact'] = orange['Tivoli Netcool/Impact']
    
    # Netcool OMNIbus
    if 'Tivoli Netcool/OMNIbus' in red:
        red['Netcool/OMNIbus'] = red['Tivoli Netcool/OMNIbus']
    if 'Tivoli Netcool/OMNIbus' in green:
        green['Netcool/OMNIbus'] = green['Tivoli Netcool/OMNIbus']
    if 'Tivoli Netcool/OMNIbus' in orange:
        orange['Netcool/OMNIbus'] = orange['Tivoli Netcool/OMNIbus']
    
    # Sterling Connect:Direct with space
    if 'IBM Sterling Connect:Direct for z/OS' in red:
        red['IBM Sterling Connect: Direct for z/OS'] = red['IBM Sterling Connect:Direct for z/OS']
    if 'IBM Sterling Connect:Direct for z/OS' in green:
        green['IBM Sterling Connect: Direct for z/OS'] = green['IBM Sterling Connect:Direct for z/OS']
    if 'IBM Sterling Connect:Direct for z/OS' in orange:
        orange['IBM Sterling Connect: Direct for z/OS'] = orange['IBM Sterling Connect:Direct for z/OS']
    
    # QRadar SIEM
    if 'IBM Security QRadar SIEM' in red:
        red['QRadar SIEM'] = red['IBM Security QRadar SIEM']
    if 'IBM Security QRadar SIEM' in green:
        green['QRadar SIEM'] = green['IBM Security QRadar SIEM']
    if 'IBM Security QRadar SIEM' in orange:
        orange['QRadar SIEM'] = orange['IBM Security QRadar SIEM']
    
    # QRadar Applications
    if 'IBM QRadar' in red:
        red['QRadar Applications'] = red['IBM QRadar']
    if 'IBM QRadar' in green:
        green['QRadar Applications'] = green['IBM QRadar']
    if 'IBM QRadar' in orange:
        orange['QRadar Applications'] = orange['IBM QRadar']
    
    # Order Management
    if 'IBM Sterling Order Management System' in green:
        green['Order Management On Cloud'] = green['IBM Sterling Order Management System']
    
    # TRIRIGA
    if 'IBM TRIRIGA Application Platform' in red:
        red['TRIRIGA Platform'] = red['IBM TRIRIGA Application Platform']
    if 'IBM TRIRIGA Application Platform' in green:
        green['TRIRIGA Platform'] = green['IBM TRIRIGA Application Platform']
    if 'IBM TRIRIGA Application Platform' in orange:
        orange['TRIRIGA Platform'] = orange['IBM TRIRIGA Application Platform']
    
    # Convert all keys to lowercase (lines 533-535)
    red = {red_key.lower(): value for red_key, value in red.items()}
    green = {green_key.lower(): value for green_key, value in green.items()}
    orange = {orange_key.lower(): value for orange_key, value in orange.items()}
    
    # Remove entries with None values (lines 536-538)
    red = {key: value for key, value in red.items() if value and value[0] is not None}
    orange = {key: value for key, value in orange.items() if value and value[0] is not None}
    green = {key: value for key, value in green.items() if value and value[0] is not None}
    
    print(f"After preprocessing:")
    print(f"  Red: {len(red)} products")
    print(f"  Orange: {len(orange)} products")
    print(f"  Green: {len(green)} products")
    
    return red, orange, green


def detect_shortest_string(LIST, prod_string):
    """
    Find the best matching product name from a list.
    Replicates app.py lines 693-723.
    """
    prod_lower = prod_string.lower()
    
    # Check for exact match (case-insensitive)
    for item in LIST:
        if item.lower() == prod_lower:
            return item
    
    # Check for standard edition variant
    for item in LIST:
        if item.lower() == prod_lower + ' standard edition':
            return item
    
    # Check for IBM prefix variant
    for item in LIST:
        if item.lower() == 'ibm ' + prod_lower:
            return item
    
    # Find best match by length ratio
    best_match = 0
    loc = None
    for index, string in enumerate(LIST):
        percent_match = len(prod_string) / len(string)
        if percent_match > best_match:
            best_match = percent_match
            loc = index
    return LIST[loc] if loc is not None else LIST[0]


def calc_color_detailed(product_name, product_version, red, orange, green):
    """
    Replicate calc_color() logic from app.py (lines 543-692) with detailed tracking.
    Returns: (color, match_type, match_details)
    """
    # Handle NaN/None product names
    if pd.isna(product_name) or product_name is None:
        return "blue", "no_match", "Product name is null or NaN"
    
    # Apply product name mapping
    original_product = str(product_name)
    mapped_product = get_mapped_product_name(original_product)
    prod_string = str(mapped_product)
    prod_string_lower = prod_string.lower()
    version_raw = str(product_version)
    
    # Normalize version
    versions_to_try = normalize_version(version_raw)
    version = versions_to_try[0]
    
    # Check if version is null/empty
    if version_raw in [None, " ", "", "NaN", "nan", "None"]:
        return "blue", "no_match", "Empty or null version"
    
    # SaaS products check
    def is_saas_product(d, key):
        versions = d.get(key, [])
        return len(versions) > 0 and all(v.lower() == 'saas' for v in versions if v)
    
    # Check SaaS in red
    if prod_string_lower in red and is_saas_product(red, prod_string_lower):
        return "red", "saas", f"SaaS product in red dict"
    
    # Check SaaS in orange
    if prod_string_lower in orange and is_saas_product(orange, prod_string_lower):
        return "orange", "saas", f"SaaS product in orange dict"
    
    # Check SaaS in green
    if prod_string_lower in green and is_saas_product(green, prod_string_lower):
        return "green", "saas", f"SaaS product in green dict"
    
    # Try exact product name match with all normalized version formats
    if prod_string_lower in red:
        for ver in versions_to_try:
            if ver in red[prod_string_lower]:
                return "red", "exact", f"Exact match: product='{prod_string_lower}', version='{ver}'"
    
    if prod_string_lower in orange:
        for ver in versions_to_try:
            if ver in orange[prod_string_lower]:
                return "orange", "exact", f"Exact match: product='{prod_string_lower}', version='{ver}'"
    
    if prod_string_lower in green:
        for ver in versions_to_try:
            if ver in green[prod_string_lower]:
                return "green", "exact", f"Exact match: product='{prod_string_lower}', version='{ver}'"
    
    # Substring matching - ORANGE
    orange_products = []
    for oname in orange:
        if prod_string.lower() in oname.lower():
            orange_products.append(oname)
    
    if len(orange_products) > 0:
        shortest_name = detect_shortest_string(orange_products, prod_string_lower)
        orange_product_versions = [i.lower() for i in orange[shortest_name]]
        
        # Try all normalized version formats
        for ver in versions_to_try:
            if ver in orange_product_versions:
                return "orange", "substring", f"Substring match: found '{prod_string_lower}' in '{shortest_name}', version='{ver}'"
        
        # Major.minor matching
        if prod_string_lower in shortest_name.lower():
            for detected_version in orange_product_versions:
                if '.' in detected_version and '.' in version:
                    if version.split('.')[0:2] == detected_version.split('.')[0:2]:
                        return 'orange', 'major.minor', f"Major.minor match: '{version}' matches '{detected_version}' in '{shortest_name}'"
        
        # Wildcard matching
        for i in orange_product_versions:
            if 'x' in i:
                prod_name = i.replace('x', '[0-9]+')
                if re.search(prod_name, version):
                    return "orange", "wildcard", f"Wildcard match: version '{version}' matches pattern '{i}' in '{shortest_name}'"
                elif version == i.replace('.x', ''):
                    return "orange", "wildcard", f"Wildcard match: version '{version}' matches '{i}' (without .x) in '{shortest_name}'"
                elif ('.x.x' in i) and ('.' in version):
                    versions_split = i.split('.x')
                    provided_versions_split = version.split('.')
                    if versions_split[0] == provided_versions_split[0]:
                        return 'orange', 'wildcard', f"Wildcard match: major version '{provided_versions_split[0]}' matches '{i}' in '{shortest_name}'"
    
    # Substring matching - RED
    red_products = []
    for rname in red:
        if prod_string.lower() in rname.lower():
            red_products.append(rname)
    
    if len(red_products) > 0:
        shortest_name = detect_shortest_string(red_products, prod_string_lower)
        red_product_versions = [i.lower() for i in red[shortest_name]]
        
        # Try all normalized version formats
        for ver in versions_to_try:
            if ver in red_product_versions:
                return "red", "substring", f"Substring match: found '{prod_string_lower}' in '{shortest_name}', version='{ver}'"
        
        # Major.minor matching
        if prod_string_lower in shortest_name.lower():
            for detected_version in red_product_versions:
                if '.' in detected_version and '.' in version:
                    if version.split('.')[0:2] == detected_version.split('.')[0:2]:
                        return 'red', 'major.minor', f"Major.minor match: '{version}' matches '{detected_version}' in '{shortest_name}'"
        
        # Wildcard matching
        for i in red_product_versions:
            if 'x' in i:
                prod_name = i.replace('x', '[0-9]+')
                if re.search(prod_name, version):
                    return "red", "wildcard", f"Wildcard match: version '{version}' matches pattern '{i}' in '{shortest_name}'"
                elif version == i.replace('.x', ''):
                    return "red", "wildcard", f"Wildcard match: version '{version}' matches '{i}' (without .x) in '{shortest_name}'"
                elif ('.x.x' in i) and ('.' in version):
                    versions_split = i.split('.x')
                    provided_versions_split = version.split('.')
                    if versions_split[0] == provided_versions_split[0]:
                        return 'red', 'wildcard', f"Wildcard match: major version '{provided_versions_split[0]}' matches '{i}' in '{shortest_name}'"
    
    # Substring matching - GREEN
    green_products = []
    for gname in green:
        if prod_string.lower() in gname.lower():
            green_products.append(gname)
    
    if len(green_products) > 0:
        shortest_name = detect_shortest_string(green_products, prod_string_lower)
        green_product_versions = [i.lower() for i in green[shortest_name]]
        
        # Try all normalized version formats
        for ver in versions_to_try:
            if ver in green_product_versions:
                return "green", "substring", f"Substring match: found '{prod_string_lower}' in '{shortest_name}', version='{ver}'"
        
        # Major.minor matching
        if prod_string_lower in shortest_name.lower():
            for detected_version in green_product_versions:
                if '.' in detected_version and '.' in version:
                    if version.split('.')[0:2] == detected_version.split('.')[0:2]:
                        return 'green', 'major.minor', f"Major.minor match: '{version}' matches '{detected_version}' in '{shortest_name}'"
        
        # Wildcard matching
        for i in green_product_versions:
            if 'x' in i:
                prod_name = i.replace('x', '[0-9]+')
                if re.search(prod_name, version):
                    return "green", "wildcard", f"Wildcard match: version '{version}' matches pattern '{i}' in '{shortest_name}'"
                elif version == i.replace('.x', ''):
                    return "green", "wildcard", f"Wildcard match: version '{version}' matches '{i}' (without .x) in '{shortest_name}'"
                elif ('.x.x' in i) and ('.' in version):
                    versions_split = i.split('.x')
                    provided_versions_split = version.split('.')
                    if versions_split[0] == provided_versions_split[0]:
                        return 'green', 'wildcard', f"Wildcard match: major version '{provided_versions_split[0]}' matches '{i}' in '{shortest_name}'"
    
    # No match found
    return "blue", "no_match", f"No match found for product '{prod_string}' (mapped from '{original_product}'), version '{version}'"


def generate_reports(data_file):
    """
    Main function to generate all three reports.
    """
    print("\n" + "="*80)
    print("LIFECYCLE MATCH REPORT GENERATOR")
    print("="*80)
    print(f"Data file: {data_file}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # Load lifecycle dictionaries
    red, orange, green = load_lifecycle_dictionaries()
    
    # Load May 2026 data
    print("\nLoading May 2026 data...")
    try:
        df = pd.read_csv(data_file, low_memory=False)
        print(f"✓ Loaded {len(df):,} records")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return
    
    # Get unique product/version combinations
    print("\nAnalyzing unique product/version combinations...")
    unique_combos = df[['Product Name', 'Product Version']].drop_duplicates()
    print(f"✓ Found {len(unique_combos):,} unique combinations")
    
    # Analyze each combination
    results = []
    total = len(unique_combos)
    
    print("\nProcessing combinations...")
    for idx, row in unique_combos.iterrows():
        if (idx + 1) % 100 == 0:
            progress = (idx + 1) / total * 100
            print(f"  Progress: {idx + 1:,}/{total:,} ({progress:.1f}%)")
        
        product_name = row['Product Name']
        product_version = row['Product Version']
        
        # Get mapped product name
        mapped_product = get_mapped_product_name(product_name)
        
        # Calculate color with detailed tracking
        color, match_type, match_details = calc_color_detailed(
            product_name, product_version, red, orange, green
        )
        
        results.append({
            'Product Name': product_name,
            'Product Version': str(product_version),
            'Mapped Product Name': mapped_product,
            'Lifecycle Color': color,
            'Match Type': match_type,
            'Match Details': match_details
        })
    
    print(f"✓ Processed all {total:,} combinations\n")
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Generate detailed results CSV
    output_file = 'lifecycle_match_results.csv'
    print(f"Generating {output_file}...")
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✓ Saved {len(results_df):,} results to {output_file}")
    
    # Generate summary by color
    summary_file = 'lifecycle_summary_by_color.csv'
    print(f"\nGenerating {summary_file}...")
    
    summary_data = []
    for color in ['red', 'orange', 'green', 'blue']:
        color_df = results_df[results_df['Lifecycle Color'] == color]
        
        # Count by match type
        match_type_counts = color_df['Match Type'].value_counts().to_dict()
        
        summary_data.append({
            'Color': color.upper(),
            'Total Count': len(color_df),
            'Percentage': f"{len(color_df) / len(results_df) * 100:.1f}%",
            'Exact Matches': match_type_counts.get('exact', 0),
            'Substring Matches': match_type_counts.get('substring', 0),
            'Wildcard Matches': match_type_counts.get('wildcard', 0),
            'Major.Minor Matches': match_type_counts.get('major.minor', 0),
            'SaaS Matches': match_type_counts.get('saas', 0),
            'No Matches': match_type_counts.get('no_match', 0)
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
    print(f"✓ Saved summary to {summary_file}")
    
    # Generate markdown report
    md_file = 'LIFECYCLE_MATCH_REPORT.md'
    print(f"\nGenerating {md_file}...")
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Lifecycle Match Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Data Source:** {data_file}\n\n")
        f.write(f"**Total Unique Product/Version Combinations:** {len(results_df):,}\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write("| Color | Count | Percentage | Description |\n")
        f.write("|-------|-------|------------|-------------|\n")
        
        color_descriptions = {
            'RED': 'End of Support (EOS) - Products that have reached end of support',
            'ORANGE': 'Approaching EOS - Products approaching end of support within 12 months',
            'GREEN': 'Supported - Products with active support',
            'BLUE': 'Unknown/No Match - Products not found in lifecycle dictionaries'
        }
        
        for _, row in summary_df.iterrows():
            color = row['Color']
            f.write(f"| **{color}** | {row['Total Count']:,} | {row['Percentage']} | {color_descriptions[color]} |\n")
        
        f.write("\n## Match Type Breakdown\n\n")
        f.write("| Color | Exact | Substring | Wildcard | Major.Minor | SaaS | No Match |\n")
        f.write("|-------|-------|-----------|----------|-------------|------|----------|\n")
        
        for _, row in summary_df.iterrows():
            f.write(f"| **{row['Color']}** | {row['Exact Matches']} | {row['Substring Matches']} | "
                   f"{row['Wildcard Matches']} | {row['Major.Minor Matches']} | "
                   f"{row['SaaS Matches']} | {row['No Matches']} |\n")
        
        f.write("\n## Match Type Definitions\n\n")
        f.write("- **Exact**: Product name and version match exactly in lifecycle dictionary\n")
        f.write("- **Substring**: Product name found as substring in lifecycle dictionary key\n")
        f.write("- **Wildcard**: Version matches using wildcard patterns (e.g., 7.1.x)\n")
        f.write("- **Major.Minor**: Version matches on major.minor version numbers only\n")
        f.write("- **SaaS**: Product identified as SaaS (version matching not applicable)\n")
        f.write("- **No Match**: No matching product/version found in any lifecycle dictionary\n")
        
        # Add sample of blue (no match) products
        blue_df = results_df[results_df['Lifecycle Color'] == 'blue']
        if len(blue_df) > 0:
            f.write("\n## Sample of Unmatched Products (Blue)\n\n")
            f.write("These products were not found in the lifecycle dictionaries:\n\n")
            f.write("| Product Name | Version | Mapped Product Name |\n")
            f.write("|--------------|---------|---------------------|\n")
            
            # Show up to 20 examples
            for _, row in blue_df.head(20).iterrows():
                prod = row['Product Name'][:50]  # Truncate long names
                ver = str(row['Product Version'])[:20]
                mapped = row['Mapped Product Name'][:50]
                f.write(f"| {prod} | {ver} | {mapped} |\n")
            
            if len(blue_df) > 20:
                f.write(f"\n*...and {len(blue_df) - 20:,} more unmatched products*\n")
        
        f.write("\n## Files Generated\n\n")
        f.write("1. **lifecycle_match_results.csv** - Detailed results for every product/version combination\n")
        f.write("2. **lifecycle_summary_by_color.csv** - Summary statistics by lifecycle color\n")
        f.write("3. **LIFECYCLE_MATCH_REPORT.md** - This human-readable report\n")
        
        f.write("\n## Next Steps\n\n")
        f.write("1. Review the blue (unmatched) products in `lifecycle_match_results.csv`\n")
        f.write("2. Add missing product name mappings to `product_name_mappings.py`\n")
        f.write("3. Verify that lifecycle dictionaries contain all expected products\n")
        f.write("4. Re-run this script after making updates to see improvements\n")
        
        f.write("\n---\n")
        f.write("*Generated by generate_lifecycle_match_report.py*\n")
    
    print(f"✓ Saved markdown report to {md_file}")
    
    # Print summary to console
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(summary_df.to_string(index=False))
    print("="*80)
    
    print("\n✓ All reports generated successfully!")
    print(f"\nFiles created:")
    print(f"  1. {output_file}")
    print(f"  2. {summary_file}")
    print(f"  3. {md_file}")


if __name__ == "__main__":
    # Set encoding for Windows console
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    # Run the report generator
    data_file = '../Files/2026/May/May_2026_merged.csv'
    
    try:
        generate_reports(data_file)
    except KeyboardInterrupt:
        print("\n\n✗ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
