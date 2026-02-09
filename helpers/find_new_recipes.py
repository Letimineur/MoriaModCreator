"""Find NEW recipes and constructions that exist in Secrets but not in base game."""

import json
from pathlib import Path
import os

appdata = Path(os.environ['APPDATA']) / 'MoriaMODCreator'

# Paths - Recipes
secret_recipe_path = appdata / 'Secrets Source' / 'jsondata' / 'Moria' / 'Content' / 'Tech' / 'Data' / 'Building' / 'DT_ConstructionRecipes.json'
game_recipe_path = appdata / 'output' / 'jsondata' / 'Moria' / 'Content' / 'Tech' / 'Data' / 'Building' / 'DT_ConstructionRecipes.json'

# Paths - Constructions
secret_construction_path = appdata / 'Secrets Source' / 'jsondata' / 'Moria' / 'Content' / 'Tech' / 'Data' / 'Building' / 'DT_Constructions.json'
game_construction_path = appdata / 'output' / 'jsondata' / 'Moria' / 'Content' / 'Tech' / 'Data' / 'Building' / 'DT_Constructions.json'


def get_names_from_table(json_path):
    """Extract names from Exports[0].Table.Data[*].Name"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    names = set()
    exports = data.get('Exports', [])
    if exports:
        table = exports[0].get('Table', {})
        rows = table.get('Data', [])
        for row in rows:
            row_name = row.get('Name')
            if row_name:
                names.add(row_name)
    
    return names


print("=" * 60)
print("RECIPES")
print("=" * 60)

secret_recipe_names = get_names_from_table(secret_recipe_path)
game_recipe_names = get_names_from_table(game_recipe_path)

print(f"Secret Recipe count: {len(secret_recipe_names)}")
print(f"Game Recipe count: {len(game_recipe_names)}")

new_recipes = secret_recipe_names - game_recipe_names
print(f"NEW recipes: {len(new_recipes)}")

print()
print("=" * 60)
print("CONSTRUCTIONS")
print("=" * 60)

secret_construction_names = get_names_from_table(secret_construction_path)
game_construction_names = get_names_from_table(game_construction_path)

print(f"Secret Construction count: {len(secret_construction_names)}")
print(f"Game Construction count: {len(game_construction_names)}")

new_constructions = secret_construction_names - game_construction_names
print(f"NEW constructions: {len(new_constructions)}")

print()
print("=" * 60)
print("COMPARISON: NEW Recipes vs NEW Constructions")
print("=" * 60)

# Items in recipes but NOT in constructions
recipes_only = new_recipes - new_constructions
print(f"\nIn NEW Recipes but NOT in NEW Constructions: {len(recipes_only)}")
if recipes_only:
    for name in sorted(recipes_only):
        print(f"  - {name}")

# Items in constructions but NOT in recipes
constructions_only = new_constructions - new_recipes
print(f"\nIn NEW Constructions but NOT in NEW Recipes: {len(constructions_only)}")
if constructions_only:
    for name in sorted(constructions_only):
        print(f"  - {name}")

# Items in BOTH
matching = new_recipes & new_constructions
print(f"\nMatching in BOTH: {len(matching)}")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"NEW Recipes: {len(new_recipes)}")
print(f"NEW Constructions: {len(new_constructions)}")
print(f"Matching: {len(matching)}")
print(f"Recipes only: {len(recipes_only)}")
print(f"Constructions only: {len(constructions_only)}")
