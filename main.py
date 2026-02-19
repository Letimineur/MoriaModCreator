"""Main entry point for Moria MOD Creator."""

import logging
import customtkinter as ctk

from src.config import (
    config_exists, get_color_scheme, apply_color_scheme,
    get_appdata_dir, get_debug_mode,
)
from src.ui.config_dialog import show_config_dialog
from src.ui.main_window import MainWindow

# Configure logging - only for our application
logging.basicConfig(
    level=logging.WARNING,  # Set root logger to WARNING to suppress library debug messages
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Our logger stays at DEBUG

# Enable INFO logging for all src.* modules so build_manager logs are visible
logging.getLogger('src').setLevel(logging.INFO)

# Create/clear application log file in AppData (starts at WARNING level;
# upgraded to DEBUG when the debug config flag is True).
_log_path = get_appdata_dir() / 'MoriaMODCreator.log'
_file_handler = logging.FileHandler(_log_path, mode='w', encoding='utf-8')
_file_handler.setLevel(logging.WARNING)
_file_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logging.getLogger().addHandler(_file_handler)


def _apply_debug_mode():
    """Check the debug config flag and adjust file logging level accordingly."""
    if get_debug_mode():
        _file_handler.setLevel(logging.DEBUG)
        logging.getLogger('src').setLevel(logging.DEBUG)
        logger.info("Debug mode ON — verbose logging to %s", _log_path)
    else:
        _file_handler.setLevel(logging.WARNING)
        logging.getLogger('src').setLevel(logging.INFO)


def main():
    """Main application entry point."""
    # Apply color scheme from config or default to system
    config_found = config_exists()
    if config_found:
        apply_color_scheme(get_color_scheme())
        _apply_debug_mode()
        logger.info("Application starting — config loaded")
    else:
        ctk.set_appearance_mode("system")

    # Check if first run (no config exists)
    if not config_found:
        logger.info("First run — showing config dialog")
        # Create a temporary root for the config dialog
        temp_root = ctk.CTk()
        temp_root.withdraw()

        # Show configuration dialog
        if not show_config_dialog(temp_root):
            logger.info("User cancelled config dialog — exiting")
            temp_root.destroy()
            return

        # Apply the newly saved color scheme and debug mode
        apply_color_scheme(get_color_scheme())
        _apply_debug_mode()
        temp_root.destroy()

    # Set default color theme
    ctk.set_default_color_theme("blue")

    # Create and show the main window
    logger.info("Creating main window")
    app = MainWindow()
    logger.info("Starting mainloop")
    app.mainloop()
    logger.info("Application exiting")


if __name__ == "__main__":
    main()
