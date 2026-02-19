"""
Free Building Helper - Generate .def files that set all material counts to 0.

Reads DT_ConstructionRecipes.json from both the game output and Secrets cache,
and creates two .def files:
  1. Free Building.def - covers all 814 base game recipes
  2. Free Building Secrets.def - covers the 179 Secrets-only recipes

Usage:
    python helpers/freebuildinghelper.py

Output:
    %AppData%/MoriaMODCreator/Definitions/Building/Free Building.def
    %AppData%/MoriaMODCreator/Definitions/Building/Free Building Secrets.def
"""

import json
import os
from pathlib import Path


def get_appdata_dir() -> Path:
    """Get the MoriaMODCreator AppData directory."""
    appdata = os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming'))
    return Path(appdata) / 'MoriaMODCreator'


def get_jsondata_dir() -> Path:
    """Get the jsondata output directory from AppData."""
    return get_appdata_dir() / 'output' / 'jsondata'


def get_secrets_cache_dir() -> Path:
    """Get the Secrets cache directory from AppData."""
    return get_appdata_dir() / 'cache' / 'secrets' / 'buildings'


def get_output_dir() -> Path:
    """Get the Definitions output directory in AppData."""
    output_dir = get_appdata_dir() / 'Definitions' / 'Building'
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def load_json_file(filepath: Path) -> dict:
    """Load and parse a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_property(value_list: list, prop_name: str):
    """Find a property by name in a Value array."""
    for prop in value_list:
        if prop.get('Name') == prop_name:
            return prop
    return None


def count_materials(row: dict) -> int:
    """Count how many materials a recipe row has."""
    materials_prop = find_property(row.get('Value', []), 'DefaultRequiredMaterials')
    if not materials_prop:
        return 0
    materials = materials_prop.get('Value', [])
    return len(materials)


def get_material_info(material_entry: dict) -> tuple:
    """Extract material name and count from a material entry.

    Returns (material_name, count) tuple.
    """
    material_name = "Unknown"
    count_val = 0

    value_list = material_entry.get('Value', [])

    # Get MaterialHandle.RowName
    handle = find_property(value_list, 'MaterialHandle')
    if handle:
        row_name_prop = find_property(handle.get('Value', []), 'RowName')
        if row_name_prop:
            material_name = row_name_prop.get('Value', 'Unknown')

    # Get Count
    count_prop = find_property(value_list, 'Count')
    if count_prop:
        count_val = count_prop.get('Value', 0)

    return material_name, count_val


def build_changes(rows, filter_names=None):
    """Build change entries for the given rows.

    Args:
        rows: List of recipe row dicts from the JSON.
        filter_names: If set, only include rows whose Name is in this set.

    Returns:
        (changes, total_materials, skipped_rows) tuple.
    """
    changes = []
    total_materials = 0
    skipped_rows = 0

    for row in rows:
        row_name = row.get('Name', '')
        if not row_name:
            continue

        if filter_names is not None and row_name not in filter_names:
            continue

        materials_prop = find_property(row.get('Value', []), 'DefaultRequiredMaterials')
        if not materials_prop:
            skipped_rows += 1
            continue

        materials = materials_prop.get('Value', [])
        if not materials:
            skipped_rows += 1
            continue

        for idx, material in enumerate(materials):
            mat_name, mat_count = get_material_info(material)
            comment = f"    <!-- {row_name}: {mat_name} (was {mat_count}) -->"
            change = (f'    <change item="{row_name}" '
                      f'property="DefaultRequiredMaterials[{idx}].Count" '
                      f'value="0" />')
            changes.append(comment)
            changes.append(change)
            total_materials += 1

    return changes, total_materials, skipped_rows


def write_def_file(output_path, title, recipe_count, changes, total_materials):
    """Write a .def file with the given changes."""
    changes_block = '\n'.join(changes)
    def_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<definition>
  <title>{title}</title>
  <author>Moria MOD Creator</author>
  <description>Sets all material counts to 0 for {recipe_count} construction recipes ({total_materials} material entries)</description>
  <mod file="Moria\\Content\\Tech\\Data\\Building\\DT_ConstructionRecipes.json">
{changes_block}
  </mod>
</definition>
'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(def_content)


def main():
    """Main entry point."""
    output_dir = get_output_dir()

    # --- 1. Base game: Free Building.def ---
    jsondata_dir = get_jsondata_dir()
    recipes_path = (jsondata_dir / 'Moria' / 'Content' / 'Tech' / 'Data'
                    / 'Building' / 'DT_ConstructionRecipes.json')

    if not recipes_path.exists():
        print(f"ERROR: Could not find {recipes_path}")
        print("Make sure the game data has been extracted to the jsondata directory.")
        return

    print(f"Loading game recipes: {recipes_path}...")
    game_data = load_json_file(recipes_path)
    game_rows = game_data['Exports'][0]['Table']['Data']
    game_names = {r['Name'] for r in game_rows}
    print(f"  Found {len(game_rows)} recipe rows")

    changes, total_materials, skipped_rows = build_changes(game_rows)
    recipe_count = len(game_rows) - skipped_rows

    print(f"  {total_materials} material entries across {recipe_count} recipes")
    print(f"  Skipped {skipped_rows} rows with no materials")

    game_def_path = output_dir / 'Free Building.def'
    write_def_file(game_def_path, 'Free Building - All Construction Costs Zero',
                   recipe_count, changes, total_materials)
    print(f"  Generated: {game_def_path}")

    # --- 2. Secrets-only: Free Building Secrets.def ---
    secrets_path = get_secrets_cache_dir() / 'DT_ConstructionRecipes.json'

    if not secrets_path.exists():
        print(f"\nWARNING: Secrets cache not found at {secrets_path}")
        print("Skipping Secrets .def generation.")
        return

    print(f"\nLoading Secrets recipes: {secrets_path}...")
    secrets_data = load_json_file(secrets_path)
    secrets_rows = secrets_data['Exports'][0]['Table']['Data']
    secrets_names = {r['Name'] for r in secrets_rows}
    new_names = secrets_names - game_names
    print(f"  Found {len(secrets_rows)} total rows, {len(new_names)} Secrets-only")

    changes, total_materials, skipped_rows = build_changes(secrets_rows,
                                                           filter_names=new_names)
    recipe_count = len(new_names) - skipped_rows

    print(f"  {total_materials} material entries across {recipe_count} recipes")
    print(f"  Skipped {skipped_rows} rows with no materials")

    secrets_def_path = output_dir / 'Free Building Secrets.def'
    write_def_file(secrets_def_path,
                   'Free Building Secrets - All Secrets Construction Costs Zero',
                   recipe_count, changes, total_materials)
    print(f"  Generated: {secrets_def_path}")

    print("\nDone!")


if __name__ == '__main__':
    main()
