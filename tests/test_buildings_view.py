"""Unit tests for the buildings view module."""

import json
import tempfile
import shutil
from pathlib import Path

import pytest

from src.ui.buildings_view import (
    parse_def_file,
    extract_recipe_fields,
    extract_construction_fields,
    FIELD_DESCRIPTIONS,
)


class TestParseDefFile:
    """Tests for parse_def_file function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_basic_def_file(self):
        """Test parsing a basic .def file with metadata."""
        def_file = Path(self.temp_dir) / "TestBuilding.def"
        def_file.write_text('''<?xml version="1.0" encoding="utf-8"?>
<definition>
    <title>Test Building</title>
    <author>Test Author</author>
    <description>A test building description</description>
</definition>''', encoding='utf-8')
        
        result = parse_def_file(def_file)
        
        assert result["name"] == "TestBuilding"
        assert result["title"] == "Test Building"
        assert result["author"] == "Test Author"
        assert result["description"] == "A test building description"
        assert result["recipe_json"] is None
        assert result["construction_json"] is None

    def test_parse_def_file_with_recipe(self):
        """Test parsing a .def file with recipe JSON."""
        recipe_data = {
            "Name": "Test_Recipe",
            "Value": [
                {"$type": "EnumPropertyData", "Name": "BuildProcess", "Value": "EBuildProcess::DualMode"}
            ]
        }
        
        def_file = Path(self.temp_dir) / "RecipeBuilding.def"
        def_file.write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<definition>
    <title>Recipe Building</title>
    <mod file="\\Moria\\Content\\Tech\\Data\\Building\\DT_ConstructionRecipes.json">
        <add_row>{json.dumps(recipe_data)}</add_row>
    </mod>
</definition>''', encoding='utf-8')
        
        result = parse_def_file(def_file)
        
        assert result["recipe_json"] is not None
        assert result["recipe_json"]["Name"] == "Test_Recipe"

    def test_parse_def_file_with_construction(self):
        """Test parsing a .def file with construction JSON."""
        construction_data = {
            "Name": "Test_Construction",
            "Value": [
                {"$type": "TextPropertyData", "Name": "DisplayName", "Value": "Test Display"}
            ]
        }
        imports_data = [{"ObjectName": "TestIcon", "ClassName": "Texture2D"}]
        
        def_file = Path(self.temp_dir) / "ConstructionBuilding.def"
        def_file.write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<definition>
    <title>Construction Building</title>
    <mod file="\\Moria\\Content\\Tech\\Data\\Building\\DT_Constructions.json">
        <add_row>{json.dumps(construction_data)}</add_row>
        <add_imports>{json.dumps(imports_data)}</add_imports>
    </mod>
</definition>''', encoding='utf-8')
        
        result = parse_def_file(def_file)
        
        assert result["construction_json"] is not None
        assert result["construction_json"]["Name"] == "Test_Construction"
        assert result["imports_json"] is not None
        assert len(result["imports_json"]) == 1
        assert result["imports_json"][0]["ObjectName"] == "TestIcon"

    def test_parse_def_file_minimal(self):
        """Test parsing a minimal .def file with no optional elements."""
        def_file = Path(self.temp_dir) / "Minimal.def"
        def_file.write_text('''<?xml version="1.0" encoding="utf-8"?>
<definition>
</definition>''', encoding='utf-8')
        
        result = parse_def_file(def_file)
        
        assert result["name"] == "Minimal"
        assert result["title"] == ""
        assert result["author"] == ""
        assert result["description"] == ""


class TestExtractRecipeFields:
    """Tests for extract_recipe_fields function."""

    def test_extract_empty_recipe(self):
        """Test extracting fields from empty recipe."""
        result = extract_recipe_fields({})
        
        assert result["Name"] == ""
        assert result["BuildProcess"] == "EBuildProcess::DualMode"
        assert result["bOnFloor"] is True
        assert result["Materials"] == []

    def test_extract_recipe_with_name(self):
        """Test extracting Name field."""
        recipe = {"Name": "Test_Building"}
        result = extract_recipe_fields(recipe)
        
        assert result["Name"] == "Test_Building"

    def test_extract_recipe_enum_fields(self):
        """Test extracting enum fields from recipe."""
        recipe = {
            "Name": "Test",
            "Value": [
                {"$type": "EnumPropertyData", "Name": "BuildProcess", "Value": "EBuildProcess::SingleMode"},
                {"$type": "EnumPropertyData", "Name": "PlacementType", "Value": "EPlacementType::SnapGrid"},
                {"$type": "EnumPropertyData", "Name": "LocationRequirement", "Value": "EConstructionLocation::Anywhere"},
                {"$type": "EnumPropertyData", "Name": "FoundationRule", "Value": "EFoundationRule::Always"},
            ]
        }
        
        result = extract_recipe_fields(recipe)
        
        assert result["BuildProcess"] == "EBuildProcess::SingleMode"
        assert result["PlacementType"] == "EPlacementType::SnapGrid"
        assert result["LocationRequirement"] == "EConstructionLocation::Anywhere"
        assert result["FoundationRule"] == "EFoundationRule::Always"

    def test_extract_recipe_bool_fields(self):
        """Test extracting boolean fields from recipe."""
        recipe = {
            "Value": [
                {"$type": "BoolPropertyData", "Name": "bOnWall", "Value": True},
                {"$type": "BoolPropertyData", "Name": "bOnFloor", "Value": False},
                {"$type": "BoolPropertyData", "Name": "bAllowRefunds", "Value": False},
            ]
        }
        
        result = extract_recipe_fields(recipe)
        
        assert result["bOnWall"] is True
        assert result["bOnFloor"] is False
        assert result["bAllowRefunds"] is False

    def test_extract_recipe_numeric_fields(self):
        """Test extracting numeric fields from recipe."""
        recipe = {
            "Value": [
                {"$type": "FloatPropertyData", "Name": "MaxAllowedPenetrationDepth", "Value": 50.0},
                {"$type": "FloatPropertyData", "Name": "RequireNearbyRadius", "Value": 500.0},
                {"$type": "IntPropertyData", "Name": "CameraStateOverridePriority", "Value": 10},
            ]
        }
        
        result = extract_recipe_fields(recipe)
        
        assert result["MaxAllowedPenetrationDepth"] == 50.0
        assert result["RequireNearbyRadius"] == 500.0
        assert result["CameraStateOverridePriority"] == 10

    def test_extract_recipe_materials(self):
        """Test extracting materials array from recipe."""
        recipe = {
            "Value": [
                {
                    "$type": "ArrayPropertyData",
                    "Name": "DefaultRequiredMaterials",
                    "Value": [
                        {
                            "Value": [
                                {
                                    "Name": "MaterialHandle",
                                    "Value": [
                                        {"Name": "RowName", "Value": "Item.Stone"}
                                    ]
                                },
                                {"Name": "Count", "Value": 10}
                            ]
                        },
                        {
                            "Value": [
                                {
                                    "Name": "MaterialHandle",
                                    "Value": [
                                        {"Name": "RowName", "Value": "Item.Wood"}
                                    ]
                                },
                                {"Name": "Count", "Value": 5}
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_recipe_fields(recipe)
        
        assert len(result["Materials"]) == 2
        assert result["Materials"][0]["Material"] == "Item.Stone"
        assert result["Materials"][0]["Amount"] == 10
        assert result["Materials"][1]["Material"] == "Item.Wood"
        assert result["Materials"][1]["Amount"] == 5

    def test_extract_recipe_result_construction_handle(self):
        """Test extracting ResultConstructionHandle from recipe."""
        recipe = {
            "Value": [
                {
                    "$type": "StructPropertyData",
                    "Name": "ResultConstructionHandle",
                    "Value": [
                        {"Name": "RowName", "Value": "Test_Construction"}
                    ]
                }
            ]
        }
        
        result = extract_recipe_fields(recipe)
        
        assert result["ResultConstructionHandle"] == "Test_Construction"


class TestExtractConstructionFields:
    """Tests for extract_construction_fields function."""

    def test_extract_empty_construction(self):
        """Test extracting fields from empty construction."""
        result = extract_construction_fields({})
        
        assert result["Name"] == ""
        assert result["DisplayName"] == ""
        assert result["Actor"] == ""
        assert result["Tags"] == []

    def test_extract_construction_with_name(self):
        """Test extracting Name field."""
        construction = {"Name": "Test_Construction"}
        result = extract_construction_fields(construction)
        
        assert result["Name"] == "Test_Construction"

    def test_extract_construction_display_name(self):
        """Test extracting DisplayName from construction."""
        construction = {
            "Value": [
                {"$type": "TextPropertyData", "Name": "DisplayName", "Value": "Test Display Name"}
            ]
        }
        
        result = extract_construction_fields(construction)
        
        assert result["DisplayName"] == "Test Display Name"

    def test_extract_construction_description(self):
        """Test extracting Description from construction."""
        construction = {
            "Value": [
                {"$type": "TextPropertyData", "Name": "Description", "Value": "A test description"}
            ]
        }
        
        result = extract_construction_fields(construction)
        
        assert result["Description"] == "A test description"

    def test_extract_construction_actor(self):
        """Test extracting Actor path from construction."""
        construction = {
            "Value": [
                {
                    "$type": "SoftObjectPropertyData",
                    "Name": "Actor",
                    "Value": {
                        "AssetPath": {
                            "AssetName": "/Game/Buildings/BP_TestBuilding.BP_TestBuilding_C"
                        }
                    }
                }
            ]
        }
        
        result = extract_construction_fields(construction)
        
        assert result["Actor"] == "/Game/Buildings/BP_TestBuilding.BP_TestBuilding_C"

    def test_extract_construction_icon(self):
        """Test extracting Icon index from construction."""
        construction = {
            "Value": [
                {"Name": "Icon", "Value": -1234}
            ]
        }
        
        result = extract_construction_fields(construction)
        
        assert result["Icon"] == -1234

    def test_extract_construction_enabled_state(self):
        """Test extracting EnabledState from construction."""
        construction = {
            "Value": [
                {"$type": "EnumPropertyData", "Name": "EnabledState", "Value": "ERowEnabledState::Disabled"}
            ]
        }
        
        result = extract_construction_fields(construction)
        
        assert result["EnabledState"] == "ERowEnabledState::Disabled"

    def test_extract_construction_tags(self):
        """Test extracting Tags from construction."""
        construction = {
            "Value": [
                {
                    "Name": "Tags",
                    "Value": [
                        {"Name": "Tags", "Value": ["UI.Construction.Category.Walls", "Building.Type.Stone"]}
                    ]
                }
            ]
        }
        
        result = extract_construction_fields(construction)
        
        assert "UI.Construction.Category.Walls" in result["Tags"]
        assert "Building.Type.Stone" in result["Tags"]


class TestFieldDescriptions:
    """Tests for FIELD_DESCRIPTIONS dictionary."""

    def test_field_descriptions_exist(self):
        """Test that FIELD_DESCRIPTIONS is not empty."""
        assert len(FIELD_DESCRIPTIONS) > 0

    def test_common_fields_have_descriptions(self):
        """Test that common fields have descriptions."""
        common_fields = [
            "BuildingName",
            "BuildProcess",
            "PlacementType",
            "LocationRequirement",
            "bOnWall",
            "bOnFloor",
            "bAllowRefunds",
            "DisplayName",
            "Actor",
            "Tags",
        ]
        
        for field in common_fields:
            assert field in FIELD_DESCRIPTIONS, f"Missing description for {field}"
            assert len(FIELD_DESCRIPTIONS[field]) > 0, f"Empty description for {field}"

    def test_descriptions_are_strings(self):
        """Test that all descriptions are non-empty strings."""
        for field, description in FIELD_DESCRIPTIONS.items():
            assert isinstance(description, str), f"{field} description is not a string"
            assert len(description.strip()) > 0, f"{field} has empty description"


class TestFieldTooltip:
    """Tests for FieldTooltip class (basic tests without GUI)."""

    def test_field_tooltip_import(self):
        """Test that FieldTooltip can be imported."""
        from src.ui.buildings_view import FieldTooltip
        assert FieldTooltip is not None
