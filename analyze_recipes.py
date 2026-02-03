import json

with open('test/DT_ConstructionRecipes.json', 'r') as f:
    d = json.load(f)

data = d['Exports'][0]['Table']['Data']

def get_materials(prop_value):
    mats = []
    for mat in prop_value:
        mat_name = None
        amount = 1
        for inner in mat.get('Value', []):
            if inner['Name'] == 'MaterialHandle':
                for v in inner.get('Value', []):
                    if v['Name'] == 'RowName':
                        mat_name = v['Value']
            if inner['Name'] == 'Amount':
                amount = inner['Value']
        if mat_name:
            mats.append((mat_name, amount))
    return mats

print("=== Sample Construction Recipes ===\n")
for i in range(15):
    item = data[i]
    name = item['Name']
    for prop in item['Value']:
        if prop['Name'] == 'DefaultRequiredMaterials':
            mats = get_materials(prop.get('Value', []))
            mats_str = ', '.join([f"{m[0]} x{m[1]}" for m in mats])
            print(f"{name}:")
            print(f"  Materials: {mats_str}")
            break

print("\n=== Looking at DT_Constructions ===\n")

with open('test/DT_Constructions.json', 'r') as f:
    d2 = json.load(f)

data2 = d2['Exports'][0]['Table']['Data']

for i in range(10):
    item = data2[i]
    name = item['Name']
    display_name = None
    tags = []
    actor = None
    
    for prop in item['Value']:
        if prop['Name'] == 'DisplayName':
            display_name = prop.get('Value', '')
        if prop['Name'] == 'Tags':
            for inner in prop.get('Value', []):
                if inner['Name'] == 'Tags':
                    tags = inner.get('Value', [])
        if prop['Name'] == 'Actor':
            val = prop.get('Value', {})
            if isinstance(val, dict):
                asset_path = val.get('AssetPath', {})
                actor = asset_path.get('AssetName', '')
    
    print(f"{name}:")
    print(f"  Display: {display_name}")
    print(f"  Tags: {tags}")
    print(f"  Actor: {actor}")
    print()
