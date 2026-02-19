"""
Free Building Helper - Generate .def files that set all material counts to 0.

Reads DT_ConstructionRecipes.json from both the base game output and the
Secrets cache, then creates two separate .def files:

  1. Free Building.def           - base game recipes (814 rows)
  2. Free Building Secrets.def   - Secrets-only recipes (179 rows)

Each .def file contains one <change> entry per material in every recipe,
setting its Count to 0 so the building costs nothing to construct.

JSON structure of each recipe row (UAssetAPI format):
    Row
      └─ DefaultRequiredMaterials  (ArrayPropertyData)
           └─ Value[]  (StructPropertyData: MorRequiredRecipeMaterial)
                ├─ MaterialHandle.RowName  (e.g., "Item.IronIngot")
                └─ Count                   (IntPropertyData, the build cost)

.def output format per material:
    <change item="RECIPE_NAME"
            property="DefaultRequiredMaterials[N].Count"
            value="0" />

Usage:
    python helpers/freebuildinghelper.py

Output:
    %AppData%/MoriaMODCreator/Definitions/Building/Free Building.def
    %AppData%/MoriaMODCreator/Definitions/Building/Free Building Secrets.def
"""

import json
import os
from pathlib import Path


# ---------------------------------------------------------------------------
#  Path helpers
# ---------------------------------------------------------------------------

def get_appdata_dir() -> Path:
    """Get the MoriaMODCreator AppData directory."""
    appdata = os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming'))
    return Path(appdata) / 'MoriaMODCreator'


def get_jsondata_dir() -> Path:
    """Get the jsondata output directory (base game extracted JSON)."""
    return get_appdata_dir() / 'output' / 'jsondata'


def get_secrets_cache_dir() -> Path:
    """Get the Secrets cache directory (Secrets-modded JSON)."""
    return get_appdata_dir() / 'cache' / 'secrets' / 'buildings'


def get_output_dir() -> Path:
    """Get the Definitions output directory; creates it if missing."""
    output_dir = get_appdata_dir() / 'Definitions' / 'Building'
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# ---------------------------------------------------------------------------
#  JSON parsing helpers
# ---------------------------------------------------------------------------

def load_json_file(filepath: Path) -> dict:
    """Load and parse a UAssetAPI-exported JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_property(value_list: list, prop_name: str):
    """Find a property dict by Name within a UAssetAPI Value array.

    Each element in value_list is a dict with at least {"Name": ...}.
    Returns the first match, or None.
    """
    for prop in value_list:
        if prop.get('Name') == prop_name:
            return prop
    return None


def get_material_info(material_entry: dict) -> tuple:
    """Extract material name and count from a single material struct.

    Navigates:  material -> MaterialHandle -> RowName  (material id)
                material -> Count                      (build quantity)

    Returns:
        (material_name, count) tuple, e.g. ("Item.IronIngot", 5)
    """
    material_name = "Unknown"
    count_val = 0

    value_list = material_entry.get('Value', [])

    # MaterialHandle is a nested struct containing RowName
    handle = find_property(value_list, 'MaterialHandle')
    if handle:
        row_name_prop = find_property(handle.get('Value', []), 'RowName')
        if row_name_prop:
            material_name = row_name_prop.get('Value', 'Unknown')

    # Count is a top-level IntPropertyData in the material struct
    count_prop = find_property(value_list, 'Count')
    if count_prop:
        count_val = count_prop.get('Value', 0)

    return material_name, count_val


# ---------------------------------------------------------------------------
#  .def XML generation
# ---------------------------------------------------------------------------

def build_changes(rows, filter_names=None):
    """Build XML <change> entries for the given recipe rows.

    For each recipe that has a DefaultRequiredMaterials array, emits one
    <change> per material setting its Count to 0. Also emits an XML comment
    showing the recipe name, material, and original count for readability.

    Args:
        rows: List of recipe row dicts from Exports[0].Table.Data.
        filter_names: If provided, only process rows whose Name is in this set.
                      Used to isolate Secrets-only recipes.

    Returns:
        (changes, total_materials, skipped_rows) where changes is a list
        of XML strings ready to join into the .def file body.
    """
    changes = []
    total_materials = 0
    skipped_rows = 0

    for row in rows:
        row_name = row.get('Name', '')
        if not row_name:
            continue

        # Skip rows not in the filter set (used for Secrets-only filtering)
        if filter_names is not None and row_name not in filter_names:
            continue

        # Find the materials array for this recipe
        materials_prop = find_property(
            row.get('Value', []), 'DefaultRequiredMaterials')
        if not materials_prop:
            skipped_rows += 1
            continue

        materials = materials_prop.get('Value', [])
        if not materials:
            skipped_rows += 1
            continue

        # Emit one <change> per material, indexed by array position
        for idx, material in enumerate(materials):
            mat_name, mat_count = get_material_info(material)
            # XML comment for human readability
            comment = f"    <!-- {row_name}: {mat_name} (was {mat_count}) -->"
            # The actual .def change entry
            change = (f'    <change item="{row_name}" '
                      f'property="DefaultRequiredMaterials[{idx}].Count" '
                      f'value="0" />')
            changes.append(comment)
            changes.append(change)
            total_materials += 1

    return changes, total_materials, skipped_rows


def write_def_file(output_path, title, recipe_count, changes,
                   total_materials):
    """Write a complete .def XML file with the given change entries.

    The .def format is the Moria MOD Creator's definition file format:
        <definition>
          <title>...</title>
          <author>...</author>
          <description>...</description>
          <mod file="path/to/target.json">
            <change ... />
          </mod>
        </definition>
    """
    changes_block = '\n'.join(changes)
    desc = (f"Sets all material counts to 0 for {recipe_count} "
            f"construction recipes ({total_materials} material entries)")
    def_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<definition>
  <title>{title}</title>
  <author>Moria MOD Creator</author>
  <description>{desc}</description>
  <mod file="Moria\\Content\\Tech\\Data\\Building\\DT_ConstructionRecipes.json">
{changes_block}
  </mod>
</definition>
'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(def_content)


# ---------------------------------------------------------------------------
#  Main generation logic
# ---------------------------------------------------------------------------

def generate_game_def(output_dir: Path) -> set:
    """Generate Free Building.def from base game construction recipes.

    Reads the game's DT_ConstructionRecipes.json, builds <change> entries
    for every material in every recipe, and writes the .def file.

    Returns:
        Set of game recipe names (used to exclude them from Secrets).
    """
    jsondata_dir = get_jsondata_dir()
    recipes_path = (jsondata_dir / 'Moria' / 'Content' / 'Tech' / 'Data'
                    / 'Building' / 'DT_ConstructionRecipes.json')

    if not recipes_path.exists():
        print(f"ERROR: Could not find {recipes_path}")
        print("Make sure the game data has been extracted to the "
              "jsondata directory.")
        return set()

    print(f"Loading game recipes: {recipes_path}...")
    game_data = load_json_file(recipes_path)
    game_rows = game_data['Exports'][0]['Table']['Data']
    game_names = {r['Name'] for r in game_rows}
    print(f"  Found {len(game_rows)} recipe rows")

    changes, total_materials, skipped_rows = build_changes(game_rows)
    recipe_count = len(game_rows) - skipped_rows

    print(f"  {total_materials} material entries across {recipe_count} recipes")
    print(f"  Skipped {skipped_rows} rows with no materials")

    def_path = output_dir / 'Free Building.def'
    write_def_file(def_path, 'Free Building - All Construction Costs Zero',
                   recipe_count, changes, total_materials)
    print(f"  Generated: {def_path}")
    return game_names


def generate_secrets_def(output_dir: Path, game_names: set):
    """Generate Free Building Secrets.def for Secrets-only recipes.

    Reads the Secrets-modded DT_ConstructionRecipes.json, filters out rows
    that already exist in the base game, and writes <change> entries only
    for the new Secrets recipes.

    Args:
        output_dir: Directory to write the .def file.
        game_names: Set of base game recipe names to exclude.
    """
    secrets_path = get_secrets_cache_dir() / 'DT_ConstructionRecipes.json'

    if not secrets_path.exists():
        print(f"\nWARNING: Secrets cache not found at {secrets_path}")
        print("Skipping Secrets .def generation.")
        return

    print(f"\nLoading Secrets recipes: {secrets_path}...")
    secrets_data = load_json_file(secrets_path)
    secrets_rows = secrets_data['Exports'][0]['Table']['Data']

    # Only include recipes that are NEW in Secrets (not in base game)
    new_names = {r['Name'] for r in secrets_rows} - game_names
    print(f"  Found {len(secrets_rows)} total rows, "
          f"{len(new_names)} Secrets-only")

    changes, total_materials, skipped_rows = build_changes(
        secrets_rows, filter_names=new_names)
    recipe_count = len(new_names) - skipped_rows

    print(f"  {total_materials} material entries across {recipe_count} recipes")
    print(f"  Skipped {skipped_rows} rows with no materials")

    def_path = output_dir / 'Free Building Secrets.def'
    write_def_file(
        def_path,
        'Free Building Secrets - All Secrets Construction Costs Zero',
        recipe_count, changes, total_materials)
    print(f"  Generated: {def_path}")


def main():
    """Generate both Free Building .def files."""
    output_dir = get_output_dir()

    # Step 1: Base game recipes -> Free Building.def
    game_names = generate_game_def(output_dir)

    # Step 2: Secrets-only recipes -> Free Building Secrets.def
    if game_names:
        generate_secrets_def(output_dir, game_names)

    print("\nDone!")


if __name__ == '__main__':
    main()
