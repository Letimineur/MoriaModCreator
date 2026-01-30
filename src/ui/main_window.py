"""Main application window for Moria MOD Creator."""

import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
import customtkinter as ctk

from src.config import get_utilities_dir, get_definitions_dir, get_output_dir
from src.ui.about_dialog import show_about_dialog
from src.ui.utility_check_dialog import find_utility
from src.ui.import_dialog import show_import_dialog
from src.ui.json_convert_dialog import show_json_convert_dialog


# Icon sizes
TOOLBAR_ICON_SIZE = (32, 32)
TITLE_ICON_SIZE = (40, 40)


def get_assets_dir() -> Path:
    """Get the assets directory path."""
    return Path(__file__).parent.parent.parent / "assets"


def get_icon_path(name: str) -> Path:
    """Get the path to an icon file."""
    return get_assets_dir() / "icons" / name


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.title("Moria MOD Creator")
        self.geometry("1024x768")
        self.minsize(800, 600)
        
        # Start maximized/fullscreen
        self.after(10, lambda: self.state('zoomed'))

        # Track definition checkboxes and their states
        self.definition_checkboxes: dict[Path, ctk.CTkCheckBox] = {}
        self.definition_vars: dict[Path, ctk.BooleanVar] = {}

        # Track row checkboxes and entries for the right pane
        self.row_checkboxes: list[ctk.CTkCheckBox] = []
        self.row_checkbox_vars: list[ctk.BooleanVar] = []
        self.row_entries: list[ctk.CTkEntry] = []
        self.row_entry_vars: list[ctk.StringVar] = []
        self.row_values: list[str] = []  # Original values for resetting

        self._create_widgets()


    def _create_widgets(self):
        """Create the main window widgets."""
        # Main content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        # Single header row with title left, utility icons center, settings/help right
        self._create_header()

        # Main content area with definitions pane on left (1/3) and main area (2/3)
        self._create_main_area()

        # Status bar at the bottom
        self._create_status_bar()

    def _create_header(self):
        """Create the header with title left, utility icons center, settings/help right."""
        header_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
            height=60
        )
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)

        # Configure grid columns: left (weight 1), center (weight 1), right (weight 1)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)

        # LEFT: App icon and title
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="w")

        icon_path = get_icon_path("app_icon.png")
        if icon_path.exists():
            try:
                img = Image.open(icon_path)
                icon_image = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=TITLE_ICON_SIZE
                )
                icon_label = ctk.CTkLabel(left_frame, image=icon_image, text="")
                icon_label.pack(side="left", padx=(0, 10))
            except Exception:
                pass

        title_label = ctk.CTkLabel(
            left_frame,
            text="Moria MOD Creator",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(side="left")

        # CENTER: Import, Convert, UAssetGUI and FModel buttons
        center_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        center_frame.grid(row=0, column=1)

        self._create_toolbar_button(
            center_frame,
            "import_icon.png",
            "Import",
            self._run_import
        )

        self._create_toolbar_button(
            center_frame,
            "json_icon.png",
            "Convert to JSON",
            self._run_json_convert
        )

        self._create_toolbar_button(
            center_frame,
            "uasset_icon.png",
            "UAssetGUI",
            self._launch_uassetgui
        )

        self._create_toolbar_button(
            center_frame,
            "fmodel_icon.png",
            "FModel",
            self._launch_fmodel
        )

        # RIGHT: Settings and Help buttons
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="e")

        self._create_toolbar_button(
            right_frame,
            "gear_icon.png",
            "Settings",
            self._open_settings
        )

        self._create_toolbar_button(
            right_frame,
            "help_icon.png",
            "Help",
            self._open_about
        )

    def _create_main_area(self):
        """Create the main content area with definitions pane."""
        # Container for the main area
        main_area = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_area.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure grid: definitions pane (smaller) and main content (larger)
        main_area.grid_columnconfigure(0, weight=1)
        main_area.grid_columnconfigure(1, weight=3)
        main_area.grid_rowconfigure(0, weight=1)

        # Definitions pane (left)
        self._create_definitions_pane(main_area)

        # Main content area (right)
        self.main_content = ctk.CTkFrame(main_area, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    def _create_status_bar(self):
        """Create the status bar at the bottom of the window."""
        self.status_bar = ctk.CTkFrame(self.content_frame, height=70)
        self.status_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.status_bar.pack_propagate(False)

        # Top row - buttons aligned to right (under right pane)
        button_frame = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(5, 0))

        self.save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            width=80,
            height=32,
            fg_color="#28a745",
            hover_color="#218838",
            text_color="white",
            font=ctk.CTkFont(weight="bold"),
            command=self._on_save_click
        )
        self.save_btn.pack(side="right", padx=(0, 10))

        # Bottom row - status message
        self.status_message = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_message.pack(fill="x", padx=10, pady=(5, 5))

    def set_status_message(self, message: str, is_error: bool = False):
        """Set the status bar message.
        
        Args:
            message: The message to display.
            is_error: If True, display in red color.
        """
        self.status_message.configure(
            text=message,
            text_color="red" if is_error else ("gray70", "gray30")
        )

    def clear_status_message(self):
        """Clear the status bar message."""
        self.status_message.configure(text="")

    def _create_definitions_pane(self, parent):
        """Create the definitions file list pane."""
        # Track current directory for navigation
        self.current_definitions_dir = None
        
        # Definitions frame with border
        definitions_frame = ctk.CTkFrame(parent)
        definitions_frame.grid(row=0, column=0, sticky="nsew")

        # Title row with label and refresh button
        title_row = ctk.CTkFrame(definitions_frame, fg_color="transparent")
        title_row.pack(fill="x", pady=(10, 5), padx=10)

        title_label = ctk.CTkLabel(
            title_row,
            text="Definitions Files",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(side="left")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            title_row,
            text="↻",
            width=28,
            height=28,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            command=self._refresh_definitions_list
        )
        refresh_btn.pack(side="right")

        # Scrollable frame for file list
        self.definitions_list = ctk.CTkScrollableFrame(
            definitions_frame,
            fg_color="transparent"
        )
        self.definitions_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Load definitions files
        self._refresh_definitions_list()

    def _refresh_definitions_list(self, target_dir: Path = None):
        """Refresh the list of definition files and directories.
        
        Args:
            target_dir: Directory to display. If None, uses root definitions dir.
        """
        # Clear existing items
        for widget in self.definitions_list.winfo_children():
            widget.destroy()

        # Clear tracking dictionaries
        self.definition_checkboxes.clear()
        self.definition_vars.clear()

        # Get definitions directory
        root_dir = get_definitions_dir()
        
        if target_dir is None:
            target_dir = root_dir
        
        # Store current directory
        self.current_definitions_dir = target_dir

        if not target_dir.exists():
            no_files_label = ctk.CTkLabel(
                self.definitions_list,
                text="No definitions directory found",
                text_color="gray"
            )
            no_files_label.pack(pady=10)
            return

        # Add ".." back navigation if not at root
        if target_dir != root_dir:
            back_frame = ctk.CTkFrame(self.definitions_list, fg_color="transparent")
            back_frame.pack(fill="x", pady=2, anchor="w")
            
            back_label = ctk.CTkLabel(
                back_frame,
                text="📁 ..",
                anchor="w",
                cursor="hand2",
                font=ctk.CTkFont(size=14)
            )
            back_label.pack(side="left", fill="x", expand=True, padx=(5, 0))
            back_label.bind("<Button-1>", lambda e: self._refresh_definitions_list(target_dir.parent))

        # List directories first, then .def files
        dirs = sorted([d for d in target_dir.iterdir() if d.is_dir()])
        def_files = sorted([f for f in target_dir.iterdir()
                           if f.is_file() and f.suffix.lower() == '.def'])

        if not dirs and not def_files:
            no_files_label = ctk.CTkLabel(
                self.definitions_list,
                text="No items found",
                text_color="gray"
            )
            no_files_label.pack(pady=10)
            return

        # Create entries for directories
        for dir_path in dirs:
            row_frame = ctk.CTkFrame(self.definitions_list, fg_color="transparent")
            row_frame.pack(fill="x", pady=2, anchor="w")

            # Folder icon and name (clickable)
            dir_label = ctk.CTkLabel(
                row_frame,
                text=f"📁 {dir_path.name}",
                anchor="w",
                cursor="hand2",
                font=ctk.CTkFont(size=14)
            )
            dir_label.pack(side="left", fill="x", expand=True, padx=(5, 0))
            dir_label.bind("<Button-1>", lambda e, p=dir_path: self._refresh_definitions_list(p))

        # Create a checkbox for each .def file
        for file_path in def_files:
            title = self._get_definition_title(file_path)

            # Create a row frame for checkbox and clickable label
            row_frame = ctk.CTkFrame(self.definitions_list, fg_color="transparent")
            row_frame.pack(fill="x", pady=2, anchor="w")

            # Create BooleanVar for checkbox state
            var = ctk.BooleanVar(value=False)
            self.definition_vars[file_path] = var

            # Create checkbox (no text)
            checkbox = ctk.CTkCheckBox(
                row_frame,
                text="",
                variable=var,
                onvalue=True,
                offvalue=False,
                width=20
            )
            checkbox.pack(side="left")
            self.definition_checkboxes[file_path] = checkbox

            # Create clickable label for the title
            title_label = ctk.CTkLabel(
                row_frame,
                text=title,
                anchor="w",
                cursor="hand2"
            )
            title_label.pack(side="left", fill="x", expand=True)
            # Bind click to show details pane
            title_label.bind("<Button-1>", lambda e, p=file_path: self._show_definition_details(p))

    def _get_definition_title(self, file_path: Path) -> str:
        """Extract the title from a .def file.

        Args:
            file_path: Path to the .def file.

        Returns:
            The title value, or filename if not found.
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            title_elem = root.find('title')
            if title_elem is not None and title_elem.text:
                return title_elem.text.strip()
        except ET.ParseError:
            pass
        except Exception:
            pass
        # Fallback to filename without extension
        return file_path.stem

    def get_selected_definitions(self) -> list[Path]:
        """Get list of checked definition file paths.

        Returns:
            List of paths to checked definition files.
        """
        return [path for path, var in self.definition_vars.items() if var.get()]

    def _get_definition_description(self, file_path: Path) -> str:
        """Extract the description from a .def file.

        Args:
            file_path: Path to the .def file.

        Returns:
            The description value, or empty string if not found.
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            desc_elem = root.find('description')
            if desc_elem is not None and desc_elem.text:
                return desc_elem.text.strip()
        except ET.ParseError:
            pass
        except Exception:
            pass
        return ""

    def _get_definition_author(self, file_path: Path) -> str:
        """Extract the author from a .def file.

        Args:
            file_path: Path to the .def file.

        Returns:
            The author value, or empty string if not found.
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            author_elem = root.find('author')
            if author_elem is not None and author_elem.text:
                return author_elem.text.strip()
        except ET.ParseError:
            pass
        except Exception:
            pass
        return ""

    def _get_definition_changes(self, file_path: Path) -> list[dict]:
        """Extract the change elements from a .def file.

        Args:
            file_path: Path to the .def file.

        Returns:
            List of dictionaries with item, property, value keys.
        """
        changes = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            # Find all <change> elements at root level and inside <mod> elements
            for change_elem in root.iter('change'):
                item = change_elem.get('item', '')
                prop = change_elem.get('property', '')
                value = change_elem.get('value', '')
                if item and prop:  # Only add if we have at least item and property
                    changes.append({
                        'item': item,
                        'property': prop,
                        'value': value
                    })
        except ET.ParseError:
            pass
        except Exception:
            pass
        # Sort by item name
        return sorted(changes, key=lambda x: x['item'].lower())

    def _get_mod_file_path(self, file_path: Path) -> str | None:
        """Extract the mod file path from a .def file's <mod> element.

        Args:
            file_path: Path to the .def file.

        Returns:
            The file attribute value, or None if not found.
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            mod_elem = root.find('mod')
            if mod_elem is not None:
                return mod_elem.get('file', None)
        except ET.ParseError:
            pass
        except Exception:
            pass
        return None

    def _load_game_data(self, mod_file_path: str) -> dict | None:
        """Load game data JSON file from the jsondata directory.

        Args:
            mod_file_path: Relative path from the mod element (e.g., \\Moria\\Content\\...)

        Returns:
            Parsed JSON data or None if file not found.
        """
        try:
            # Normalize the path - remove leading backslash and convert to forward slashes
            normalized_path = mod_file_path.lstrip('\\').lstrip('/').replace('\\', '/')
            
            # Build full path: %APPDATA%/MoriaMODCreator/output/jsondata/ + normalized_path
            jsondata_dir = get_output_dir() / 'jsondata'
            full_path = jsondata_dir / normalized_path
            
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _load_string_table(self, table_path: str) -> dict:
        """Load a string table and return a lookup dictionary.

        Args:
            table_path: The TableId path (e.g., /Game/Tech/Data/StringTables/Items.Items)

        Returns:
            Dictionary mapping string keys to their values.
        """
        try:
            # Convert TableId to file path
            # /Game/Tech/Data/StringTables/Items.Items -> Moria/Content/Tech/Data/StringTables/Items.json
            # The .Items suffix is the table namespace, not part of the file name
            path_parts = table_path.lstrip('/').split('.')
            base_path = path_parts[0]  # e.g., "Game/Tech/Data/StringTables/Items"
            
            # Replace "Game" with "Moria/Content"
            if base_path.startswith('Game/'):
                base_path = 'Moria/Content/' + base_path[5:]
            
            # Add .json extension
            json_path = base_path + '.json'
            
            jsondata_dir = get_output_dir() / 'jsondata'
            full_path = jsondata_dir / json_path
            
            if not full_path.exists():
                return {}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse the string table: Exports[0].Table.Value is array of [key, value] pairs
            lookup = {}
            try:
                entries = data['Exports'][0]['Table']['Value']
                for entry in entries:
                    if isinstance(entry, list) and len(entry) >= 2:
                        lookup[entry[0]] = entry[1]
            except (KeyError, IndexError):
                pass
            
            return lookup
        except Exception:
            return {}

    def _get_nested_property_value(self, data: list | dict, property_path: str) -> str:
        """Get a property value using dot notation for nested traversal.

        Args:
            data: The data to search (list of properties or dict).
            property_path: Dot-separated property path (e.g., "DurationMagnitude.ScalableFloatMagnitude.Value").

        Returns:
            The property value as a string, or empty string if not found.
        """
        if not data or not property_path:
            return ''
        
        parts = property_path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, list):
                # Search for property by Name in list
                found = False
                for item in current:
                    if isinstance(item, dict) and item.get('Name') == part:
                        # Check if this has a Value that is a list (nested struct)
                        if 'Value' in item:
                            current = item['Value']
                            found = True
                            break
                if not found:
                    return ''
            elif isinstance(current, dict):
                if part in current:
                    current = current[part]
                elif 'Value' in current:
                    # Try to traverse into Value
                    current = current['Value']
                    # Then look for the part
                    if isinstance(current, list):
                        found = False
                        for item in current:
                            if isinstance(item, dict) and item.get('Name') == part:
                                current = item.get('Value', item)
                                found = True
                                break
                        if not found:
                            return ''
                    elif isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return ''
                else:
                    return ''
            else:
                # Reached a leaf value
                return ''
        
        # Extract final value
        if isinstance(current, (str, int, float, bool)):
            return str(current)
        elif isinstance(current, dict) and 'Value' in current:
            val = current['Value']
            if isinstance(val, (str, int, float, bool)):
                return str(val)
        elif isinstance(current, list) and len(current) > 0:
            # Could be a final value in an unexpected format
            pass
        
        return ''

    def _get_item_property_value(self, item_data: dict, property_name: str) -> str:
        """Get a property value from an item's data.

        Args:
            item_data: The item's Value array from the JSON.
            property_name: The property name to find (supports dot notation for nested properties).

        Returns:
            The property value as a string, or empty string if not found.
        """
        if not item_data:
            return ''
        
        # Get the Value array (for data table items)
        value_array = item_data.get('Value', [])
        if not value_array:
            return ''
        
        # Check if property uses dot notation (nested path)
        if '.' in property_name:
            return self._get_nested_property_value(value_array, property_name)
        
        # Simple property lookup
        for prop in value_array:
            if prop.get('Name') == property_name:
                # Handle different property types
                if 'Value' in prop:
                    val = prop['Value']
                    # If it's a simple value, return it
                    if isinstance(val, (str, int, float, bool)):
                        return str(val)
                    # If it's a dict with nested value, try to extract
                    if isinstance(val, dict):
                        return str(val)
                return ''
        return ''

    def _get_item_display_name(self, item_data: dict, string_tables: dict) -> str:
        """Get the display name for an item by resolving from string tables.

        Args:
            item_data: The item's data from the JSON.
            string_tables: Cache of loaded string tables {table_path: {key: value}}

        Returns:
            The resolved display name, or the item's Name as fallback.
        """
        item_name = item_data.get('Name', '')
        
        # Find the DisplayName property in the item's Value array
        for prop in item_data.get('Value', []):
            if prop.get('Name') == 'DisplayName':
                table_id = prop.get('TableId', '')
                string_key = prop.get('Value', '')
                
                if table_id and string_key:
                    # Load string table if not cached
                    if table_id not in string_tables:
                        string_tables[table_id] = self._load_string_table(table_id)
                    
                    # Look up the display name
                    display_name = string_tables[table_id].get(string_key, '')
                    if display_name:
                        return display_name
                break
        
        # Fallback to item's internal Name
        return item_name

    def _build_display_data(self, file_path: Path) -> list[dict]:
        """Build the display data by merging game data with XML changes.

        Args:
            file_path: Path to the .def file.

        Returns:
            List of dictionaries with name, property, value, new_value keys.
        """
        display_data = []
        
        # Get mod file path and load game data
        mod_file_path = self._get_mod_file_path(file_path)
        if not mod_file_path:
            return display_data
        
        game_data = self._load_game_data(mod_file_path)
        if not game_data:
            return display_data
        
        # Get XML changes as a lookup: {item_name: {property: new_value}}
        xml_changes = self._get_definition_changes(file_path)
        changes_lookup = {}
        for change in xml_changes:
            item_name = change['item']
            if item_name not in changes_lookup:
                changes_lookup[item_name] = {}
            changes_lookup[item_name][change['property']] = change['value']
        
        # Get all items from the game data
        # Try data table format first (Exports[0].Table.Data)
        items = None
        is_data_table = False
        try:
            items = game_data['Exports'][0]['Table']['Data']
            is_data_table = True
        except (KeyError, IndexError, TypeError):
            pass
        
        # If not a data table, try single asset format (Exports with Data array)
        if not is_data_table:
            return self._build_display_data_single_asset(game_data, changes_lookup)
        
        # Cache for string tables to avoid reloading
        string_tables = {}
        
        # Collect all properties being modified by the XML to know which to display
        all_properties = set()
        none_defaults = {}  # Store property -> value from NONE entries
        for item_changes in changes_lookup.values():
            all_properties.update(item_changes.keys())
        
        # Check for NONE entries - these define properties/values but no items selected
        if 'NONE' in changes_lookup:
            none_defaults = changes_lookup['NONE']
            # Remove NONE from lookup so it doesn't match any real items
            del changes_lookup['NONE']
        
        # For each item, show the properties (with XML changes where applicable)
        for item in items:
            item_name = item.get('Name', '')
            display_name = self._get_item_display_name(item, string_tables)
            
            # For each property type being tracked
            for prop_name in all_properties:
                current_value = self._get_item_property_value(item, prop_name)
                
                # Skip if this item doesn't have this property
                if not current_value:
                    continue
                
                # Check if there's an XML change for this item/property
                has_mod = item_name in changes_lookup and prop_name in changes_lookup[item_name]
                if has_mod:
                    new_value = changes_lookup[item_name][prop_name]
                elif prop_name in none_defaults:
                    # Use NONE default value but don't check the item
                    new_value = none_defaults[prop_name]
                else:
                    # No XML modification - new equals current value
                    new_value = current_value
                
                display_data.append({
                    'row_name': item_name,  # Original name for XML
                    'name': display_name,   # Display name from string table
                    'property': prop_name,
                    'value': current_value,
                    'new_value': new_value,
                    'has_mod': has_mod
                })
        
        # Sort by name
        return sorted(display_data, key=lambda x: x['name'].lower())

    def _build_display_data_single_asset(self, game_data: dict, changes_lookup: dict) -> list[dict]:
        """Build display data for single asset files (non-data-table).

        Args:
            game_data: The parsed JSON game data.
            changes_lookup: Dictionary of {item_name: {property: new_value}}.

        Returns:
            List of dictionaries with name, property, value, new_value keys.
        """
        display_data = []
        
        # Check for NONE entries - these define properties/values for all exports
        none_defaults = {}
        if 'NONE' in changes_lookup:
            none_defaults = changes_lookup['NONE']
            # Remove NONE from lookup so it doesn't try to match as item name
            changes_lookup = {k: v for k, v in changes_lookup.items() if k != 'NONE'}
        
        # Collect all properties being modified by the XML
        all_properties = set()
        for item_changes in changes_lookup.values():
            all_properties.update(item_changes.keys())
        all_properties.update(none_defaults.keys())
        
        # Find exports with Data arrays (skip class exports)
        for export in game_data.get('Exports', []):
            if 'Data' not in export or not isinstance(export.get('Data'), list):
                continue
            if len(export.get('Data', [])) == 0:
                continue
            
            # Get the item name from ObjectName
            item_name = export.get('ObjectName', '')
            
            # Skip class definition exports (non-Default__ exports that are just class defs)
            # Focus on Default__ exports which contain actual property values
            # But also check if there's a direct match in changes_lookup
            
            # Check for direct match in changes_lookup
            has_direct_match = False
            for lookup_item_name in changes_lookup:
                if lookup_item_name == item_name or lookup_item_name in item_name:
                    has_direct_match = True
                    break
            
            # For each property we're tracking, try to get the value from this export
            for prop_name in all_properties:
                # Get current value using nested property lookup
                current_value = self._get_nested_property_value(export['Data'], prop_name)
                
                if not current_value:
                    continue
                
                # Check if there's a specific item match in changes_lookup
                has_mod = False
                new_value = current_value
                row_name = item_name
                
                for lookup_item_name, properties in changes_lookup.items():
                    if lookup_item_name == item_name or lookup_item_name in item_name:
                        if prop_name in properties:
                            has_mod = True
                            new_value = properties[prop_name]
                            row_name = lookup_item_name
                            break
                
                # If no specific match but NONE defaults exist for this property
                if not has_mod and prop_name in none_defaults:
                    new_value = none_defaults[prop_name]
                    # Keep row_name as item_name (the actual export name) for saving
                
                display_data.append({
                    'row_name': row_name,  # Always use actual item name for XML saving
                    'name': item_name,
                    'property': prop_name,
                    'value': current_value,
                    'new_value': new_value,
                    'has_mod': has_mod
                })
        
        return display_data

    def _show_definition_details(self, file_path: Path):
        """Show the definition details in the right pane.

        Args:
            file_path: Path to the .def file.
        """
        # Store current definition path for saving
        self.current_definition_path = file_path
        
        # Clear existing content in main_content
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Get description and build display data from game files
        title = self._get_definition_title(file_path)
        author = self._get_definition_author(file_path)
        description = self._get_definition_description(file_path)
        display_data = self._build_display_data(file_path)

        # Create details frame
        details_frame = ctk.CTkFrame(self.main_content)
        details_frame.pack(fill="both", expand=True)

        # Header section with Title, Author, Description
        header_info_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        header_info_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        label_font = ctk.CTkFont(size=14, weight="bold")
        value_font = ctk.CTkFont(size=14)
        
        # Title row
        title_row = ctk.CTkFrame(header_info_frame, fg_color="transparent")
        title_row.pack(fill="x", anchor="w")
        ctk.CTkLabel(title_row, text="TITLE:", font=label_font, width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(title_row, text=title if title else file_path.stem, font=value_font, anchor="w").pack(side="left", fill="x", expand=True)
        
        # Author row (only if author exists)
        if author:
            author_row = ctk.CTkFrame(header_info_frame, fg_color="transparent")
            author_row.pack(fill="x", anchor="w")
            ctk.CTkLabel(author_row, text="AUTHOR:", font=label_font, width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(author_row, text=author, font=value_font, anchor="w").pack(side="left", fill="x", expand=True)
        
        # Description row
        if description:
            desc_row = ctk.CTkFrame(header_info_frame, fg_color="transparent")
            desc_row.pack(fill="x", anchor="w")
            ctk.CTkLabel(desc_row, text="DESCRIPTION:", font=label_font, width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(desc_row, text=description, font=value_font, anchor="w").pack(side="left", fill="x", expand=True)

        # Table header
        header_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 0))

        # Configure columns with weights for alignment (checkbox, name, property, value, new)
        header_frame.grid_columnconfigure(0, weight=0, minsize=30)  # Checkbox column
        header_frame.grid_columnconfigure(1, weight=3, uniform="col")  # Name - larger
        header_frame.grid_columnconfigure(2, weight=2, uniform="col")  # Property - moved towards Name
        header_frame.grid_columnconfigure(3, weight=1, uniform="col")
        header_frame.grid_columnconfigure(4, weight=1, uniform="col")

        header_font = ctk.CTkFont(size=16, weight="bold")
        
        # Header tri-state button for select all/none/mixed
        # States: "none" (☐), "all" (☑), "mixed" (☐ with ─)
        self.select_all_state = "none"  # Track state: "none", "all", "mixed"
        self.select_all_btn = ctk.CTkButton(
            header_frame,
            text="☐",
            width=24,
            height=24,
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            text_color=("gray10", "gray90"),
            font=ctk.CTkFont(size=16),
            command=self._on_select_all_toggle
        )
        self.select_all_btn.grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(header_frame, text="Name", font=header_font, anchor="w").grid(
            row=0, column=1, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(header_frame, text="Property", font=header_font, anchor="w").grid(
            row=0, column=2, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(header_frame, text="Value", font=header_font, anchor="w").grid(
            row=0, column=3, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(header_frame, text="New", font=header_font, anchor="w").grid(
            row=0, column=4, sticky="ew")

        # Scrollable table for changes
        changes_frame = ctk.CTkScrollableFrame(details_frame)
        changes_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Configure columns for changes with weights for alignment
        changes_frame.grid_columnconfigure(0, weight=0, minsize=30)  # Checkbox column
        changes_frame.grid_columnconfigure(1, weight=3, uniform="col")  # Name - larger
        changes_frame.grid_columnconfigure(2, weight=2, uniform="col")  # Property - moved towards Name
        changes_frame.grid_columnconfigure(3, weight=1, uniform="col")
        changes_frame.grid_columnconfigure(4, weight=1, uniform="col")

        # Clear row tracking lists
        self.row_checkboxes = []
        self.row_checkbox_vars = []
        self.row_entries = []
        self.row_entry_vars = []
        self.row_values = []
        self.row_names = []      # Original item names for XML
        self.row_properties = [] # Property names for XML

        # Display the data in table format
        if display_data:
            row_font = ctk.CTkFont(size=16)
            for i, item in enumerate(display_data):
                # Store original value for reset
                self.row_values.append(str(item['value']))
                # Store row_name and property for XML saving
                self.row_names.append(item['row_name'])
                self.row_properties.append(item['property'])
                
                # Checkbox - checked if has XML modification
                var = ctk.BooleanVar(value=item.get('has_mod', False))
                self.row_checkbox_vars.append(var)
                
                # New column - editable input field with new_value as default
                new_var = ctk.StringVar(value=str(item['new_value']))
                self.row_entry_vars.append(new_var)
                
                checkbox = ctk.CTkCheckBox(
                    changes_frame,
                    text="",
                    variable=var,
                    width=20,
                    command=lambda idx=i: self._on_row_checkbox_toggle(idx)
                )
                checkbox.grid(row=i, column=0, sticky="w", pady=2)
                self.row_checkboxes.append(checkbox)

                ctk.CTkLabel(
                    changes_frame,
                    text=item['name'],
                    font=row_font,
                    anchor="w"
                ).grid(row=i, column=1, sticky="w", padx=(0, 10), pady=2)

                ctk.CTkLabel(
                    changes_frame,
                    text=item['property'],
                    font=row_font,
                    anchor="w"
                ).grid(row=i, column=2, sticky="w", padx=(0, 10), pady=2)

                ctk.CTkLabel(
                    changes_frame,
                    text=item['value'],
                    font=row_font,
                    anchor="w"
                ).grid(row=i, column=3, sticky="w", padx=(0, 10), pady=2)

                new_entry = ctk.CTkEntry(
                    changes_frame,
                    textvariable=new_var,
                    font=row_font,
                    width=80,
                    height=28
                )
                new_entry.grid(row=i, column=4, sticky="w", pady=2)
                self.row_entries.append(new_entry)
            
            # Update select all checkbox state based on initial row states
            self._update_select_all_checkbox_state()
        else:
            no_changes_label = ctk.CTkLabel(
                changes_frame,
                text="No data found - ensure game files are imported and converted",
                text_color="gray",
                font=ctk.CTkFont(size=16)
            )
            no_changes_label.grid(row=0, column=0, columnspan=5, pady=20)

    def _on_select_all_toggle(self):
        """Handle select all button toggle - cycles between all checked and all unchecked."""
        # If currently none or mixed, select all. If all, deselect all.
        if self.select_all_state == "all":
            # Uncheck all
            for i, var in enumerate(self.row_checkbox_vars):
                var.set(False)
                self.row_entry_vars[i].set(self.row_values[i])
        else:
            # Check all
            for var in self.row_checkbox_vars:
                var.set(True)
        
        # Update button state
        self._update_select_all_checkbox_state()

    def _on_row_checkbox_toggle(self, idx: int):
        """Handle individual row checkbox toggle.
        
        Args:
            idx: Index of the row that was toggled.
        """
        if not self.row_checkbox_vars[idx].get():
            # Unchecked - set New to Value
            self.row_entry_vars[idx].set(self.row_values[idx])
        
        # Update header checkbox state based on row checkboxes
        self._update_select_all_checkbox_state()

    def _update_select_all_checkbox_state(self):
        """Update the select all button to reflect the state of row checkboxes."""
        if not self.row_checkbox_vars:
            return
        
        checked_count = sum(1 for var in self.row_checkbox_vars if var.get())
        total_count = len(self.row_checkbox_vars)
        
        if checked_count == 0:
            # None checked - show empty box
            self.select_all_state = "none"
            self.select_all_btn.configure(text="☐")
        elif checked_count == total_count:
            # All checked - show checked box
            self.select_all_state = "all"
            self.select_all_btn.configure(text="☑")
        else:
            # Mixed state - show box with dash
            self.select_all_state = "mixed"
            self.select_all_btn.configure(text="▣")

    def _on_save_click(self):
        """Handle Save button click - update the XML definition file."""
        if not hasattr(self, 'current_definition_path') or not self.current_definition_path:
            self.set_status_message("No definition file selected", is_error=True)
            return
        
        try:
            file_path = self.current_definition_path
            
            # Parse the existing XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Find the <mod> element
            mod_element = root.find('mod')
            if mod_element is None:
                self.set_status_message("No <mod> element found in definition file", is_error=True)
                return
            
            # Clear existing <change> elements
            for change in mod_element.findall('change'):
                mod_element.remove(change)
            
            # Add new <change> elements for checked rows
            changes_added = 0
            properties_used = {}  # Track property -> value for NONE fallback
            
            for i, checkbox_var in enumerate(self.row_checkbox_vars):
                prop_name = self.row_properties[i]
                new_value = self.row_entry_vars[i].get()
                
                # Track the first value seen for each property (for NONE fallback)
                if prop_name not in properties_used:
                    properties_used[prop_name] = new_value
                
                if checkbox_var.get():  # Only add if checked
                    row_name = self.row_names[i]
                    
                    change_elem = ET.SubElement(mod_element, 'change')
                    change_elem.set('item', row_name)
                    change_elem.set('property', prop_name)
                    change_elem.set('value', new_value)
                    changes_added += 1
            
            # If no items were checked, save NONE entries to preserve property/value
            if changes_added == 0 and properties_used:
                for prop_name, value in properties_used.items():
                    change_elem = ET.SubElement(mod_element, 'change')
                    change_elem.set('item', 'NONE')
                    change_elem.set('property', prop_name)
                    change_elem.set('value', value)
            
            # Format the XML with proper indentation
            self._indent_xml(root)
            
            # Write back to file
            tree.write(file_path, encoding='UTF-8', xml_declaration=True)
            
            if changes_added == 0 and properties_used:
                self.set_status_message(f"Saved template (no items selected) to {file_path.name}")
            else:
                self.set_status_message(f"Saved {changes_added} changes to {file_path.name}")
            
        except Exception as e:
            self.set_status_message(f"Error saving: {e}", is_error=True)

    def _indent_xml(self, elem, level=0):
        """Add proper indentation to XML elements.
        
        Args:
            elem: The XML element to indent.
            level: Current indentation level.
        """
        indent = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent

    def _create_toolbar_button(self, parent, icon_name: str, tooltip: str, command):
        """Create a toolbar button with icon.

        Args:
            parent: Parent widget.
            icon_name: Name of the icon file.
            tooltip: Tooltip text for the button.
            command: Command to execute when clicked.
        """
        icon_path = get_icon_path(icon_name)

        if icon_path.exists():
            try:
                img = Image.open(icon_path)
                icon_image = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=TOOLBAR_ICON_SIZE
                )
                btn = ctk.CTkButton(
                    parent,
                    image=icon_image,
                    text="",
                    width=50,
                    height=50,
                    fg_color="transparent",
                    hover_color=("gray75", "gray25"),
                    command=command
                )
            except Exception:
                # Fallback to text button
                btn = ctk.CTkButton(
                    parent,
                    text=tooltip[:3],
                    width=50,
                    height=50,
                    fg_color="transparent",
                    hover_color=("gray75", "gray25"),
                    command=command
                )
        else:
            # Fallback to text button with abbreviation
            btn = ctk.CTkButton(
                parent,
                text=tooltip[:3],
                width=50,
                height=50,
                fg_color="transparent",
                hover_color=("gray75", "gray25"),
                command=command
            )

        btn.pack(side="left", padx=5)

        # Store tooltip reference (for future tooltip implementation)
        btn._tooltip_text = tooltip

    def _run_import(self):
        """Run the retoc import process."""
        show_import_dialog(self)

    def _run_json_convert(self):
        """Run the JSON conversion process."""
        show_json_convert_dialog(self)

    def _launch_uassetgui(self):
        """Launch UAssetGUI from utilities directory."""
        utilities_dir = get_utilities_dir()
        exe_path = find_utility(utilities_dir, "UAssetGUI.exe")

        if exe_path:
            try:
                subprocess.Popen([str(exe_path)], cwd=str(utilities_dir))
            except Exception as e:
                self._show_error(f"Failed to launch UAssetGUI: {e}")
        else:
            self._show_error(f"UAssetGUI.exe not found in {utilities_dir}")

    def _launch_fmodel(self):
        """Launch FModel from utilities directory."""
        utilities_dir = get_utilities_dir()
        exe_path = find_utility(utilities_dir, "FModel.exe")

        if exe_path:
            try:
                subprocess.Popen([str(exe_path)], cwd=str(utilities_dir))
            except Exception as e:
                self._show_error(f"Failed to launch FModel: {e}")
        else:
            self._show_error(f"FModel.exe not found in {utilities_dir}")

    def _open_settings(self):
        """Open the settings/configuration dialog."""
        from src.ui.config_dialog import show_config_dialog
        show_config_dialog(self)

    def _open_about(self):
        """Open the Help About dialog."""
        show_about_dialog(self)

    def _show_error(self, message: str):
        """Show an error message dialog.

        Args:
            message: The error message to display.
        """
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Error")
        error_dialog.geometry("400x150")
        error_dialog.resizable(False, False)
        error_dialog.transient(self)
        error_dialog.grab_set()

        # Center on screen
        error_dialog.update_idletasks()
        x = (error_dialog.winfo_screenwidth() - 400) // 2
        y = (error_dialog.winfo_screenheight() - 150) // 2
        error_dialog.geometry(f"400x150+{x}+{y}")

        # Message
        msg_label = ctk.CTkLabel(
            error_dialog,
            text=message,
            wraplength=350,
            justify="center"
        )
        msg_label.pack(expand=True, padx=20, pady=20)

        # OK button
        ok_btn = ctk.CTkButton(
            error_dialog,
            text="OK",
            command=error_dialog.destroy,
            width=80
        )
        ok_btn.pack(pady=(0, 20))
