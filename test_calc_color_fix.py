import sys
import json
import pandas as pd

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import the mapping functions
from product_name_mappings import get_mapped_product_name, normalize_version

# Load lifecycle dictionaries (simulating what app.py does)
with open('../Files/2026/Product Lifecycle/Red_dict_May_26_final.json', 'r') as f:
    red = json.load(f)
with open('../Files/2026/Product Lifecycle/Orange_dict_May_26_final.json', 'r') as f:
    orange = json.load(f)
with open('../Files/2026/Product Lifecycle/Green_dict_May_26_final.json', 'r') as f:
    green = json.load(f)

# Simplified calc_color function with our fix
def calc_color_fixed(product_name, product_version):
    """Test version of calc_color with normalization fix"""
    # Apply product name mapping
    mapped_product = get_mapped_product_name(product_name)
    prod_string = mapped_product  # Keep original case for dictionary lookup
    version_raw = str(product_version)
    
    # Normalize version to try multiple formats
    versions_to_try = normalize_version(version_raw)
    
    print(f"  Product: {product_name} -> {mapped_product}")
    print(f"  Version: {product_version}")
    print(f"  Normalized versions to try: {versions_to_try}")
    
    # Check if version is null/empty
    if version_raw in [None, " ", "", "NaN", "nan", "None"]:
        return "blue"
    
    # Try exact product name match with all normalized version formats
    if prod_string in red:
        print(f"  Found '{prod_string}' in RED dict with versions: {red[prod_string][:5]}")
        for ver in versions_to_try:
            if ver in red[prod_string]:
                print(f"  MATCH! Version '{ver}' found in RED")
                return "red"
    
    if prod_string in orange:
        print(f"  Found '{prod_string}' in ORANGE dict with versions: {orange[prod_string][:5]}")
        for ver in versions_to_try:
            if ver in orange[prod_string]:
                print(f"  MATCH! Version '{ver}' found in ORANGE")
                return "orange"
    
    if prod_string in green:
        print(f"  Found '{prod_string}' in GREEN dict with versions: {green[prod_string][:5]}")
        for ver in versions_to_try:
            if ver in green[prod_string]:
                print(f"  MATCH! Version '{ver}' found in GREEN")
                return "green"
    
    print(f"  X NO MATCH - returning blue")
    return "blue"

# Test AIX versions from ticket data
test_cases = [
    ('AIX', '7.2'),
    ('AIX', '7.3'),
    ('AIX', '7.1 (EOS 4/30/2023)'),
    ('AIX', '6.1 (EOS 4/30/2017)'),
]

print('Testing AIX version matching with FIXED calc_color:')
print('=' * 80)
for product, version in test_cases:
    print(f'\nTest: {product} version {version}')
    print('-' * 80)
    color = calc_color_fixed(product, version)
    print(f'  RESULT: {color.upper()}')

# Made with Bob
