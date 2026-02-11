"""Patch ore Properties JSON files to add missing DropRate property.

Many ore Properties_*.json files in the game data are missing the
PrimaryDrop.DropRate sub-property. This helper adds DropRate (default 0.0)
to any Properties file that has PrimaryDrop but lacks DropRate, so the
Mod Builder UI can display and edit the value.

Usage:
    python helpers/patch_ore_droprates.py [--dry-run]

Options:
    --dry-run    Show what would be changed without modifying files.
"""

import json
import os
import sys
from pathlib import Path

DROPRATE_PROPERTY = {
    "$type": "UAssetAPI.PropertyTypes.Objects.FloatPropertyData, UAssetAPI",
    "Name": "DropRate",
    "DuplicationIndex": 0,
    "ArrayIndex": 0,
    "IsZero": False,
    "PropertyTagFlags": "None",
    "PropertyTagExtensions": "NoExtension",
    "Value": 0.0
}


def patch_file(json_path: Path, dry_run: bool = False) -> bool:
    """Add DropRate to PrimaryDrop if missing.

    Returns True if the file was modified (or would be in dry-run).
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    exports = data.get('Exports', [])
    modified = False

    for export in exports:
        export_data = export.get('Data', [])
        if not isinstance(export_data, list):
            continue

        for prop in export_data:
            if not isinstance(prop, dict) or prop.get('Name') != 'PrimaryDrop':
                continue

            value_array = prop.get('Value', [])
            if not isinstance(value_array, list):
                continue

            # Check if DropRate already exists
            has_droprate = any(
                isinstance(v, dict) and v.get('Name') == 'DropRate'
                for v in value_array
            )

            if not has_droprate:
                if not dry_run:
                    value_array.append(DROPRATE_PROPERTY.copy())
                modified = True

    if modified and not dry_run:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return modified


def main():
    dry_run = '--dry-run' in sys.argv

    appdata = Path(os.environ['APPDATA']) / 'MoriaMODCreator'
    baking_dir = (
        appdata / 'output' / 'jsondata' / 'Moria' / 'Content'
        / 'Environments' / 'Voxels' / 'Baking'
    )

    if not baking_dir.exists():
        print(f"ERROR: Baking directory not found: {baking_dir}")
        return 1

    properties_files = sorted(baking_dir.glob('Properties_*.json'))
    if not properties_files:
        print("No Properties_*.json files found.")
        return 1

    print(f"Scanning {len(properties_files)} Properties files in:")
    print(f"  {baking_dir}")
    if dry_run:
        print("  (DRY RUN - no files will be modified)")
    print()

    patched = 0
    skipped = 0
    for fp in properties_files:
        was_modified = patch_file(fp, dry_run=dry_run)
        if was_modified:
            action = "WOULD PATCH" if dry_run else "PATCHED"
            print(f"  {action}: {fp.name}")
            patched += 1
        else:
            skipped += 1

    print()
    print(f"Results: {patched} patched, {skipped} already had DropRate")
    return 0


if __name__ == '__main__':
    sys.exit(main())
