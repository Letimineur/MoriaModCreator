"""Insert per-type extract functions into buildings_view.py."""
import sys

MARKER = """    return fields


# =============================================================================
# AUTOCOMPLETE WIDGET
# ============================================================================="""

NEW_CODE = '''    return fields


# =============================================================================
# PER-TYPE EXTRACT FUNCTIONS
# =============================================================================

def _extract_handle_rowname(prop: dict) -> str:
    """Extract RowName from a handle struct (MorAnyItemRowHandle etc.)."""
    for inner in prop.get("Value", []):
        if inner.get("Name") == "RowName":
            return inner.get("Value", "")
    return ""


def _extract_tag_names(prop: dict) -> list[str]:
    """Extract tag names from a GameplayTagContainer struct."""
    for inner in prop.get("Value", []):
        if inner.get("Name") == "Tags" or inner.get("Name") == prop.get("Name", ""):
            val = inner.get("Value", [])
            if isinstance(val, list):
                return [v for v in val if isinstance(v, str)]
    return []


def _extract_soft_object_path(prop: dict) -> str:
    """Extract asset path from a SoftObjectPropertyData."""
    val = prop.get("Value", {})
    if isinstance(val, dict):
        asset_path = val.get("AssetPath", {})
        return asset_path.get("AssetName", "")
    return ""


def _extract_repair_cost(prop: dict) -> list[dict]:
    """Extract InitialRepairCost array into [{Material, Amount}] list."""
    materials = []
    for mat_entry in prop.get("Value", []):
        mat_name = ""
        mat_count = 1
        for mat_prop in mat_entry.get("Value", []):
            if mat_prop.get("Name") == "MaterialHandle":
                for handle_prop in mat_prop.get("Value", []):
                    if handle_prop.get("Name") == "RowName":
                        mat_name = handle_prop.get("Value", "")
            elif mat_prop.get("Name") == "Count":
                mat_count = mat_prop.get("Value", 1)
        if mat_name:
            materials.append({"Material": mat_name, "Amount": mat_count})
    return materials


def extract_weapon_fields(weapon_json: dict) -> dict:
    """Extract editable fields from MorWeaponDefinition JSON."""
    fields = {
        "Name": weapon_json.get("Name", ""),
        "DamageType": "",
        "Durability": 0, "Tier": 1, "Damage": 0,
        "Speed": 1.0, "ArmorPenetration": 0.0,
        "StaminaCost": 0.0, "EnergyCost": 0.0,
        "BlockDamageReduction": 0.0,
        "InitialRepairCost": [],
        "DisplayName": "", "Description": "",
        "Icon": "", "Actor": "",
        "Tags": [],
        "Portability": "EItemPortability::Storable",
        "MaxStackSize": 1, "SlotSize": 1,
        "BaseTradeValue": 0.0,
        "EnabledState": "ERowEnabledState::Live",
    }
    for prop in weapon_json.get("Value", []):
        name = prop.get("Name", "")
        ptype = prop.get("$type", "")
        if name == "DamageType":
            for inner in prop.get("Value", []):
                if inner.get("Name") == "TagName":
                    fields["DamageType"] = inner.get("Value", "")
        elif name == "InitialRepairCost":
            fields["InitialRepairCost"] = _extract_repair_cost(prop)
        elif name == "Tags" and "StructPropertyData" in ptype:
            fields["Tags"] = _extract_tag_names(prop)
        elif name in ("Icon", "Actor") and "SoftObjectPropertyData" in ptype:
            fields[name] = _extract_soft_object_path(prop)
        elif name == "DisplayName" and "TextPropertyData" in ptype:
            fields["DisplayName"] = prop.get("Value", "")
        elif name == "Description" and "TextPropertyData" in ptype:
            fields["Description"] = prop.get("Value", "")
        elif "EnumPropertyData" in ptype:
            fields[name] = prop.get("Value", "")
        elif "BoolPropertyData" in ptype:
            fields[name] = prop.get("Value", False)
        elif "FloatPropertyData" in ptype:
            val = prop.get("Value", 0.0)
            fields[name] = float(val) if not isinstance(val, str) else 0.0
        elif "IntPropertyData" in ptype:
            fields[name] = prop.get("Value", 0)
        elif "BytePropertyData" in ptype and name == "Tier":
            fields["Tier"] = prop.get("Value", 1)
    return fields


def extract_armor_fields(armor_json: dict) -> dict:
    """Extract editable fields from MorArmorDefinition JSON."""
    fields = {
        "Name": armor_json.get("Name", ""),
        "Durability": 0,
        "DamageReduction": 0.0, "DamageProtection": 0.0,
        "InitialRepairCost": [],
        "DisplayName": "", "Description": "",
        "Icon": "", "Actor": "",
        "Tags": [],
        "Portability": "EItemPortability::Storable",
        "MaxStackSize": 1, "SlotSize": 1,
        "BaseTradeValue": 0.0,
        "EnabledState": "ERowEnabledState::Live",
    }
    for prop in armor_json.get("Value", []):
        name = prop.get("Name", "")
        ptype = prop.get("$type", "")
        if name == "InitialRepairCost":
            fields["InitialRepairCost"] = _extract_repair_cost(prop)
        elif name == "Tags" and "StructPropertyData" in ptype:
            fields["Tags"] = _extract_tag_names(prop)
        elif name in ("Icon", "Actor") and "SoftObjectPropertyData" in ptype:
            fields[name] = _extract_soft_object_path(prop)
        elif name == "DisplayName" and "TextPropertyData" in ptype:
            fields["DisplayName"] = prop.get("Value", "")
        elif name == "Description" and "TextPropertyData" in ptype:
            fields["Description"] = prop.get("Value", "")
        elif "EnumPropertyData" in ptype:
            fields[name] = prop.get("Value", "")
        elif "BoolPropertyData" in ptype:
            fields[name] = prop.get("Value", False)
        elif "FloatPropertyData" in ptype:
            val = prop.get("Value", 0.0)
            fields[name] = float(val) if not isinstance(val, str) else 0.0
        elif "IntPropertyData" in ptype:
            fields[name] = prop.get("Value", 0)
    return fields


def extract_tool_fields(tool_json: dict) -> dict:
    """Extract editable fields from MorToolDefinition JSON."""
    fields = {
        "Name": tool_json.get("Name", ""),
        "Durability": 0,
        "DurabilityDecayWhileEquipped": 0.0,
        "StaminaCost": 0.0, "EnergyCost": 0.0,
        "CarveHits": 0, "NpcMiningRate": 0.0,
        "InitialRepairCost": [],
        "DisplayName": "", "Description": "",
        "Icon": "", "Actor": "",
        "Tags": [],
        "Portability": "EItemPortability::Storable",
        "MaxStackSize": 1, "SlotSize": 1,
        "BaseTradeValue": 0.0,
        "EnabledState": "ERowEnabledState::Live",
    }
    for prop in tool_json.get("Value", []):
        name = prop.get("Name", "")
        ptype = prop.get("$type", "")
        if name == "InitialRepairCost":
            fields["InitialRepairCost"] = _extract_repair_cost(prop)
        elif name == "Tags" and "StructPropertyData" in ptype:
            fields["Tags"] = _extract_tag_names(prop)
        elif name in ("Icon", "Actor") and "SoftObjectPropertyData" in ptype:
            fields[name] = _extract_soft_object_path(prop)
        elif name == "DisplayName" and "TextPropertyData" in ptype:
            fields["DisplayName"] = prop.get("Value", "")
        elif name == "Description" and "TextPropertyData" in ptype:
            fields["Description"] = prop.get("Value", "")
        elif "EnumPropertyData" in ptype:
            fields[name] = prop.get("Value", "")
        elif "BoolPropertyData" in ptype:
            fields[name] = prop.get("Value", False)
        elif "FloatPropertyData" in ptype:
            val = prop.get("Value", 0.0)
            fields[name] = float(val) if not isinstance(val, str) else 0.0
        elif "IntPropertyData" in ptype:
            fields[name] = prop.get("Value", 0)
    return fields


def extract_item_fields(item_json: dict) -> dict:
    """Extract editable fields from MorItemDefinition JSON."""
    fields = {
        "Name": item_json.get("Name", ""),
        "DisplayName": "", "Description": "",
        "Icon": "", "Actor": "",
        "Tags": [],
        "Portability": "EItemPortability::Storable",
        "MaxStackSize": 1, "SlotSize": 1,
        "BaseTradeValue": 0.0,
        "EnabledState": "ERowEnabledState::Live",
    }
    for prop in item_json.get("Value", []):
        name = prop.get("Name", "")
        ptype = prop.get("$type", "")
        if name == "Tags" and "StructPropertyData" in ptype:
            fields["Tags"] = _extract_tag_names(prop)
        elif name in ("Icon", "Actor") and "SoftObjectPropertyData" in ptype:
            fields[name] = _extract_soft_object_path(prop)
        elif name == "DisplayName" and "TextPropertyData" in ptype:
            fields["DisplayName"] = prop.get("Value", "")
        elif name == "Description" and "TextPropertyData" in ptype:
            fields["Description"] = prop.get("Value", "")
        elif "EnumPropertyData" in ptype:
            fields[name] = prop.get("Value", "")
        elif "BoolPropertyData" in ptype:
            fields[name] = prop.get("Value", False)
        elif "FloatPropertyData" in ptype:
            val = prop.get("Value", 0.0)
            fields[name] = float(val) if not isinstance(val, str) else 0.0
        elif "IntPropertyData" in ptype:
            fields[name] = prop.get("Value", 0)
    return fields


def extract_flora_fields(flora_json: dict) -> dict:
    """Extract editable fields from MorFloraReceptacleDefinition JSON."""
    fields = {
        "Name": flora_json.get("Name", ""),
        "DisplayName": "",
        "ItemRowHandle": "", "OverrideItemDropHandle": "",
        "MinCount": 1, "MaxCount": 1,
        "NumToGrowPerCycle": 1, "RegrowthSleepCount": 1,
        "TimeUntilGrowingStage": 0, "TimeUntilReadyStage": 0,
        "TimeUntilSpoiledStage": 0,
        "MinVariableGrowthTime": 0, "MaxVariableGrowthTime": 0,
        "bPrefersInShade": False, "MinimumFarmingLight": 0.0,
        "bCanSpoil": False,
        "FloraType": "EMorFarmingFloraType::Flora",
        "GrowthRate": "EMorFarmingFloraGrowthRate::None",
        "IsPlantable": False, "IsFungus": False,
        "MinRandomScale": 1.0, "MaxRandomScale": 1.0,
        "ReceptacleActorToSpawn": "",
        "EnabledState": "ERowEnabledState::Live",
    }
    for prop in flora_json.get("Value", []):
        name = prop.get("Name", "")
        ptype = prop.get("$type", "")
        if name in ("ItemRowHandle", "OverrideItemDropHandle"):
            fields[name] = _extract_handle_rowname(prop)
        elif name == "ReceptacleActorToSpawn" and "SoftObjectPropertyData" in ptype:
            fields[name] = _extract_soft_object_path(prop)
        elif name == "DisplayName" and "TextPropertyData" in ptype:
            fields["DisplayName"] = prop.get("Value", "")
        elif "EnumPropertyData" in ptype:
            fields[name] = prop.get("Value", "")
        elif "BoolPropertyData" in ptype:
            fields[name] = prop.get("Value", False)
        elif "FloatPropertyData" in ptype:
            val = prop.get("Value", 0.0)
            fields[name] = float(val) if not isinstance(val, str) else 0.0
        elif "IntPropertyData" in ptype:
            fields[name] = prop.get("Value", 0)
    return fields


def extract_loot_fields(loot_json: dict) -> dict:
    """Extract editable fields from MorLootRowDefinition JSON."""
    fields = {
        "Name": loot_json.get("Name", ""),
        "RequiredTags": [],
        "ItemHandle": "",
        "DropChance": 1.0,
        "MinQuantity": 1, "MaxQuantity": 1,
        "EnabledState": "ERowEnabledState::Live",
    }
    for prop in loot_json.get("Value", []):
        name = prop.get("Name", "")
        ptype = prop.get("$type", "")
        if name == "RequiredTags" and "StructPropertyData" in ptype:
            fields["RequiredTags"] = _extract_tag_names(prop)
        elif name == "ItemHandle":
            fields["ItemHandle"] = _extract_handle_rowname(prop)
        elif name == "DropChance" and "FloatPropertyData" in ptype:
            val = prop.get("Value", 1.0)
            fields["DropChance"] = float(val) if not isinstance(val, str) else 1.0
        elif "EnumPropertyData" in ptype:
            fields[name] = prop.get("Value", "")
        elif "IntPropertyData" in ptype:
            fields[name] = prop.get("Value", 0)
    return fields


def extract_item_recipe_fields(recipe_json: dict) -> dict:
    """Extract editable fields from MorItemRecipeDefinition JSON.

    Similar to extract_recipe_fields but for item recipes (weapons, armor,
    tools, items). Does NOT include building-specific fields like BuildProcess,
    PlacementType, LocationRequirement, etc.
    """
    fields = {
        "Name": recipe_json.get("Name", ""),
        "ResultItemHandle": "",
        "ResultItemCount": 1,
        "CraftTimeSeconds": 0.0,
        "bCanBePinned": True,
        "bNpcOnlyRecipe": False,
        "bHasSandboxRequirementsOverride": False,
        "bHasSandboxUnlockOverride": False,
        "EnabledState": "ERowEnabledState::Live",
        "Materials": [],
        "DefaultRequiredConstructions": [],
        "DefaultUnlocks_UnlockType": "EMorRecipeUnlockType::Manual",
        "DefaultUnlocks_NumFragments": 1,
        "DefaultUnlocks_RequiredItems": [],
        "DefaultUnlocks_RequiredConstructions": [],
        "DefaultUnlocks_RequiredFragments": [],
        "SandboxUnlocks_UnlockType": "EMorRecipeUnlockType::Manual",
        "SandboxUnlocks_NumFragments": 1,
        "SandboxUnlocks_RequiredItems": [],
        "SandboxUnlocks_RequiredConstructions": [],
        "SandboxUnlocks_RequiredFragments": [],
        "SandboxRequiredMaterials": [],
        "SandboxRequiredConstructions": [],
    }

    for prop in recipe_json.get("Value", []):
        prop_name = prop.get("Name", "")
        prop_type = prop.get("$type", "")

        if "EnumPropertyData" in prop_type:
            fields[prop_name] = prop.get("Value", "")
        elif "BoolPropertyData" in prop_type:
            fields[prop_name] = prop.get("Value", False)
        elif "FloatPropertyData" in prop_type:
            val = prop.get("Value", 0.0)
            fields[prop_name] = float(val) if not isinstance(val, str) else 0.0
        elif "IntPropertyData" in prop_type:
            fields[prop_name] = prop.get("Value", 0)
        elif prop_name == "ResultItemHandle":
            fields["ResultItemHandle"] = _extract_handle_rowname(prop)
        elif prop_name == "DefaultUnlocks":
            for unlock_prop in prop.get("Value", []):
                uname = unlock_prop.get("Name", "")
                utype = unlock_prop.get("$type", "")
                if uname == "UnlockType" and "EnumPropertyData" in utype:
                    fields["DefaultUnlocks_UnlockType"] = unlock_prop.get("Value", "")
                elif uname == "NumFragments":
                    fields["DefaultUnlocks_NumFragments"] = unlock_prop.get("Value", 1)
                elif uname == "UnlockRequiredItems":
                    items = []
                    for entry in unlock_prop.get("Value", []):
                        for ep in entry.get("Value", []):
                            if ep.get("Name") == "RowName":
                                items.append(ep.get("Value", ""))
                    fields["DefaultUnlocks_RequiredItems"] = items
                elif uname == "UnlockRequiredConstructions":
                    consts = []
                    for entry in unlock_prop.get("Value", []):
                        for ep in entry.get("Value", []):
                            if ep.get("Name") == "RowName":
                                consts.append(ep.get("Value", ""))
                    fields["DefaultUnlocks_RequiredConstructions"] = consts
                elif uname == "UnlockRequiredFragments":
                    frags = []
                    for entry in unlock_prop.get("Value", []):
                        for ep in entry.get("Value", []):
                            if ep.get("Name") == "RowName":
                                frags.append(ep.get("Value", ""))
                    fields["DefaultUnlocks_RequiredFragments"] = frags
        elif prop_name == "SandboxUnlocks":
            for unlock_prop in prop.get("Value", []):
                uname = unlock_prop.get("Name", "")
                utype = unlock_prop.get("$type", "")
                if uname == "UnlockType" and "EnumPropertyData" in utype:
                    fields["SandboxUnlocks_UnlockType"] = unlock_prop.get("Value", "")
                elif uname == "NumFragments":
                    fields["SandboxUnlocks_NumFragments"] = unlock_prop.get("Value", 1)
                elif uname == "UnlockRequiredItems":
                    items = []
                    for entry in unlock_prop.get("Value", []):
                        for ep in entry.get("Value", []):
                            if ep.get("Name") == "RowName":
                                items.append(ep.get("Value", ""))
                    fields["SandboxUnlocks_RequiredItems"] = items
                elif uname == "UnlockRequiredConstructions":
                    consts = []
                    for entry in unlock_prop.get("Value", []):
                        for ep in entry.get("Value", []):
                            if ep.get("Name") == "RowName":
                                consts.append(ep.get("Value", ""))
                    fields["SandboxUnlocks_RequiredConstructions"] = consts
                elif uname == "UnlockRequiredFragments":
                    frags = []
                    for entry in unlock_prop.get("Value", []):
                        for ep in entry.get("Value", []):
                            if ep.get("Name") == "RowName":
                                frags.append(ep.get("Value", ""))
                    fields["SandboxUnlocks_RequiredFragments"] = frags
        elif prop_name == "DefaultRequiredMaterials":
            fields["Materials"] = _extract_repair_cost(prop)
        elif prop_name == "DefaultRequiredConstructions":
            consts = []
            for entry in prop.get("Value", []):
                for ep in entry.get("Value", []):
                    if ep.get("Name") == "RowName":
                        consts.append(ep.get("Value", ""))
            fields["DefaultRequiredConstructions"] = consts
        elif prop_name == "SandboxRequiredMaterials":
            fields["SandboxRequiredMaterials"] = _extract_repair_cost(prop)
        elif prop_name == "SandboxRequiredConstructions":
            consts = []
            for entry in prop.get("Value", []):
                for ep in entry.get("Value", []):
                    if ep.get("Name") == "RowName":
                        consts.append(ep.get("Value", ""))
            fields["SandboxRequiredConstructions"] = consts

    return fields


# =============================================================================
# AUTOCOMPLETE WIDGET
# ============================================================================='''

filepath = r"c:\Users\johnb\OneDrive\Documents\Projects\Moria MOD Creator\src\ui\buildings_view.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

if MARKER not in content:
    print("ERROR: Marker not found in file!")
    sys.exit(1)

content = content.replace(MARKER, NEW_CODE, 1)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully inserted extract functions.")
