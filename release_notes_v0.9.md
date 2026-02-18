# Moria MOD Creator v0.9

## Novice Mode - Mod Info Display

When clicking a prebuilt mod in Novice mode, the right pane now displays rich metadata from the mod's INI file.

### Features
- **Title**: Displayed in large bold text (40pt)
- **Authors**: Medium gray text showing mod creator(s)
- **HTML Description**: Full HTML rendering of mod descriptions using tkhtmlview
- **Placeholder**: "Select a mod to view its description" shown when no mod is selected
- Automatically clears when a mod is unchecked or Select All is toggled off

### INI Format
Prebuilt mod INI files now include a `[ModInfo]` section:
```ini
[ModInfo]
Title = Epic Packs Everywhere
Authors = JohnB
Description = <p>Removes storage restrictions so <b>all containers</b> accept any item type.</p>
```

## Installer Improvements

Overhauled the installer build pipeline for cleaner packaging.

### Changes
- **5 zip bundles**: Definitions, prebuilt modfiles, Secrets Source (.def only), New Objects, and utilities
- **Empty directories only**: `mymodfiles/`, `changesecrets/`, and `output/` are created as empty directories (no files packaged)
- **New prebuilt modfiles bundle**: 14 novice mode INI files now included in installer
- **Secrets Source**: Only `.def` manifest files are packaged
- **New Objects**: Buildings cache INI included
- **Removed**: Old mymodfiles.zip bundle (was packaging unnecessary build intermediates)
- All zip bundles copied to `dist/` during build

## AppData Cleanup Tool

New `scripts/cleanup_appdata.py` utility to manage temporary files.

### Capabilities
- Removes build intermediates: `jsonfiles/`, `uasset/`, `finalmod/` under each mod
- Cleans `output/` directory (all content)
- Cleans `Secrets Source/` (keeps only `.def` files)
- Removes `retoc` output and `build_log.txt`
- Removes empty directories throughout the tree
- **Safe**: Backs up all files to Desktop before removal
- **Dry-run mode**: Preview what will be cleaned without making changes

### Usage
```
python scripts/cleanup_appdata.py           # Preview only
python scripts/cleanup_appdata.py --run     # Execute cleanup
```

## INI File Reformatter

New `scripts/reformat_ini.py` utility to ensure prebuilt mod INI files use proper configparser-compatible multi-line formatting (indented continuation lines for HTML descriptions).

## Code Quality

- Pylint cleanup: scripts improved to 9.81/10
- Added `tkhtmlview` dependency for HTML rendering
- Custom `html_text_renderer.py` module for fallback HTML-to-CTkTextbox rendering

## Code Signing

- Automated code signing with SSL.com eSigner
- Both executable and installer are signed

## Files Changed
- 8 files modified, 5 new files added
- New dependencies: `tkhtmlview>=0.3.2`

## Credits
Co-Authored-By: Claude Opus 4.6

---

**Full Changelog**: https://github.com/jbowensii/MoriaModCreator/compare/v0.8...v0.9
