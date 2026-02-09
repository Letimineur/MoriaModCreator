"""Analyze the JSON structure of Secrets recipe and construction files."""

import json
from pathlib import Path
import os

appdata = Path(os.environ['APPDATA']) / 'MoriaMODCreator'
secret_recipe_path = appdata / 'Secrets Source' / 'jsondata' / 'Moria' / 'Content' / 'Tech' / 'Data' / 'Building' / 'DT_ConstructionRecipes.json'
secret_construction_path = appdata / 'Secrets Source' / 'jsondata' / 'Moria' / 'Content' / 'Tech' / 'Data' / 'Building' / 'DT_Constructions.json'


def extract_fields_from_value(value_list):
    """Extract field names and their values from a Value list."""
    fields = {}
    for item in value_list:
        name = item.get('Name')
        if not name:
            continue
        
        item_type = item.get('$type', '')
        
        # Handle different property types
        if 'BoolPropertyData' in item_type:
            fields[name] = {'type': 'bool', 'value': item.get('Value')}
        elif 'EnumPropertyData' in item_type:
            fields[name] = {'type': 'enum', 'value': item.get('Value'), 'enum_type': item.get('EnumType')}
        elif 'IntPropertyData' in item_type:
            fields[name] = {'type': 'int', 'value': item.get('Value')}
        elif 'FloatPropertyData' in item_type:
            fields[name] = {'type': 'float', 'value': item.get('Value')}
        elif 'NamePropertyData' in item_type:
            fields[name] = {'type': 'name', 'value': item.get('Value')}
        elif 'StrPropertyData' in item_type:
            fields[name] = {'type': 'string', 'value': item.get('Value')}
        elif 'TextPropertyData' in item_type:
            fields[name] = {'type': 'text', 'value': item.get('Value')}
        elif 'ArrayPropertyData' in item_type:
            array_val = item.get('Value', [])
            fields[name] = {'type': 'array', 'count': len(array_val), 'value': array_val}
        elif 'StructPropertyData' in item_type:
            struct_val = item.get('Value', [])
            nested = extract_fields_from_value(struct_val) if isinstance(struct_val, list) else {}
            fields[name] = {'type': 'struct', 'struct_type': item.get('StructType'), 'nested': nested}
        elif 'SoftObjectPropertyData' in item_type:
            fields[name] = {'type': 'soft_object', 'value': item.get('Value')}
        elif 'ObjectPropertyData' in item_type:
            fields[name] = {'type': 'object', 'value': item.get('Value')}
        else:
            fields[name] = {'type': 'unknown', 'raw_type': item_type, 'value': item.get('Value')}
    
    return fields


# Load recipe file
with open(secret_recipe_path, 'r', encoding='utf-8') as f:
    recipe_data = json.load(f)

exports = recipe_data.get('Exports', [])
table = exports[0].get('Table', {})
rows = table.get('Data', [])

# Find a sample recipe
sample_recipe = None
for row in rows:
    if row.get('Name') == 'TobiPack_AleKeg':
        sample_recipe = row
        break

if sample_recipe:
    print("=" * 60)
    print("RECIPE FIELDS (TobiPack_AleKeg)")
    print("=" * 60)
    
    value_list = sample_recipe.get('Value', [])
    fields = extract_fields_from_value(value_list)
    
    for name, info in fields.items():
        if info['type'] == 'struct':
            print(f"\n{name} [{info['type']}] ({info.get('struct_type', '?')}):")
            for nested_name, nested_info in info.get('nested', {}).items():
                print(f"  - {nested_name}: {nested_info.get('value', '?')} ({nested_info['type']})")
        elif info['type'] == 'array':
            print(f"\n{name} [{info['type']}] count={info['count']}:")
            for i, arr_item in enumerate(info.get('value', [])[:3]):
                if isinstance(arr_item, dict) and 'Value' in arr_item:
                    nested = extract_fields_from_value(arr_item.get('Value', []))
                    print(f"  [{i}]: {nested}")
        else:
            print(f"{name}: {info.get('value', '?')} ({info['type']})")


# Load construction file
print("\n\n")
with open(secret_construction_path, 'r', encoding='utf-8') as f:
    construction_data = json.load(f)

exports = construction_data.get('Exports', [])
table = exports[0].get('Table', {})
rows = table.get('Data', [])

# Find a sample construction
sample_construction = None
for row in rows:
    if row.get('Name') == 'TobiPack_AleKeg':
        sample_construction = row
        break

if sample_construction:
    print("=" * 60)
    print("CONSTRUCTION FIELDS (TobiPack_AleKeg)")
    print("=" * 60)
    
    value_list = sample_construction.get('Value', [])
    fields = extract_fields_from_value(value_list)
    
    for name, info in fields.items():
        if info['type'] == 'struct':
            print(f"\n{name} [{info['type']}] ({info.get('struct_type', '?')}):")
            for nested_name, nested_info in info.get('nested', {}).items():
                print(f"  - {nested_name}: {nested_info.get('value', '?')} ({nested_info['type']})")
        elif info['type'] == 'array':
            print(f"\n{name} [{info['type']}] count={info['count']}:")
        elif info['type'] == 'text':
            val = info.get('value')
            if isinstance(val, dict):
                print(f"{name}: {val.get('CultureInvariantString', val)} ({info['type']})")
            else:
                print(f"{name}: {val} ({info['type']})")
        else:
            print(f"{name}: {info.get('value', '?')} ({info['type']})")
