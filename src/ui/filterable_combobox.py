"""Filterable combobox widget for single-value selection with type-to-filter.

Provides a text entry with dropdown arrow that shows a scrollable list of options.
Typing in the entry filters the list case-insensitively. Clicking the arrow button
shows all options. Keyboard navigation (Up/Down/Enter/Escape) is supported.

Drop-in replacement for CTkComboBox with the same variable/values API.
"""

import customtkinter as ctk


class FilterableComboBox(ctk.CTkFrame):
    """Entry widget with filterable dropdown for single-value selection.

    Features:
        - Filters options as user types (case-insensitive partial match)
        - Shows all options on arrow button click
        - Keyboard navigation (Up/Down arrows, Enter to select, Escape to close)
        - Scrollable popup for large option lists
        - Drop-in replacement for CTkComboBox

    Args:
        parent: Parent widget
        variable: StringVar to bind to the entry
        values: List of possible option values
        width: Total widget width (default 350)
    """

    MAX_VISIBLE = 30
    DROPDOWN_GAP = 4  # pixels between entry and dropdown

    def __init__(self, parent, variable: ctk.StringVar, values: list[str],
                 width: int = 350, **kwargs):
        # Remove keys that CTkFrame doesn't accept
        kwargs.pop('command', None)
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.variable = variable
        self.all_values = list(values) if values else []
        self.dropdown_visible = False
        self.dropdown_window = None
        self.scroll_frame = None
        self.current_matches = []
        self.selected_index = -1
        self.item_buttons = []
        self._closing = False  # guard against re-entrant hide

        # Entry widget (fills remaining space)
        entry_width = max(width - 28, 100)
        self.entry = ctk.CTkEntry(self, textvariable=variable, width=entry_width)
        self.entry.pack(side="left", fill="x", expand=True)

        # Arrow button
        self.arrow_btn = ctk.CTkButton(
            self, text="\u25be", width=28, height=28,
            fg_color="transparent",
            hover_color=("gray80", "gray35"),
            text_color=("gray10", "gray90"),
            command=self._toggle_dropdown
        )
        self.arrow_btn.pack(side="left")

        # Bind events
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Down>", self._on_down_arrow)
        self.entry.bind("<Up>", self._on_up_arrow)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Escape>", self._on_escape)

    # -- Public API --

    def get(self) -> str:
        """Get the current value."""
        return self.variable.get()

    def set(self, value: str):
        """Set the current value."""
        self.variable.set(value)

    def update_values(self, new_values: list[str]):
        """Update the list of available options."""
        self.all_values = list(new_values) if new_values else []

    # -- Event handlers --

    def _on_key_release(self, event):
        """Filter dropdown on key release."""
        if event.keysym in ("Return", "Tab", "Escape", "Up", "Down"):
            return

        text = self.variable.get().strip()
        if text:
            self.current_matches = [
                v for v in self.all_values if text.lower() in v.lower()
            ][:self.MAX_VISIBLE]
        else:
            self.current_matches = self.all_values[:self.MAX_VISIBLE]

        if self.current_matches:
            self._show_dropdown()
        else:
            self._hide_dropdown()

    def _toggle_dropdown(self):
        """Toggle dropdown visibility (arrow button handler)."""
        if self.dropdown_visible:
            self._hide_dropdown()
        else:
            self.current_matches = self.all_values[:self.MAX_VISIBLE]
            if self.current_matches:
                self._show_dropdown()
            self.entry.focus_set()

    def _on_escape(self, _event=None):
        """Close dropdown on Escape key."""
        if self.dropdown_visible:
            self._hide_dropdown()
            return "break"
        return None

    # -- Dropdown management --

    def _show_dropdown(self):
        """Show or update the dropdown popup."""
        if self.dropdown_window:
            self._update_listbox()
            return

        self.dropdown_window = ctk.CTkToplevel(self)
        self.dropdown_window.withdraw()
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.attributes("-topmost", True)

        # Scrollable frame for option buttons
        popup_height = min(len(self.current_matches) * 28 + 4, 300)
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.dropdown_window,
            fg_color=("gray95", "gray20"),
            height=popup_height - 4
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=1, pady=1)

        self.item_buttons = []
        self._update_listbox()
        self._position_dropdown()
        self.dropdown_window.deiconify()
        self.dropdown_visible = True
        self.selected_index = -1

    def _update_listbox(self):
        """Rebuild the option buttons for current matches."""
        for btn in self.item_buttons:
            btn.destroy()
        self.item_buttons = []

        for match in self.current_matches:
            btn = ctk.CTkButton(
                self.scroll_frame,
                text=match,
                anchor="w",
                height=28,
                corner_radius=0,
                fg_color="transparent",
                hover_color=("gray80", "gray35"),
                text_color=("gray10", "gray90"),
                command=lambda m=match: self._select_item(m)
            )
            btn.pack(fill="x")
            self.item_buttons.append(btn)

        self._position_dropdown()

    def _position_dropdown(self):
        """Position popup below the entry with a gap, flipping above if near edge."""
        if not self.dropdown_window:
            return

        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height() + self.DROPDOWN_GAP
        width = max(self.winfo_width(), 300)
        height = min(len(self.current_matches) * 28 + 4, 300)

        screen_height = self.winfo_screenheight()
        if y + height > screen_height - 50:
            # Show above the entry with gap
            y = self.entry.winfo_rooty() - height - self.DROPDOWN_GAP

        self.dropdown_window.geometry(f"{width}x{height}+{x}+{y}")

    def _hide_dropdown(self, _event=None):
        """Destroy the dropdown popup."""
        if self._closing:
            return
        self._closing = True
        try:
            if self.dropdown_window:
                self.dropdown_window.destroy()
                self.dropdown_window = None
                self.scroll_frame = None
                self.item_buttons = []
            self.dropdown_visible = False
            self.selected_index = -1
        finally:
            self._closing = False

    # -- Selection --

    def _select_item(self, item: str):
        """Set the variable to the selected item and close dropdown."""
        self.variable.set(item)
        self._hide_dropdown()
        self.entry.focus_set()

    # -- Keyboard navigation --

    def _on_down_arrow(self, _event):
        """Move selection down, or open dropdown if closed."""
        if not self.dropdown_visible or not self.current_matches:
            self.current_matches = self.all_values[:self.MAX_VISIBLE]
            if self.current_matches:
                self._show_dropdown()
            return "break"

        self.selected_index = min(self.selected_index + 1, len(self.current_matches) - 1)
        self._highlight_selection()
        return "break"

    def _on_up_arrow(self, _event):
        """Move selection up."""
        if not self.dropdown_visible or not self.current_matches:
            return None
        self.selected_index = max(self.selected_index - 1, 0)
        self._highlight_selection()
        return "break"

    def _on_enter(self, _event):
        """Select the highlighted item on Enter."""
        if self.dropdown_visible and 0 <= self.selected_index < len(self.current_matches):
            self._select_item(self.current_matches[self.selected_index])
            return "break"
        self._hide_dropdown()
        return None

    def _highlight_selection(self):
        """Highlight the currently selected item button."""
        for i, btn in enumerate(self.item_buttons):
            if i == self.selected_index:
                btn.configure(fg_color=("gray75", "gray40"))
            else:
                btn.configure(fg_color="transparent")

    # -- Focus management --

    def _on_focus_out(self, _event):
        """Delay hide to allow clicking dropdown items."""
        self.after(200, self._check_focus_and_hide)

    def _check_focus_and_hide(self):
        """Hide dropdown if focus has moved outside this widget and its popup."""
        if not self.dropdown_visible:
            return
        try:
            focused = self.focus_get()
            # Keep open if focus is on our entry or arrow button
            if focused is self.entry or focused is self.arrow_btn:
                return
            # Keep open if focus is on the entry's inner widget
            if hasattr(self.entry, '_entry') and focused is self.entry._entry:
                return
        except (AttributeError, KeyError):
            pass
        self._hide_dropdown()
