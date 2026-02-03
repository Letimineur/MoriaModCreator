"""
Rebuild JSON files from .def files and compare with originals.

This script reads the .def files from AppData, extracts the JSON objects,
rebuilds the original DT_ConstructionRecipes.json and DT_Constructions.json files,
and compares them with the originals to verify they match exactly.

Usage:
    python helpers/rebuild_and_compare.py
"""

import json
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def get_def_files_dir() -> Path:
    """Get the .def files directory in AppData."""
    appdata = os.environ.get('APPDATA')
    if not appdata:
        appdata = Path.home() / 'AppData' / 'Roaming'
    return Path(appdata) / 'MoriaMODCreator' / 'Definitions' / 'Building' / 'New Objects'


def load_json_file(filepath: Path) -> dict:
    """Load and parse a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(filepath: Path, data: dict):
    """Save data to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def extract_json_from_def(def_path: Path) -> tuple[dict, dict]:
    """Extract recipe and construction JSON from a .def file.
    
    Returns:
        Tuple of (recipe_json, construction_json)
    """
    with open(def_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse XML
    root = ET.fromstring(content)
    
    recipe_json = None
    construction_json = None
    
    for mod in root.findall('mod'):
        file_path = mod.get('file', '')
        add_row = mod.find('add_row')
        
        if add_row is not None and add_row.text:
            json_text = add_row.text.strip()
            json_obj = json.loads(json_text)
            
            if 'DT_ConstructionRecipes.json' in file_path:
                recipe_json = json_obj
            elif 'DT_Constructions.json' in file_path:
                construction_json = json_obj
    
    return recipe_json, construction_json


def compare_json_objects(obj1, obj2, path="") -> list[str]:
    """Recursively compare two JSON objects and return differences."""
    differences = []
    
    if type(obj1) != type(obj2):
        differences.append(f"{path}: type mismatch - {type(obj1).__name__} vs {type(obj2).__name__}")
        return differences
    
    if isinstance(obj1, dict):
        keys1 = set(obj1.keys())
        keys2 = set(obj2.keys())
        
        for key in keys1 - keys2:
            differences.append(f"{path}.{key}: missing in rebuilt")
        for key in keys2 - keys1:
            differences.append(f"{path}.{key}: extra in rebuilt")
        
        for key in keys1 & keys2:
            differences.extend(compare_json_objects(obj1[key], obj2[key], f"{path}.{key}"))
    
    elif isinstance(obj1, list):
        if len(obj1) != len(obj2):
            differences.append(f"{path}: list length mismatch - {len(obj1)} vs {len(obj2)}")
        else:
            for i, (item1, item2) in enumerate(zip(obj1, obj2)):
                differences.extend(compare_json_objects(item1, item2, f"{path}[{i}]"))
    
    else:
        if obj1 != obj2:
            differences.append(f"{path}: value mismatch - {repr(obj1)} vs {repr(obj2)}")
    
    return differences


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    test_dir = project_dir / 'test'
    output_dir = project_dir / 'test_rebuild'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load original files
    print("Loading original files...")
    original_recipes_path = test_dir / 'DT_ConstructionRecipes.json'
    original_constructions_path = test_dir / 'DT_Constructions.json'
    
    original_recipes = load_json_file(original_recipes_path)
    original_constructions = load_json_file(original_constructions_path)
    
    original_recipe_data = original_recipes['Exports'][0]['Table']['Data']
    original_construction_data = original_constructions['Exports'][0]['Table']['Data']
    
    print(f"  Original recipes: {len(original_recipe_data)}")
    print(f"  Original constructions: {len(original_construction_data)}")
    
    # Build lookup by name for originals
    original_recipe_by_name = {r['Name']: r for r in original_recipe_data}
    original_construction_by_name = {c['Name']: c for c in original_construction_data}
    
    # Read all .def files and extract JSON
    def_dir = get_def_files_dir()
    def_files = list(def_dir.glob('*.def'))
    print(f"\nReading {len(def_files)} .def files from {def_dir}...")
    
    rebuilt_recipes = []
    rebuilt_constructions = []
    
    for def_file in sorted(def_files):
        try:
            recipe, construction = extract_json_from_def(def_file)
            if recipe:
                rebuilt_recipes.append(recipe)
            if construction:
                rebuilt_constructions.append(construction)
        except Exception as e:
            print(f"  ERROR parsing {def_file.name}: {e}")
    
    print(f"  Extracted {len(rebuilt_recipes)} recipes")
    print(f"  Extracted {len(rebuilt_constructions)} constructions")
    
    # Build lookup by name for rebuilt
    rebuilt_recipe_by_name = {r['Name']: r for r in rebuilt_recipes}
    rebuilt_construction_by_name = {c['Name']: c for c in rebuilt_constructions}
    
    # Compare recipes
    print("\n=== Comparing Recipes ===")
    recipe_differences = []
    
    # Check for missing/extra recipes
    original_recipe_names = set(original_recipe_by_name.keys())
    rebuilt_recipe_names = set(rebuilt_recipe_by_name.keys())
    
    missing_recipes = original_recipe_names - rebuilt_recipe_names
    extra_recipes = rebuilt_recipe_names - original_recipe_names
    
    if missing_recipes:
        print(f"  Missing recipes: {len(missing_recipes)}")
        for name in sorted(missing_recipes):
            recipe_differences.append(f"Missing recipe: {name}")
    
    if extra_recipes:
        print(f"  Extra recipes: {len(extra_recipes)}")
        for name in sorted(extra_recipes):
            recipe_differences.append(f"Extra recipe: {name}")
    
    # Compare matching recipes
    matching_recipes = original_recipe_names & rebuilt_recipe_names
    print(f"  Comparing {len(matching_recipes)} matching recipes...")
    
    for name in sorted(matching_recipes):
        orig = original_recipe_by_name[name]
        rebuilt = rebuilt_recipe_by_name[name]
        diffs = compare_json_objects(orig, rebuilt, name)
        recipe_differences.extend(diffs)
    
    # Compare constructions
    print("\n=== Comparing Constructions ===")
    construction_differences = []
    
    # Check for missing/extra constructions
    original_construction_names = set(original_construction_by_name.keys())
    rebuilt_construction_names = set(rebuilt_construction_by_name.keys())
    
    missing_constructions = original_construction_names - rebuilt_construction_names
    extra_constructions = rebuilt_construction_names - original_construction_names
    
    if missing_constructions:
        print(f"  Missing constructions: {len(missing_constructions)}")
        for name in sorted(missing_constructions):
            construction_differences.append(f"Missing construction: {name}")
    
    if extra_constructions:
        print(f"  Extra constructions: {len(extra_constructions)}")
        for name in sorted(extra_constructions):
            construction_differences.append(f"Extra construction: {name}")
    
    # Compare matching constructions
    matching_constructions = original_construction_names & rebuilt_construction_names
    print(f"  Comparing {len(matching_constructions)} matching constructions...")
    
    for name in sorted(matching_constructions):
        orig = original_construction_by_name[name]
        rebuilt = rebuilt_construction_by_name[name]
        diffs = compare_json_objects(orig, rebuilt, name)
        construction_differences.extend(diffs)
    
    # Report results
    print("\n" + "=" * 60)
    
    all_differences = recipe_differences + construction_differences
    
    if not all_differences:
        print("SUCCESS! All JSON objects match exactly.")
        
        # Save rebuilt files anyway for reference
        rebuilt_recipes_full = original_recipes.copy()
        rebuilt_recipes_full['Exports'][0]['Table']['Data'] = rebuilt_recipes
        save_json_file(output_dir / 'DT_ConstructionRecipes_rebuilt.json', rebuilt_recipes_full)
        
        rebuilt_constructions_full = original_constructions.copy()
        rebuilt_constructions_full['Exports'][0]['Table']['Data'] = rebuilt_constructions
        save_json_file(output_dir / 'DT_Constructions_rebuilt.json', rebuilt_constructions_full)
        
        print(f"\nRebuilt files saved to: {output_dir}")
    else:
        print(f"DIFFERENCES FOUND: {len(all_differences)}")
        print("\nFirst 20 differences:")
        for diff in all_differences[:20]:
            print(f"  - {diff}")
        
        if len(all_differences) > 20:
            print(f"\n  ... and {len(all_differences) - 20} more differences")
        
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
