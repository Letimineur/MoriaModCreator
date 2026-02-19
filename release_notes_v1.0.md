# Moria MOD Creator v1.0

## Constructions Tab

New dedicated tab for editing base game construction recipes, mirroring the existing Secrets tab functionality.

### Features
- **Full construction editing**: Browse, search, and modify all base game building recipes
- **Category sub-tabs**: Buildings, Items, Weapons, Tools, Armor, Flora, Loot
- **Cached game data**: Scans and caches game JSON files for fast browsing
- **Definition management**: Create, edit, and build .def files for construction modifications

## Filterable Dropdowns

All dropdown fields across both Constructions and Secrets tabs now support type-to-filter.

### Features
- **Partial match filtering**: Type any part of an option name to narrow the list
- **Case-insensitive search**: Filters from the first character typed
- **Scrollable popup**: Handles large option lists (100+ materials) with a scrollable dropdown
- **Keyboard navigation**: Up/Down arrows to move, Enter to select, Escape to close
- **Arrow button toggle**: Click the dropdown arrow to show all options
- **Drop-in replacement**: Uses the same `variable`/`values` API as CTkComboBox

## Free Building Helper

New utility to generate .def files that set all construction material costs to zero.

### Output
- **Free Building.def**: 1,295 material entries across 812 base game recipes
- **Free Building Secrets.def**: 297 material entries across 179 Secrets-only recipes
- Output location: `%AppData%/MoriaMODCreator/Definitions/Building/`

### Usage
```
python helpers/freebuildinghelper.py
```

## Installer Improvements

Expanded installer to ship constructions and secrets data alongside existing bundles.

### Changes
- **7 zip bundles**: Added `changeconstructions.zip` and `changesecrets.zip` to the installer
- **changeconstructions**: Ships prefix directories with .ini files and .def definitions
- **changesecrets**: Ships both Axbeard Secrets and Mereaks Secrets prefix data
- **New AppData directories**: Installer creates `cache/constructions`, `cache/game`, `cache/secrets`, and `changeconstructions`
- **Inno Setup path**: Build script now finds Inno Setup in user-local install path

## AppData Cleanup Tool Updates

Enhanced the cleanup utility with new targets for the expanded directory structure.

### New Cleanup Targets
- **Cache directories**: `cache/constructions`, `cache/game`, `cache/secrets` (~200 MB of cached JSON)
- **Change set intermediates**: JSON build files in `changeconstructions/` and `changesecrets/` (preserves .def files)
- **New Objects build cache**: `New Objects/Build/` intermediates
- **Refactored**: Extracted scan, summary, and execution into separate functions (pylint 10.00/10)

## Novice Mode Improvements

- Prebuilt mod list now includes 16 INI files (up from 14)
- Updated Definitions bundle with 107 definition files including new Free Building .def files

## Code Quality

- New `FilterableComboBox` widget: `src/ui/filterable_combobox.py`
- New `constructions_view.py`: Full constructions editing UI (~7,000 lines)
- Removed unused imports and dead code from `main_window.py`
- All modified files pass pylint with scores 9.55+

## Files Changed
- 17 files changed: 8,221 insertions, 209 deletions
- 4 new files, 2 new installer zip bundles

---

**Full Changelog**: https://github.com/jbowensii/MoriaModCreator/compare/v0.9...v1.0
