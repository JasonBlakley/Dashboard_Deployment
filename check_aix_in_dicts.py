import json

for color in ['Orange', 'Red']:
    with open(f'../Files/2026/Product Lifecycle/{color}_dict_May_26_final.json') as f:
        d = json.load(f)
        aix_keys = [k for k in d.keys() if 'aix' in k.lower()]
        print(f'\nAIX-related keys in {color} dictionary:')
        for k in sorted(aix_keys)[:10]:
            print(f'  - {k}: {d[k][:5]}')

# Made with Bob
