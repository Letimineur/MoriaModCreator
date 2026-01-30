"""Help About dialog for Moria MOD Creator."""

import customtkinter as ctk


class AboutDialog(ctk.CTkToplevel):
    """About dialog showing application information."""

    def __init__(self, parent: ctk.CTk):
        super().__init__(parent)

        self.title("About Moria MOD Creator")
        self.geometry("400x300")
        self.resizable(False, False)

        # Make this dialog modal
        self.transient(parent)
        self.grab_set()

        # Center the dialog on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 300) // 2
        self.geometry(f"400x300+{x}+{y}")

        self._create_widgets()

        # Handle window close button
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        """Create the dialog widgets."""
        # Main frame with padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Configure grid
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Moria MOD Creator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        # Version and info
        info_text = (
            "Version 1.0.0\n\n"
            "A tool for creating and managing mods for\n"
            "Lord of the Rings: Return to Moria\n\n"
            "Create loadable patterns to modify game files\n"
            "and enhance your gaming experience."
        )

        info_label = ctk.CTkLabel(
            main_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        info_label.grid(row=1, column=0)

        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            command=self._on_close,
            width=100
        )
        close_btn.grid(row=2, column=0, pady=(20, 0))

    def _on_close(self):
        """Handle close button click."""
        self.destroy()


def show_about_dialog(parent: ctk.CTk) -> None:
    """Show the about dialog.

    Args:
        parent: The parent window.
    """
    dialog = AboutDialog(parent)
    parent.wait_window(dialog)
