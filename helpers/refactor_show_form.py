"""Refactor _show_form into per-type form dispatching."""
import re

filepath = r"c:\Users\johnb\OneDrive\Documents\Projects\Moria MOD Creator\src\ui\buildings_view.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the old _show_form method - from "    def _show_form(self):" to "    def _create_action_buttons"
old_start = "    def _show_form(self):"
old_end = "    def _create_action_buttons(self):"

start_idx = content.index(old_start)
end_idx = content.index(old_end)

old_method = content[start_idx:end_idx]

new_code = '''    def _show_form(self):
        """Render the editable form, dispatching to per-type renderer."""
        # Hide placeholder and show form widgets
        self.placeholder_label.pack_forget()

        # Clear existing form content
        for widget in self.form_content.winfo_children():
            widget.destroy()
        self.form_content.pack(fill="both", expand=True)

        # Update header with def file metadata
        title = self.current_def_data.get("title", "")
        author = self.current_def_data.get("author", "")
        description = self.current_def_data.get("description", "")
        if title or author:
            header_text = title or "(Untitled)"
            construction_json = self.current_def_data.get("construction_json")
            construction_name = (construction_json.get("Name", "")
                                 if construction_json else "")
            game_display = (self._lookup_game_name(construction_name)
                            if construction_name else "")
            if game_display and game_display != construction_name and game_display != title:
                header_text = f"{header_text}  \\u2014  {game_display}"
            self.header_title.configure(text=header_text)
            self.header_author.configure(text=f"by {author}" if author else "")
            self.header_description.configure(text=description or "")
            self.form_header.grid()
        else:
            self.form_header.grid_remove()

        # Show footer with save/revert/delete buttons
        self.form_footer.grid()

        self.form_vars.clear()
        self.material_rows.clear()
        self.sandbox_material_rows.clear()

        recipe_json = self.current_def_data.get("recipe_json")
        construction_json = self.current_def_data.get("construction_json")

        # Dispatch to per-type form renderer
        mode = self.view_mode or 'buildings'
        has_data = False

        if mode == 'buildings':
            has_data = self._show_buildings_form(recipe_json, construction_json)
        elif mode == 'weapons':
            has_data = self._show_weapon_form(recipe_json, construction_json)
        elif mode == 'armor':
            has_data = self._show_armor_form(recipe_json, construction_json)
        elif mode == 'tools':
            has_data = self._show_tool_form(recipe_json, construction_json)
        elif mode == 'items':
            has_data = self._show_items_form(recipe_json, construction_json)
        elif mode == 'flora':
            has_data = self._show_flora_form(construction_json)
        elif mode == 'loot':
            has_data = self._show_loot_form(construction_json)

        if not has_data:
            ctk.CTkLabel(
                self.form_content, text="No data found for this item.",
                text_color="gray"
            ).pack(anchor="center", pady=40)

    # ----- Per-type form renderers -----

    def _show_buildings_form(self, recipe_json, construction_json):
        """Render buildings form (construction recipe + construction definition)."""
        has_data = False

        if recipe_json and isinstance(recipe_json, dict):
            has_data = True
            recipe = extract_recipe_fields(recipe_json)

            self._create_section_header("Construction Recipe", "#FF9800")

            self._create_text_field("Name", recipe["Name"], label="Row Name")
            self._create_text_field(
                "ResultConstructionHandle", recipe["ResultConstructionHandle"],
                label="Result Construction", autocomplete_key="ResultConstructions"
            )

            row1 = ctk.CTkFrame(self.form_content, fg_color="transparent")
            row1.pack(fill="x", pady=3)
            self._create_dropdown_field_inline(
                row1, "BuildProcess", recipe["BuildProcess"],
                self._get_options("Enum_BuildProcess", DEFAULT_BUILD_PROCESS)
            )
            self._create_dropdown_field_inline(
                row1, "PlacementType", recipe["PlacementType"],
                self._get_options("Enum_PlacementType", DEFAULT_PLACEMENT)
            )

            row2 = ctk.CTkFrame(self.form_content, fg_color="transparent")
            row2.pack(fill="x", pady=3)
            self._create_dropdown_field_inline(
                row2, "LocationRequirement", recipe["LocationRequirement"],
                self._get_options("Enum_LocationRequirement", DEFAULT_LOCATION)
            )
            self._create_dropdown_field_inline(
                row2, "FoundationRule", recipe["FoundationRule"],
                self._get_options("Enum_FoundationRule", DEFAULT_FOUNDATION_RULE)
            )

            row3 = ctk.CTkFrame(self.form_content, fg_color="transparent")
            row3.pack(fill="x", pady=3)
            self._create_dropdown_field_inline(
                row3, "MonumentType", recipe["MonumentType"],
                self._get_options("Enum_MonumentType", DEFAULT_MONUMENT_TYPE)
            )

            self._create_subsection_header("Placement Options")
            bool_row1 = ctk.CTkFrame(self.form_content, fg_color="transparent")
            bool_row1.pack(fill="x", pady=4)
            for bf in ["bOnWall", "bOnFloor", "bPlaceOnWater", "bOverrideRotation"]:
                self._create_checkbox_field(bool_row1, bf, recipe[bf])

            bool_row2 = ctk.CTkFrame(self.form_content, fg_color="transparent")
            bool_row2.pack(fill="x", pady=4)
            for bf in ["bAllowRefunds", "bAutoFoundation", "bInheritAutoFoundationStability", "bOnlyOnVoxel"]:
                self._create_checkbox_field(bool_row2, bf, recipe[bf])

            bool_row3 = ctk.CTkFrame(self.form_content, fg_color="transparent")
            bool_row3.pack(fill="x", pady=4)
            for bf in ["bIsBlockedByNearbySettlementStones", "bIsBlockedByNearbyRavenConstructions"]:
                self._create_checkbox_field(bool_row3, bf, recipe[bf])

            self._create_subsection_header("Numeric Properties")
            self._create_text_field(
                "MaxAllowedPenetrationDepth", str(recipe["MaxAllowedPenetrationDepth"]),
                label="Max Penetration Depth", width=200
            )
            self._create_text_field(
                "RequireNearbyRadius", str(recipe["RequireNearbyRadius"]),
                label="Require Nearby Radius", width=200
            )
            self._create_text_field(
                "CameraStateOverridePriority", str(recipe["CameraStateOverridePriority"]),
                label="Camera Priority", width=200
            )

            self._render_materials_section(recipe)
            self._render_unlocks_section(recipe)
            self._render_sandbox_section(recipe)

            self._create_dropdown_field(
                "Recipe_EnabledState", recipe["EnabledState"],
                DEFAULT_ENABLED_STATE, label="Recipe Enabled State"
            )

        if construction_json and isinstance(construction_json, dict):
            has_data = True
            construction = extract_construction_fields(construction_json)
            self._render_construction_definition(construction)

        return has_data

    def _render_materials_section(self, recipe):
        """Render required materials with add/remove buttons."""
        self._create_subsection_header("Required Materials")
        add_mat_btn = ctk.CTkButton(
            self.form_content, text="+ Add Material", width=120, height=28,
            fg_color="#4CAF50", hover_color="#45a049",
            command=self._add_new_material_row
        )
        add_mat_btn.pack(anchor="w", pady=(0, 5))

        self.materials_frame = ctk.CTkFrame(self.form_content, fg_color="transparent")
        self.materials_frame.pack(fill="x", pady=5)
        for mat in recipe["Materials"]:
            self._add_material_row(mat["Material"], mat["Amount"])

        self._create_text_field(
            "DefaultRequiredConstructions",
            ", ".join(recipe["DefaultRequiredConstructions"]),
            label="Required Constructions", autocomplete_key="Constructions"
        )

    def _render_unlocks_section(self, recipe):
        """Render default unlocks subsection."""
        self._create_subsection_header("Default Unlocks")
        self._create_dropdown_field(
            "DefaultUnlocks_UnlockType", recipe["DefaultUnlocks_UnlockType"],
            self._get_options("Enum_EMorRecipeUnlockType", DEFAULT_UNLOCK_TYPE),
            label="Unlock Type"
        )
        self._create_text_field(
            "DefaultUnlocks_NumFragments", str(recipe["DefaultUnlocks_NumFragments"]),
            label="Num Fragments", width=200
        )
        self._create_text_field(
            "DefaultUnlocks_RequiredItems",
            ", ".join(recipe["DefaultUnlocks_RequiredItems"]),
            label="Required Items", autocomplete_key="AllValues"
        )
        self._create_text_field(
            "DefaultUnlocks_RequiredConstructions",
            ", ".join(recipe["DefaultUnlocks_RequiredConstructions"]),
            label="Required Constructions", autocomplete_key="AllValues"
        )
        self._create_text_field(
            "DefaultUnlocks_RequiredFragments",
            ", ".join(recipe["DefaultUnlocks_RequiredFragments"]),
            label="Required Fragments", autocomplete_key="AllValues"
        )

    def _render_sandbox_section(self, recipe):
        """Render sandbox overrides subsection."""
        self._create_subsection_header("Sandbox Overrides")
        sandbox_bool_frame = ctk.CTkFrame(self.form_content, fg_color="transparent")
        sandbox_bool_frame.pack(fill="x", pady=4)
        self._create_checkbox_field(sandbox_bool_frame, "bHasSandboxRequirementsOverride",
                                    recipe["bHasSandboxRequirementsOverride"])
        self._create_checkbox_field(sandbox_bool_frame, "bHasSandboxUnlockOverride",
                                    recipe["bHasSandboxUnlockOverride"])

        self._create_dropdown_field(
            "SandboxUnlocks_UnlockType", recipe["SandboxUnlocks_UnlockType"],
            self._get_options("Enum_EMorRecipeUnlockType", DEFAULT_UNLOCK_TYPE),
            label="Sandbox Unlock Type"
        )
        self._create_text_field(
            "SandboxUnlocks_NumFragments", str(recipe["SandboxUnlocks_NumFragments"]),
            label="Sandbox Num Fragments", width=200
        )
        self._create_text_field(
            "SandboxUnlocks_RequiredItems",
            ", ".join(recipe["SandboxUnlocks_RequiredItems"]),
            label="Sandbox Required Items", autocomplete_key="AllValues"
        )
        self._create_text_field(
            "SandboxUnlocks_RequiredConstructions",
            ", ".join(recipe.get("SandboxUnlocks_RequiredConstructions", [])),
            label="Sandbox Unlock Req. Constructions", autocomplete_key="AllValues"
        )
        self._create_text_field(
            "SandboxUnlocks_RequiredFragments",
            ", ".join(recipe.get("SandboxUnlocks_RequiredFragments", [])),
            label="Sandbox Unlock Req. Fragments", autocomplete_key="AllValues"
        )

        self._create_subsection_header("Sandbox Required Materials")
        add_sandbox_mat_btn = ctk.CTkButton(
            self.form_content, text="+ Add Sandbox Material", width=160, height=28,
            fg_color="#4CAF50", hover_color="#45a049",
            command=self._add_new_sandbox_material_row
        )
        add_sandbox_mat_btn.pack(anchor="w", pady=(0, 5))

        self.sandbox_materials_frame = ctk.CTkFrame(self.form_content, fg_color="transparent")
        sandbox_mats = recipe.get("SandboxRequiredMaterials", [])
        if sandbox_mats:
            self.sandbox_materials_frame.pack(fill="x", pady=(0, 5))
            for mat in sandbox_mats:
                self._add_sandbox_material_row(mat["Material"], mat["Amount"])

        self._create_text_field(
            "SandboxRequiredConstructions",
            ", ".join(recipe.get("SandboxRequiredConstructions", [])),
            label="Sandbox Required Constructions", autocomplete_key="Constructions"
        )

    def _render_construction_definition(self, construction):
        """Render construction definition section (shared by buildings)."""
        self._create_section_header("Construction Definition", "#4CAF50")

        self._create_text_field("Construction_Name", construction["Name"], label="Row Name")
        self._create_text_field("DisplayName", construction["DisplayName"], label="Display Name")
        self._create_text_field("Description", construction["Description"])
        self._create_text_field("Actor", construction["Actor"],
                                label="Actor Path", autocomplete_key="Actors")
        icon_val = construction.get("Icon")
        self._create_text_field(
            "Icon", str(icon_val) if icon_val is not None else "",
            label="Icon (Import Index)", readonly=True
        )
        self._create_dropdown_field(
            "Tags",
            construction["Tags"][0] if construction["Tags"] else "",
            self._get_options("Tags", []),
            label="Category Tag"
        )
        self._create_text_field(
            "BackwardCompatibilityActors",
            ", ".join(construction["BackwardCompatibilityActors"]),
            label="Backward Compat Actors", autocomplete_key="Actors"
        )
        self._create_dropdown_field(
            "Construction_EnabledState", construction["EnabledState"],
            DEFAULT_ENABLED_STATE, label="Construction Enabled State"
        )

    def _render_item_recipe_section(self, recipe_json):
        """Render item recipe section (shared by weapons, armor, tools, items)."""
        recipe = extract_item_recipe_fields(recipe_json)

        self._create_section_header("Item Recipe", "#FF9800")

        self._create_text_field("Name", recipe["Name"], label="Row Name")
        self._create_text_field(
            "ResultItemHandle", recipe["ResultItemHandle"],
            label="Result Item", autocomplete_key="AllValues"
        )
        self._create_text_field(
            "ResultItemCount", str(recipe.get("ResultItemCount", 1)),
            label="Result Count", width=200
        )
        self._create_text_field(
            "CraftTimeSeconds", str(recipe.get("CraftTimeSeconds", 0.0)),
            label="Craft Time (s)", width=200
        )

        # Booleans
        bool_frame = ctk.CTkFrame(self.form_content, fg_color="transparent")
        bool_frame.pack(fill="x", pady=4)
        self._create_checkbox_field(bool_frame, "bCanBePinned", recipe.get("bCanBePinned", True))
        self._create_checkbox_field(bool_frame, "bNpcOnlyRecipe", recipe.get("bNpcOnlyRecipe", False))

        self._render_materials_section(recipe)
        self._render_unlocks_section(recipe)
        self._render_sandbox_section(recipe)

        self._create_dropdown_field(
            "Recipe_EnabledState", recipe["EnabledState"],
            DEFAULT_ENABLED_STATE, label="Recipe Enabled State"
        )

    def _render_common_item_fields(self, fields, section_title, section_color):
        """Render common item definition fields (display, inventory, tags)."""
        self._create_section_header(section_title, section_color)

        self._create_text_field("Def_Name", fields["Name"], label="Row Name", readonly=True)
        self._create_text_field("DisplayName", fields["DisplayName"], label="Display Name")
        self._create_text_field("Description", fields.get("Description", ""))
        self._create_text_field("Actor", fields.get("Actor", ""),
                                label="Actor Path", autocomplete_key="Actors")
        if "Icon" in fields:
            self._create_text_field("Icon", fields["Icon"], label="Icon Path", readonly=True)

        # Tags
        tags = fields.get("Tags", [])
        self._create_dropdown_field(
            "Tags",
            tags[0] if tags else "",
            self._get_options("Tags", []),
            label="Category Tag"
        )

        # Inventory
        self._create_subsection_header("Inventory")
        self._create_dropdown_field(
            "Portability", fields.get("Portability", "EItemPortability::Storable"),
            ["EItemPortability::Storable", "EItemPortability::NotStorable",
             "EItemPortability::Holdable"],
            label="Portability"
        )
        inv_row = ctk.CTkFrame(self.form_content, fg_color="transparent")
        inv_row.pack(fill="x", pady=3)
        for col in range(3):
            inv_row.grid_columnconfigure(col, weight=1)
        for i, (key, label) in enumerate([
            ("MaxStackSize", "Max Stack"), ("SlotSize", "Slot Size"),
            ("BaseTradeValue", "Trade Value")
        ]):
            frame = ctk.CTkFrame(inv_row, fg_color="transparent")
            frame.grid(row=0, column=i, sticky="ew", padx=2)
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11),
                         width=80, anchor="w").pack(side="left")
            var = ctk.StringVar(value=str(fields.get(key, 0)))
            self.form_vars[key] = var
            ctk.CTkEntry(frame, textvariable=var, width=80).pack(side="left", padx=2)

        self._create_dropdown_field(
            "Def_EnabledState", fields["EnabledState"],
            DEFAULT_ENABLED_STATE, label="Definition Enabled State"
        )

    def _show_weapon_form(self, recipe_json, definition_json):
        """Render weapon form (item recipe + weapon definition)."""
        has_data = False

        if recipe_json and isinstance(recipe_json, dict):
            has_data = True
            self._render_item_recipe_section(recipe_json)

        if definition_json and isinstance(definition_json, dict):
            has_data = True
            w = extract_weapon_fields(definition_json)

            self._create_section_header("Weapon Definition", "#9C27B0")

            self._create_text_field("Def_Name", w["Name"], label="Row Name", readonly=True)

            # Combat stats
            self._create_subsection_header("Combat Stats")
            self._create_text_field("DamageType", w["DamageType"], label="Damage Type",
                                    autocomplete_key="DamageTypes")
            stats_row1 = ctk.CTkFrame(self.form_content, fg_color="transparent")
            stats_row1.pack(fill="x", pady=3)
            for col in range(4):
                stats_row1.grid_columnconfigure(col, weight=1)
            for i, (key, label) in enumerate([
                ("Damage", "Damage"), ("Speed", "Speed"),
                ("Durability", "Durability"), ("Tier", "Tier")
            ]):
                frame = ctk.CTkFrame(stats_row1, fg_color="transparent")
                frame.grid(row=0, column=i, sticky="ew", padx=2)
                ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11),
                             width=70, anchor="w").pack(side="left")
                var = ctk.StringVar(value=str(w[key]))
                self.form_vars[key] = var
                ctk.CTkEntry(frame, textvariable=var, width=70).pack(side="left", padx=2)

            stats_row2 = ctk.CTkFrame(self.form_content, fg_color="transparent")
            stats_row2.pack(fill="x", pady=3)
            for col in range(4):
                stats_row2.grid_columnconfigure(col, weight=1)
            for i, (key, label) in enumerate([
                ("ArmorPenetration", "Armor Pen"),
                ("StaminaCost", "Stamina Cost"),
                ("EnergyCost", "Energy Cost"),
                ("BlockDamageReduction", "Block Reduction")
            ]):
                frame = ctk.CTkFrame(stats_row2, fg_color="transparent")
                frame.grid(row=0, column=i, sticky="ew", padx=2)
                ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11),
                             width=80, anchor="w").pack(side="left")
                var = ctk.StringVar(value=str(w[key]))
                self.form_vars[key] = var
                ctk.CTkEntry(frame, textvariable=var, width=70).pack(side="left", padx=2)

            # Repair cost
            if w["InitialRepairCost"]:
                self._create_subsection_header("Repair Cost")
                self.materials_frame = ctk.CTkFrame(self.form_content, fg_color="transparent")
                self.materials_frame.pack(fill="x", pady=5)
                for mat in w["InitialRepairCost"]:
                    self._add_material_row(mat["Material"], mat["Amount"])

            # Display
            self._create_subsection_header("Display")
            self._create_text_field("DisplayName", w["DisplayName"], label="Display Name")
            self._create_text_field("Description", w["Description"])
            self._create_text_field("Actor", w["Actor"],
                                    label="Actor Path", autocomplete_key="Actors")
            self._create_text_field("Icon", w["Icon"], label="Icon Path", readonly=True)

            # Tags & inventory
            tags = w.get("Tags", [])
            self._create_dropdown_field(
                "Tags", tags[0] if tags else "",
                self._get_options("Tags", []), label="Category Tag"
            )

            self._create_subsection_header("Inventory")
            self._create_dropdown_field(
                "Portability", w.get("Portability", "EItemPortability::Storable"),
                ["EItemPortability::Storable", "EItemPortability::NotStorable",
                 "EItemPortability::Holdable"], label="Portability"
            )
            inv_row = ctk.CTkFrame(self.form_content, fg_color="transparent")
            inv_row.pack(fill="x", pady=3)
            for col in range(3):
                inv_row.grid_columnconfigure(col, weight=1)
            for i, (key, lbl) in enumerate([
                ("MaxStackSize", "Max Stack"), ("SlotSize", "Slot Size"),
                ("BaseTradeValue", "Trade Value")
            ]):
                frame = ctk.CTkFrame(inv_row, fg_color="transparent")
                frame.grid(row=0, column=i, sticky="ew", padx=2)
                ctk.CTkLabel(frame, text=lbl, font=ctk.CTkFont(size=11),
                             width=80, anchor="w").pack(side="left")
                var = ctk.StringVar(value=str(w.get(key, 0)))
                self.form_vars[key] = var
                ctk.CTkEntry(frame, textvariable=var, width=80).pack(side="left", padx=2)

            self._create_dropdown_field(
                "Def_EnabledState", w["EnabledState"],
                DEFAULT_ENABLED_STATE, label="Definition Enabled State"
            )

        return has_data

    def _show_armor_form(self, recipe_json, definition_json):
        """Render armor form (item recipe + armor definition)."""
        has_data = False

        if recipe_json and isinstance(recipe_json, dict):
            has_data = True
            self._render_item_recipe_section(recipe_json)

        if definition_json and isinstance(definition_json, dict):
            has_data = True
            a = extract_armor_fields(definition_json)

            self._create_section_header("Armor Definition", "#FF9800")

            self._create_text_field("Def_Name", a["Name"], label="Row Name", readonly=True)

            # Defense stats
            self._create_subsection_header("Defense Stats")
            stats_row = ctk.CTkFrame(self.form_content, fg_color="transparent")
            stats_row.pack(fill="x", pady=3)
            for col in range(3):
                stats_row.grid_columnconfigure(col, weight=1)
            for i, (key, label) in enumerate([
                ("Durability", "Durability"),
                ("DamageReduction", "Damage Reduction"),
                ("DamageProtection", "Damage Protection"),
            ]):
                frame = ctk.CTkFrame(stats_row, fg_color="transparent")
                frame.grid(row=0, column=i, sticky="ew", padx=2)
                ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11),
                             width=100, anchor="w").pack(side="left")
                var = ctk.StringVar(value=str(a[key]))
                self.form_vars[key] = var
                ctk.CTkEntry(frame, textvariable=var, width=80).pack(side="left", padx=2)

            # Repair cost
            if a["InitialRepairCost"]:
                self._create_subsection_header("Repair Cost")
                self.materials_frame = ctk.CTkFrame(self.form_content, fg_color="transparent")
                self.materials_frame.pack(fill="x", pady=5)
                for mat in a["InitialRepairCost"]:
                    self._add_material_row(mat["Material"], mat["Amount"])

            # Display & common
            self._create_subsection_header("Display")
            self._create_text_field("DisplayName", a["DisplayName"], label="Display Name")
            self._create_text_field("Description", a["Description"])
            self._create_text_field("Actor", a["Actor"],
                                    label="Actor Path", autocomplete_key="Actors")
            self._create_text_field("Icon", a["Icon"], label="Icon Path", readonly=True)

            tags = a.get("Tags", [])
            self._create_dropdown_field(
                "Tags", tags[0] if tags else "",
                self._get_options("Tags", []), label="Category Tag"
            )

            self._create_subsection_header("Inventory")
            self._create_dropdown_field(
                "Portability", a.get("Portability", "EItemPortability::Storable"),
                ["EItemPortability::Storable", "EItemPortability::NotStorable",
                 "EItemPortability::Holdable"], label="Portability"
            )
            inv_row = ctk.CTkFrame(self.form_content, fg_color="transparent")
            inv_row.pack(fill="x", pady=3)
            for col in range(3):
                inv_row.grid_columnconfigure(col, weight=1)
            for i, (key, lbl) in enumerate([
                ("MaxStackSize", "Max Stack"), ("SlotSize", "Slot Size"),
                ("BaseTradeValue", "Trade Value")
            ]):
                frame = ctk.CTkFrame(inv_row, fg_color="transparent")
                frame.grid(row=0, column=i, sticky="ew", padx=2)
                ctk.CTkLabel(frame, text=lbl, font=ctk.CTkFont(size=11),
                             width=80, anchor="w").pack(side="left")
                var = ctk.StringVar(value=str(a.get(key, 0)))
                self.form_vars[key] = var
                ctk.CTkEntry(frame, textvariable=var, width=80).pack(side="left", padx=2)

            self._create_dropdown_field(
                "Def_EnabledState", a["EnabledState"],
                DEFAULT_ENABLED_STATE, label="Definition Enabled State"
            )

        return has_data

    def _show_tool_form(self, recipe_json, definition_json):
        """Render tool form (item recipe + tool definition)."""
        has_data = False

        if recipe_json and isinstance(recipe_json, dict):
            has_data = True
            self._render_item_recipe_section(recipe_json)

        if definition_json and isinstance(definition_json, dict):
            has_data = True
            t = extract_tool_fields(definition_json)

            self._create_section_header("Tool Definition", "#00897B")

            self._create_text_field("Def_Name", t["Name"], label="Row Name", readonly=True)

            # Tool stats
            self._create_subsection_header("Tool Stats")
            stats_row1 = ctk.CTkFrame(self.form_content, fg_color="transparent")
            stats_row1.pack(fill="x", pady=3)
            for col in range(3):
                stats_row1.grid_columnconfigure(col, weight=1)
            for i, (key, label) in enumerate([
                ("Durability", "Durability"),
                ("DurabilityDecayWhileEquipped", "Durability Decay"),
                ("CarveHits", "Carve Hits"),
            ]):
                frame = ctk.CTkFrame(stats_row1, fg_color="transparent")
                frame.grid(row=0, column=i, sticky="ew", padx=2)
                ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11),
                             width=90, anchor="w").pack(side="left")
                var = ctk.StringVar(value=str(t[key]))
                self.form_vars[key] = var
                ctk.CTkEntry(frame, textvariable=var, width=80).pack(side="left", padx=2)

            stats_row2 = ctk.CTkFrame(self.form_content, fg_color="transparent")
            stats_row2.pack(fill="x", pady=3)
            for col in range(3):
                stats_row2.grid_columnconfigure(col, weight=1)
            for i, (key, label) in enumerate([
                ("StaminaCost", "Stamina Cost"),
                ("EnergyCost", "Energy Cost"),
                ("NpcMiningRate", "NPC Mining Rate"),
            ]):
                frame = ctk.CTkFrame(stats_row2, fg_color="transparent")
                frame.grid(row=0, column=i, sticky="ew", padx=2)
                ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11),
                             width=90, anchor="w").pack(side="left")
                var = ctk.StringVar(value=str(t[key]))
                self.form_vars[key] = var
                ctk.CTkEntry(frame, textvariable=var, width=80).pack(side="left", padx=2)

            # Repair cost
            if t["InitialRepairCost"]:
                self._create_subsection_header("Repair Cost")
                self.materials_frame = ctk.CTkFrame(self.form_content, fg_color="transparent")
                self.materials_frame.pack(fill="x", pady=5)
                for mat in t["InitialRepairCost"]:
                    self._add_material_row(mat["Material"], mat["Amount"])

            # Display & common
            self._create_subsection_header("Display")
            self._create_text_field("DisplayName", t["DisplayName"], label="Display Name")
            self._create_text_field("Description", t["Description"])
            self._create_text_field("Actor", t["Actor"],
                                    label="Actor Path", autocomplete_key="Actors")
            self._create_text_field("Icon", t["Icon"], label="Icon Path", readonly=True)

            tags = t.get("Tags", [])
            self._create_dropdown_field(
                "Tags", tags[0] if tags else "",
                self._get_options("Tags", []), label="Category Tag"
            )

            self._create_subsection_header("Inventory")
            self._create_dropdown_field(
                "Portability", t.get("Portability", "EItemPortability::Storable"),
                ["EItemPortability::Storable", "EItemPortability::NotStorable",
                 "EItemPortability::Holdable"], label="Portability"
            )
            inv_row = ctk.CTkFrame(self.form_content, fg_color="transparent")
            inv_row.pack(fill="x", pady=3)
            for col in range(3):
                inv_row.grid_columnconfigure(col, weight=1)
            for i, (key, lbl) in enumerate([
                ("MaxStackSize", "Max Stack"), ("SlotSize", "Slot Size"),
                ("BaseTradeValue", "Trade Value")
            ]):
                frame = ctk.CTkFrame(inv_row, fg_color="transparent")
                frame.grid(row=0, column=i, sticky="ew", padx=2)
                ctk.CTkLabel(frame, text=lbl, font=ctk.CTkFont(size=11),
                             width=80, anchor="w").pack(side="left")
                var = ctk.StringVar(value=str(t.get(key, 0)))
                self.form_vars[key] = var
                ctk.CTkEntry(frame, textvariable=var, width=80).pack(side="left", padx=2)

            self._create_dropdown_field(
                "Def_EnabledState", t["EnabledState"],
                DEFAULT_ENABLED_STATE, label="Definition Enabled State"
            )

        return has_data

    def _show_items_form(self, recipe_json, definition_json):
        """Render generic items form (item recipe + item definition)."""
        has_data = False

        if recipe_json and isinstance(recipe_json, dict):
            has_data = True
            self._render_item_recipe_section(recipe_json)

        if definition_json and isinstance(definition_json, dict):
            has_data = True
            item = extract_item_fields(definition_json)
            self._render_common_item_fields(item, "Item Definition", "#5C6BC0")

        return has_data

    def _show_flora_form(self, definition_json):
        """Render flora form (no recipe)."""
        if not definition_json or not isinstance(definition_json, dict):
            return False

        f = extract_flora_fields(definition_json)

        self._create_section_header("Flora Definition", "#43A047")

        self._create_text_field("Def_Name", f["Name"], label="Row Name", readonly=True)
        self._create_text_field("DisplayName", f["DisplayName"], label="Display Name")

        # Item references
        self._create_subsection_header("Item References")
        self._create_text_field("ItemRowHandle", f["ItemRowHandle"],
                                label="Item Row Handle", autocomplete_key="AllValues")
        self._create_text_field("OverrideItemDropHandle", f["OverrideItemDropHandle"],
                                label="Override Drop Handle", autocomplete_key="AllValues")

        # Drop amounts
        self._create_subsection_header("Drop Amounts")
        drop_row = ctk.CTkFrame(self.form_content, fg_color="transparent")
        drop_row.pack(fill="x", pady=3)
        for col in range(2):
            drop_row.grid_columnconfigure(col, weight=1)
        for i, (key, label) in enumerate([("MinCount", "Min Count"), ("MaxCount", "Max Count")]):
            frame = ctk.CTkFrame(drop_row, fg_color="transparent")
            frame.grid(row=0, column=i, sticky="ew", padx=2)
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11),
                         width=80, anchor="w").pack(side="left")
            var = ctk.StringVar(value=str(f[key]))
            self.form_vars[key] = var
            ctk.CTkEntry(frame, textvariable=var, width=80).pack(side="left", padx=2)

        # Growth timing
        self._create_subsection_header("Growth Timing")
        for key, label in [
            ("NumToGrowPerCycle", "Grow Per Cycle"),
            ("RegrowthSleepCount", "Regrowth Sleep Count"),
            ("TimeUntilGrowingStage", "Time Until Growing"),
            ("TimeUntilReadyStage", "Time Until Ready"),
            ("TimeUntilSpoiledStage", "Time Until Spoiled"),
            ("MinVariableGrowthTime", "Min Variable Growth"),
            ("MaxVariableGrowthTime", "Max Variable Growth"),
        ]:
            self._create_text_field(key, str(f[key]), label=label, width=200)

        # Growth properties
        self._create_subsection_header("Growth Properties")
        bool_row = ctk.CTkFrame(self.form_content, fg_color="transparent")
        bool_row.pack(fill="x", pady=4)
        for bf in ["bPrefersInShade", "bCanSpoil", "IsPlantable", "IsFungus"]:
            self._create_checkbox_field(bool_row, bf, f.get(bf, False))

        self._create_text_field("MinimumFarmingLight", str(f["MinimumFarmingLight"]),
                                label="Min Farming Light", width=200)

        # Enum dropdowns
        enum_row = ctk.CTkFrame(self.form_content, fg_color="transparent")
        enum_row.pack(fill="x", pady=3)
        self._create_dropdown_field_inline(
            enum_row, "FloraType", f["FloraType"],
            ["EMorFarmingFloraType::Flora", "EMorFarmingFloraType::Fungus",
             "EMorFarmingFloraType::Tree", "EMorFarmingFloraType::Crop"]
        )
        self._create_dropdown_field_inline(
            enum_row, "GrowthRate", f["GrowthRate"],
            ["EMorFarmingFloraGrowthRate::None", "EMorFarmingFloraGrowthRate::Slow",
             "EMorFarmingFloraGrowthRate::Medium", "EMorFarmingFloraGrowthRate::Fast"]
        )

        # Scale
        self._create_subsection_header("Visual")
        scale_row = ctk.CTkFrame(self.form_content, fg_color="transparent")
        scale_row.pack(fill="x", pady=3)
        for col in range(2):
            scale_row.grid_columnconfigure(col, weight=1)
        for i, (key, label) in enumerate([
            ("MinRandomScale", "Min Scale"), ("MaxRandomScale", "Max Scale")
        ]):
            frame = ctk.CTkFrame(scale_row, fg_color="transparent")
            frame.grid(row=0, column=i, sticky="ew", padx=2)
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11),
                         width=80, anchor="w").pack(side="left")
            var = ctk.StringVar(value=str(f[key]))
            self.form_vars[key] = var
            ctk.CTkEntry(frame, textvariable=var, width=80).pack(side="left", padx=2)

        self._create_text_field("ReceptacleActorToSpawn", f["ReceptacleActorToSpawn"],
                                label="Receptacle Actor", autocomplete_key="Actors")

        self._create_dropdown_field(
            "Def_EnabledState", f["EnabledState"],
            DEFAULT_ENABLED_STATE, label="Enabled State"
        )

        return True

    def _show_loot_form(self, definition_json):
        """Render loot form (no recipe, simple fields)."""
        if not definition_json or not isinstance(definition_json, dict):
            return False

        lt = extract_loot_fields(definition_json)

        self._create_section_header("Loot Definition", "#E53935")

        self._create_text_field("Def_Name", lt["Name"], label="Row Name", readonly=True)

        # Required tags
        self._create_text_field(
            "RequiredTags", ", ".join(lt["RequiredTags"]),
            label="Required Tags", autocomplete_key="LootTags"
        )

        # Item handle
        self._create_text_field(
            "ItemHandle", lt["ItemHandle"],
            label="Item Handle", autocomplete_key="AllValues"
        )

        # Drop settings
        self._create_subsection_header("Drop Settings")
        self._create_text_field("DropChance", str(lt["DropChance"]),
                                label="Drop Chance (0-1)", width=200)

        qty_row = ctk.CTkFrame(self.form_content, fg_color="transparent")
        qty_row.pack(fill="x", pady=3)
        for col in range(2):
            qty_row.grid_columnconfigure(col, weight=1)
        for i, (key, label) in enumerate([
            ("MinQuantity", "Min Quantity"), ("MaxQuantity", "Max Quantity")
        ]):
            frame = ctk.CTkFrame(qty_row, fg_color="transparent")
            frame.grid(row=0, column=i, sticky="ew", padx=2)
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11),
                         width=80, anchor="w").pack(side="left")
            var = ctk.StringVar(value=str(lt[key]))
            self.form_vars[key] = var
            ctk.CTkEntry(frame, textvariable=var, width=80).pack(side="left", padx=2)

        self._create_dropdown_field(
            "Def_EnabledState", lt["EnabledState"],
            DEFAULT_ENABLED_STATE, label="Enabled State"
        )

        return True

'''

content = content[:start_idx] + new_code + content[end_idx:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully refactored _show_form with per-type renderers.")
