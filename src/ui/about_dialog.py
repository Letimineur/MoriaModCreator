"""Help About dialog for Moria MOD Creator."""

import customtkinter as ctk
from pathlib import Path
from PIL import Image

# Application info
APP_NAME = "Moria MOD Creator"
APP_VERSION = "0.6"
APP_DATE = "February 2026"
APP_AUTHOR = "John B Owens II"
GITHUB_URL = "https://github.com/jbowensii/MoriaModCreator"
LICENSE_URL = "https://github.com/jbowensii/MoriaModCreator?tab=MIT-1-ov-file#"


class AboutDialog(ctk.CTkToplevel):
    """About dialog showing application information with tabbed content."""

    def __init__(self, parent: ctk.CTk):
        super().__init__(parent)

        self.title("Help - Moria MOD Creator")
        self.geometry("700x500")
        self.resizable(True, True)
        self.minsize(600, 400)

        # Make this dialog modal
        self.transient(parent)
        self.grab_set()

        # Center the dialog on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 700) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"700x500+{x}+{y}")

        # Load images
        self._load_images()

        # Current active tab
        self._active_tab = "main"

        self._create_widgets()

        # Handle window close button
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Bind resize event
        self.bind("<Configure>", self._on_resize)

    def _load_images(self):
        """Load background and overlay images."""
        assets_path = Path(__file__).parent.parent.parent / "assets" / "images"

        # Load background image
        bg_path = assets_path / "background.png"
        if bg_path.exists():
            self._bg_image_pil = Image.open(bg_path)
        else:
            self._bg_image_pil = None

        # Load overlay image (Mereak Firmaxe)
        overlay_path = assets_path / "Mereak Firmaxe.png"
        if overlay_path.exists():
            self._overlay_image_pil = Image.open(overlay_path)
        else:
            self._overlay_image_pil = None

        # CTkImage references (will be created on resize)
        self._bg_image = None
        self._overlay_image = None

    def _create_widgets(self):
        """Create the dialog widgets."""
        # Main container
        self._container = ctk.CTkFrame(self, fg_color="transparent")
        self._container.pack(fill="both", expand=True)

        # Background label (will hold the background image)
        self._bg_label = ctk.CTkLabel(self._container, text="")
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Content frame overlaid on background
        self._content_frame = ctk.CTkFrame(
            self._container,
            fg_color=("gray90", "gray17"),
            corner_radius=10
        )
        self._content_frame.place(relx=0.02, rely=0.02, relwidth=0.60, relheight=0.96)

        # Overlay image on the right
        self._overlay_label = ctk.CTkLabel(self._container, text="")
        self._overlay_label.place(relx=0.62, rely=0.1, relwidth=0.36, relheight=0.8)

        # Create content inside content frame
        self._create_content()

    def _create_content(self):
        """Create the content inside the content frame."""
        # Button bar at top
        btn_frame = ctk.CTkFrame(self._content_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)

        self._main_btn = ctk.CTkButton(
            btn_frame,
            text="Main",
            command=lambda: self._show_tab("main"),
            width=80,
            fg_color="#1a5fb4",
            hover_color="#1c4a8a"
        )
        self._main_btn.pack(side="left", padx=(0, 5))

        self._about_btn = ctk.CTkButton(
            btn_frame,
            text="About",
            command=lambda: self._show_tab("about"),
            width=80,
            fg_color="gray50",
            hover_color="gray40"
        )
        self._about_btn.pack(side="left", padx=5)

        self._credits_btn = ctk.CTkButton(
            btn_frame,
            text="Credits",
            command=lambda: self._show_tab("credits"),
            width=80,
            fg_color="gray50",
            hover_color="gray40"
        )
        self._credits_btn.pack(side="left", padx=5)

        # Close button on the right
        close_btn = ctk.CTkButton(
            btn_frame,
            text="Close",
            command=self._on_close,
            width=80,
            fg_color="#c01c28",
            hover_color="#a01020"
        )
        close_btn.pack(side="right")

        # Content area (scrollable)
        self._text_frame = ctk.CTkScrollableFrame(
            self._content_frame,
            fg_color="transparent"
        )
        self._text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Show main tab by default
        self._show_tab("main")

    def _show_tab(self, tab_name: str):
        """Switch to the specified tab."""
        self._active_tab = tab_name

        # Update button colors
        active_color = "#1a5fb4"
        inactive_color = "gray50"

        self._main_btn.configure(
            fg_color=active_color if tab_name == "main" else inactive_color
        )
        self._about_btn.configure(
            fg_color=active_color if tab_name == "about" else inactive_color
        )
        self._credits_btn.configure(
            fg_color=active_color if tab_name == "credits" else inactive_color
        )

        # Clear current content
        for widget in self._text_frame.winfo_children():
            widget.destroy()

        # Show appropriate content
        if tab_name == "main":
            self._show_main_content()
        elif tab_name == "about":
            self._show_about_content()
        elif tab_name == "credits":
            self._show_credits_content()

    def _show_main_content(self):
        """Display the main disclaimer content."""
        title = ctk.CTkLabel(
            self._text_frame,
            text="DISCLAIMER OF WARRANTY",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#c01c28"
        )
        title.pack(pady=(10, 20))

        disclaimer_text = (
            "Software is provided \"as is,\" without warranties of any kind, "
            "express or implied. Users accept all risks associated with using "
            "the software, including its quality, performance, and accuracy.\n\n"
            "⚠️  Mods can be dangerous!\n\n"
            "Please backup your game and character files often.\n\n"
            "If you use mods, do not report game or system crashes to the "
            "game developers.\n\n"
            "Thank you for understanding."
        )

        content = ctk.CTkLabel(
            self._text_frame,
            text=disclaimer_text,
            font=ctk.CTkFont(size=13),
            justify="left",
            wraplength=350
        )
        content.pack(pady=10, padx=10)

    def _show_about_content(self):
        """Display the about information."""
        # App name
        name_label = ctk.CTkLabel(
            self._text_frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=22, weight="bold")
        )
        name_label.pack(pady=(10, 5))

        # Version and date
        version_label = ctk.CTkLabel(
            self._text_frame,
            text=f"Version {APP_VERSION}  •  {APP_DATE}",
            font=ctk.CTkFont(size=14)
        )
        version_label.pack(pady=5)

        # Author
        author_label = ctk.CTkLabel(
            self._text_frame,
            text=f"Created by {APP_AUTHOR}",
            font=ctk.CTkFont(size=13)
        )
        author_label.pack(pady=10)

        # Separator
        sep = ctk.CTkFrame(self._text_frame, height=2, fg_color="gray50")
        sep.pack(fill="x", padx=20, pady=15)

        # GitHub link
        github_frame = ctk.CTkFrame(self._text_frame, fg_color="transparent")
        github_frame.pack(pady=5)

        github_icon = ctk.CTkLabel(
            github_frame,
            text="📦 GitHub Repository:",
            font=ctk.CTkFont(size=12)
        )
        github_icon.pack(side="left")

        github_link = ctk.CTkLabel(
            github_frame,
            text=GITHUB_URL,
            font=ctk.CTkFont(size=11),
            text_color="#3584e4",
            cursor="hand2"
        )
        github_link.pack(side="left", padx=(5, 0))
        github_link.bind("<Button-1>", lambda e: self._open_url(GITHUB_URL))

        # License link
        license_frame = ctk.CTkFrame(self._text_frame, fg_color="transparent")
        license_frame.pack(pady=5)

        license_icon = ctk.CTkLabel(
            license_frame,
            text="📄 MIT License:",
            font=ctk.CTkFont(size=12)
        )
        license_icon.pack(side="left")

        license_link = ctk.CTkLabel(
            license_frame,
            text="View License",
            font=ctk.CTkFont(size=11, underline=True),
            text_color="#3584e4",
            cursor="hand2"
        )
        license_link.pack(side="left", padx=(5, 0))
        license_link.bind("<Button-1>", lambda e: self._open_url(LICENSE_URL))

        # Description
        desc_label = ctk.CTkLabel(
            self._text_frame,
            text=(
                "\nA tool for creating and managing mods for\n"
                "Lord of the Rings: Return to Moria"
            ),
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        desc_label.pack(pady=15)

    def _show_credits_content(self):
        """Display the credits information."""
        title = ctk.CTkLabel(
            self._text_frame,
            text="Credits & Acknowledgments",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(10, 20))

        credits_text = (
            "Special thanks to the following people and projects:\n\n"
            "• Community contributors (to be added)\n\n"
            "─────────────────────────────\n\n"
            "Third-Party Tools:\n"
            "• FModel - UE4/UE5 asset viewer\n"
            "• UAssetGUI - Unreal Engine asset editor\n"
            "• retoc - Table of contents rebuilder\n"
            "• ZenTools - Zen asset tools\n\n"
            "─────────────────────────────\n\n"
            "Libraries:\n"
            "• CustomTkinter - Modern UI toolkit\n"
            "• Pillow - Image processing\n"
            "• Python - Programming language\n"
        )

        content = ctk.CTkLabel(
            self._text_frame,
            text=credits_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=350
        )
        content.pack(pady=10, padx=10)

    def _open_url(self, url: str):
        """Open a URL in the default browser."""
        import webbrowser
        webbrowser.open(url)

    def _on_resize(self, event=None):
        """Handle window resize to update images."""
        if event and event.widget == self:
            self._update_images()

    def _update_images(self):
        """Update images to fit current window size."""
        try:
            width = self.winfo_width()
            height = self.winfo_height()

            if width < 10 or height < 10:
                return

            # Update background image
            if self._bg_image_pil:
                self._bg_image = ctk.CTkImage(
                    light_image=self._bg_image_pil,
                    dark_image=self._bg_image_pil,
                    size=(width, height)
                )
                self._bg_label.configure(image=self._bg_image)

            # Update overlay image (maintain aspect ratio)
            if self._overlay_image_pil:
                overlay_width = int(width * 0.35)
                overlay_height = int(height * 0.75)

                # Calculate aspect ratio
                orig_w, orig_h = self._overlay_image_pil.size
                aspect = orig_w / orig_h

                # Fit within bounds
                if overlay_width / aspect <= overlay_height:
                    new_w = overlay_width
                    new_h = int(overlay_width / aspect)
                else:
                    new_h = overlay_height
                    new_w = int(overlay_height * aspect)

                self._overlay_image = ctk.CTkImage(
                    light_image=self._overlay_image_pil,
                    dark_image=self._overlay_image_pil,
                    size=(new_w, new_h)
                )
                self._overlay_label.configure(image=self._overlay_image)

        except Exception:
            pass  # Ignore errors during resize

    def _on_close(self):
        """Handle close button click."""
        self.destroy()


def show_about_dialog(parent: ctk.CTk) -> None:
    """Show the about dialog.

    Args:
        parent: The parent window.
    """
    dialog = AboutDialog(parent)
    # Trigger initial image update after window is displayed
    dialog.after(100, dialog._update_images)
    parent.wait_window(dialog)
