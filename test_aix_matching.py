import json
from product_name_mappings import get_mapped_product_name, normalize_version

# Load lifecycle dictionaries
with open('../Files/2026/Product Lifecycle/Red_dict_May_26_final.json', 'r') as f:
    red_dict = json.load(f)
with open('../Files/2026/Product Lifecycle/Orange_dict_May_26_final.json', 'r') as f:
    orange_dict = json.load(f)
with open('../Files/2026/Product Lifecycle/Green_dict_May_26_final.json', 'r') as f:
    green_dict = json.load(f)

# Test AIX versions from ticket data
test_cases = [
    ('AIX', '7.2'),
    ('AIX', '7.3'),
    ('AIX', '7.1 (EOS 4/30/2023)'),
    ('AIX', '6.1 (EOS 4/30/2017)'),
]

print('Testing AIX version matching:')
print('=' * 80)
for product, version in test_cases:
    mapped_product = get_mapped_product_name(product)
    prod_string = mapped_product.lower()
    version_clean = str(version).lower()
    
    # Check each dictionary
    color = 'Blue (N/A)'
    if prod_string in red_dict and version_clean in red_dict[prod_string]:
        color = 'Red'
    elif prod_string in orange_dict and version_clean in orange_dict[prod_string]:
        color = 'Orange'
    elif prod_string in green_dict and version_clean in green_dict[prod_string]:
        color = 'Green'
    
    print(f'Product: {product:30} Version: {version:25} -> {mapped_product}')
    print(f'  Lookup: prod="{prod_string}", ver="{version_clean}"')
    print(f'  Result: {color}')
    
    # Show what versions ARE in the dictionaries for this product
    if prod_string in green_dict:
        print(f'  Green versions available: {green_dict[prod_string][:5]}')
    if prod_string in orange_dict:
        print(f'  Orange versions available: {orange_dict[prod_string][:5]}')
    if prod_string in red_dict:
        print(f'  Red versions available: {red_dict[prod_string][:5]}')
    print()

# Made with Bob
