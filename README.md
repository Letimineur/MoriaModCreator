# Moria MOD Creator

Hi everyone, I have just finished Beta release 0.5 of Moria Mod Creator application.  

##This application:
- Handles loading the game data
- Using definition files applies any combination of changes to that data
- Comes pre-configured with 16 modes from Nexus mods, which the user can modify or create as is. 
OR
- Create your own custom combination into one mod defined by the user

It can be found here: https://github.com/jbowensii/MoriaModCreator or on my Discord channel
There are 3 files:
- MoriaMODCreator.exe
- definitions.zip    (game file change definitions)
- mymodfiles.zip  (pre-canned mods that repicate nexus mods)
All issues shown in the video have been resolved and tested. Please enter bugs on GitHub here: https://github.com/jbowensii/MoriaModCreator/issues

Utilities to download:  (all free, do not download if they ask you to pay)
https://github.com/trumank/retoc/releases
https://fmodel.app/
https://github.com/atenfyr/UAssetGUI
https://github.com/WistfulHopes/ZenTools-UE4

A desktop application for creating mods for **Lord of the Rings: Return to Moria**.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Version](https://img.shields.io/badge/Version-0.1-orange.svg)

## Overview

Moria MOD Creator simplifies the process of modding Return to Moria by providing a graphical interface to:
- Import and extract game files
- Convert game assets to editable JSON format
- Create mod definitions that specify what values to change
- Build complete mod packages ready for use

## Features

- **File Import** - Import game files using FModel integration
- **JSON Conversion** - Convert `.uasset` files to editable JSON format using UAssetGUI
- **Mod Definition Editor** - Create and manage `.def` files that define mod changes
- **Build System** - Automatically process mod definitions, modify JSON, convert back to game format, and package as a zip file
- **My Mods Management** - Organize multiple mods with separate definition sets

## Requirements

- Python 3.10 or higher
- Windows OS
- The following utilities (placed in `%APPDATA%\MoriaMODCreator\utilities\`):
  - `UAssetGUI.exe` - For JSON/uasset conversion
  - `retoc.exe` - For creating zen format packages
  - `FModel.exe` - For extracting game files (optional, for import feature)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jbowensii/MoriaModCreator.git
   cd MoriaModCreator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Place required utilities in `%APPDATA%\MoriaMODCreator\utilities\`

5. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Getting Started

1. **Import Game Files** - Click the Import button to extract game files using FModel
2. **Convert to JSON** - Convert the extracted `.uasset` files to JSON format
3. **Create a Mod** - Use "My Mods" dropdown to create a new mod project
4. **Add Definitions** - Create `.def` files that specify what values to change
5. **Build** - Click Build to process your mod and create a ready-to-use zip file

### Mod Definition Files (.def)

Definition files are XML files that specify what changes to make to game data:

```xml
<?xml version="1.0" encoding="utf-8"?>
<definition>
    <description>Makes mining song buff last longer</description>
    <author>YourName</author>
    <mod file="\Moria\Content\Character\Shared\Effects\GE_MiningSong_CompleteBuff.json">
        <object name="GE_MiningSong_CompleteBuff">
            <change property="DurationMagnitude.ScalableFloatMagnitude.Value" value="1800" />
        </object>
    </mod>
</definition>
```

### Build Output

When you click Build, the application:
1. Copies and modifies JSON files based on your definitions
2. Converts JSON back to `.uasset` format
3. Packages assets into zen format (`.utoc`/`.ucas`/`.pak`)
4. Creates a zip file in your Downloads folder

## Project Structure

```
MoriaModCreator/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── assets/                 # Icons and images
│   ├── icons/
│   └── images/
├── src/
│   ├── config.py          # Configuration and paths
│   └── ui/
│       ├── main_window.py # Main application window
│       ├── about_dialog.py
│       ├── config_dialog.py
│       ├── import_dialog.py
│       ├── json_convert_dialog.py
│       ├── mod_name_dialog.py
│       └── utility_check_dialog.py
└── test/                   # Test data
```

## Data Directories

The application stores data in `%APPDATA%\MoriaMODCreator\`:

| Directory | Purpose |
|-----------|---------|
| `definitions/` | Global definition files |
| `mymodfiles/` | Per-mod project files |
| `output/jsondata/` | Converted JSON files |
| `utilities/` | External tools (UAssetGUI, retoc, FModel) |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [UAssetGUI](https://github.com/atenfyr/UAssetGUI) - For uasset/JSON conversion
- [retoc](https://github.com/trumank/retoc) - For zen format packaging
- [FModel](https://fmodel.app/) - For game file extraction
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI framework

## Disclaimer

This tool is for personal use only. Always respect the game's terms of service and the rights of the developers.
