import json

with open('../Files/2026/Product Lifecycle/Orange_dict_May_26_final.json') as f:
    d = json.load(f)
    
print("Checking for 'AIX Standard Edition' in Orange dictionary:")
print(f"  Exact key 'AIX Standard Edition': {'AIX Standard Edition' in d}")
print(f"  Lowercase key 'aix standard edition': {'aix standard edition' in d}")

print("\nAll AIX-related keys in Orange:")
for k in sorted(d.keys()):
    if 'aix' in k.lower() and 'standard' in k.lower():
        print(f"  '{k}': {d[k]}")

# Made with Bob
