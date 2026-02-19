"""Unit tests for the shared_utils module."""

import configparser
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from src.ui.shared_utils import (
    get_retoc_dir,
    get_jsondata_dir,
    get_buildings_cache_path,
    get_files_to_convert,
    check_jsondata_exists,
    update_buildings_ini_from_json,
    UASSET_EXTENSIONS,
    BUILDINGS_CACHE_FILENAME,
)


class TestDirectoryHelpers:
    """Tests for directory path helper functions."""

    @patch('src.ui.shared_utils.get_output_dir')
    def test_get_retoc_dir(self, mock_output):
        """Test get_retoc_dir returns output/retoc."""
        mock_output.return_value = Path('C:/output')
        result = get_retoc_dir()
        assert result == Path('C:/output/retoc')

    @patch('src.ui.shared_utils.get_output_dir')
    def test_get_jsondata_dir(self, mock_output):
        """Test get_jsondata_dir returns output/jsondata."""
        mock_output.return_value = Path('C:/output')
        result = get_jsondata_dir()
        assert result == Path('C:/output/jsondata')

    @patch('src.ui.shared_utils.get_appdata_dir')
    def test_get_buildings_cache_path(self, mock_appdata):
        """Test get_buildings_cache_path returns correct path."""
        mock_appdata.return_value = Path('C:/AppData/MoriaMODCreator')
        result = get_buildings_cache_path()
        expected = Path('C:/AppData/MoriaMODCreator/New Objects/Build') / BUILDINGS_CACHE_FILENAME
        assert result == expected


class TestGetFilesToConvert:
    """Tests for get_files_to_convert function."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('src.ui.shared_utils.get_output_dir')
    def test_retoc_dir_not_exists(self, mock_output):
        """Test returns empty list when retoc dir doesn't exist."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        result = get_files_to_convert()
        assert not result

    @patch('src.ui.shared_utils.get_output_dir')
    def test_retoc_dir_empty(self, mock_output):
        """Test returns empty list when retoc dir is empty."""
        retoc_dir = Path(self.temp_dir) / 'output' / 'retoc'
        retoc_dir.mkdir(parents=True)
        mock_output.return_value = Path(self.temp_dir) / 'output'
        result = get_files_to_convert()
        assert not result

    @patch('src.ui.shared_utils.get_output_dir')
    def test_finds_uasset_files(self, mock_output):
        """Test finds .uasset files in retoc dir."""
        retoc_dir = Path(self.temp_dir) / 'output' / 'retoc'
        retoc_dir.mkdir(parents=True)
        (retoc_dir / 'test.uasset').touch()
        (retoc_dir / 'test.json').touch()  # Should be ignored

        mock_output.return_value = Path(self.temp_dir) / 'output'
        result = get_files_to_convert()
        assert len(result) == 1
        assert result[0].suffix == '.uasset'

    @patch('src.ui.shared_utils.get_output_dir')
    def test_finds_umap_files(self, mock_output):
        """Test finds .umap files in retoc dir."""
        retoc_dir = Path(self.temp_dir) / 'output' / 'retoc'
        retoc_dir.mkdir(parents=True)
        (retoc_dir / 'test.umap').touch()

        mock_output.return_value = Path(self.temp_dir) / 'output'
        result = get_files_to_convert()
        assert len(result) == 1
        assert result[0].suffix == '.umap'

    @patch('src.ui.shared_utils.get_output_dir')
    def test_finds_files_in_subdirs(self, mock_output):
        """Test finds files recursively in subdirectories."""
        retoc_dir = Path(self.temp_dir) / 'output' / 'retoc'
        sub_dir = retoc_dir / 'Moria' / 'Content'
        sub_dir.mkdir(parents=True)
        (sub_dir / 'test1.uasset').touch()
        (sub_dir / 'test2.uasset').touch()
        (retoc_dir / 'root.uasset').touch()

        mock_output.return_value = Path(self.temp_dir) / 'output'
        result = get_files_to_convert()
        assert len(result) == 3


class TestCheckJsondataExists:
    """Tests for check_jsondata_exists function."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('src.ui.shared_utils.get_output_dir')
    def test_jsondata_dir_not_exists(self, mock_output):
        """Test returns False when jsondata dir doesn't exist."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        assert check_jsondata_exists() is False

    @patch('src.ui.shared_utils.get_output_dir')
    def test_jsondata_dir_empty(self, mock_output):
        """Test returns False when jsondata dir is empty."""
        jsondata_dir = Path(self.temp_dir) / 'output' / 'jsondata'
        jsondata_dir.mkdir(parents=True)
        mock_output.return_value = Path(self.temp_dir) / 'output'
        assert check_jsondata_exists() is False

    @patch('src.ui.shared_utils.get_output_dir')
    def test_jsondata_dir_has_json_files(self, mock_output):
        """Test returns True when jsondata dir has JSON files."""
        jsondata_dir = Path(self.temp_dir) / 'output' / 'jsondata'
        jsondata_dir.mkdir(parents=True)
        (jsondata_dir / 'test.json').write_text('{}')
        mock_output.return_value = Path(self.temp_dir) / 'output'
        assert check_jsondata_exists() is True

    @patch('src.ui.shared_utils.get_output_dir')
    def test_jsondata_dir_has_json_in_subdir(self, mock_output):
        """Test returns True when JSON files are in subdirectories."""
        sub_dir = Path(self.temp_dir) / 'output' / 'jsondata' / 'Moria' / 'Content'
        sub_dir.mkdir(parents=True)
        (sub_dir / 'data.json').write_text('{}')
        mock_output.return_value = Path(self.temp_dir) / 'output'
        assert check_jsondata_exists() is True

    @patch('src.ui.shared_utils.get_output_dir')
    def test_jsondata_dir_has_non_json_files(self, mock_output):
        """Test returns False when dir has only non-JSON files."""
        jsondata_dir = Path(self.temp_dir) / 'output' / 'jsondata'
        jsondata_dir.mkdir(parents=True)
        (jsondata_dir / 'test.txt').write_text('hello')
        mock_output.return_value = Path(self.temp_dir) / 'output'
        assert check_jsondata_exists() is False


class TestUpdateBuildingsIniFromJson:
    """Tests for update_buildings_ini_from_json function."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_recipes_json(self, name_map: list) -> Path:
        """Helper to create a DT_ConstructionRecipes.json file."""
        recipes_dir = (
            Path(self.temp_dir) / 'output' / 'jsondata' / 'Moria' / 'Content'
            / 'Tech' / 'Data' / 'Building'
        )
        recipes_dir.mkdir(parents=True)
        recipes_path = recipes_dir / 'DT_ConstructionRecipes.json'
        recipes_path.write_text(json.dumps({'NameMap': name_map}))
        return recipes_path

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_recipes_file_not_found(self, mock_output, mock_appdata):
        """Test returns failure when recipes file doesn't exist."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        mock_appdata.return_value = Path(self.temp_dir) / 'appdata'
        success, msg = update_buildings_ini_from_json()
        assert success is False
        assert 'not found' in msg

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_categorizes_items(self, mock_output, mock_appdata):
        """Test categorizes Item.* names into Items and Materials."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        self._create_recipes_json(['Item.Stone', 'Item.Wood'])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        cache_path = appdata / 'New Objects' / 'Build' / BUILDINGS_CACHE_FILENAME
        assert cache_path.exists()

        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        items_values = config.get('Items', 'values')
        assert 'Item.Stone' in items_values
        assert 'Item.Wood' in items_values
        materials_values = config.get('Materials', 'values')
        assert 'Item.Stone' in materials_values

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_categorizes_ores(self, mock_output, mock_appdata):
        """Test categorizes Ore.* names into Ores and Materials."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        self._create_recipes_json(['Ore.Iron', 'Ore.Gold'])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        cache_path = appdata / 'New Objects' / 'Build' / BUILDINGS_CACHE_FILENAME
        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        assert 'Ore.Iron' in config.get('Ores', 'values')
        assert 'Ore.Iron' in config.get('Materials', 'values')

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_categorizes_consumables(self, mock_output, mock_appdata):
        """Test categorizes Consumable.* names."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        self._create_recipes_json(['Consumable.Potion'])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        cache_path = appdata / 'New Objects' / 'Build' / BUILDINGS_CACHE_FILENAME
        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        assert 'Consumable.Potion' in config.get('Consumables', 'values')
        assert 'Consumable.Potion' in config.get('Materials', 'values')

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_categorizes_enums(self, mock_output, mock_appdata):
        """Test categorizes Enum::Value names."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        self._create_recipes_json(['EBuildProcess::DualMode', 'EBuildProcess::SingleMode'])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        cache_path = appdata / 'New Objects' / 'Build' / BUILDINGS_CACHE_FILENAME
        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        values = config.get('Enum_EBuildProcess', 'values')
        assert 'EBuildProcess::DualMode' in values
        assert 'EBuildProcess::SingleMode' in values

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_categorizes_tags(self, mock_output, mock_appdata):
        """Test categorizes UI.*.Category tags."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        self._create_recipes_json(['UI.Construction.Category.Walls'])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        cache_path = appdata / 'New Objects' / 'Build' / BUILDINGS_CACHE_FILENAME
        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        assert 'UI.Construction.Category.Walls' in config.get('Tags', 'values')

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_categorizes_tools(self, mock_output, mock_appdata):
        """Test categorizes Tool.* names."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        self._create_recipes_json(['Tool.Pickaxe'])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        cache_path = appdata / 'New Objects' / 'Build' / BUILDINGS_CACHE_FILENAME
        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        assert 'Tool.Pickaxe' in config.get('Tools', 'values')

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_categorizes_decorations(self, mock_output, mock_appdata):
        """Test categorizes Decoration* names."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        self._create_recipes_json(['DecorationTable'])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        cache_path = appdata / 'New Objects' / 'Build' / BUILDINGS_CACHE_FILENAME
        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        assert 'DecorationTable' in config.get('Decorations', 'values')

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_categorizes_fragments(self, mock_output, mock_appdata):
        """Test categorizes *_Fragment names."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        self._create_recipes_json(['Ancient_Fragment'])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        cache_path = appdata / 'New Objects' / 'Build' / BUILDINGS_CACHE_FILENAME
        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        assert 'Ancient_Fragment' in config.get('Fragments', 'values')
        assert 'Ancient_Fragment' in config.get('UnlockRequiredFragments', 'values')

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_categorizes_constructions(self, mock_output, mock_appdata):
        """Test categorizes uppercase names with underscores as constructions."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        self._create_recipes_json(['Stone_Wall_Small'])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        cache_path = appdata / 'New Objects' / 'Build' / BUILDINGS_CACHE_FILENAME
        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        assert 'Stone_Wall_Small' in config.get('Constructions', 'values')
        assert 'Stone_Wall_Small' in config.get('ResultConstructions', 'values')

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_skips_slash_prefixed_names(self, mock_output, mock_appdata):
        """Test that /Game/ paths are skipped (filtered as system names starting with /)."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        self._create_recipes_json(['/Game/Buildings/BP_Wall.BP_Wall_C'])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        cache_path = appdata / 'New Objects' / 'Build' / BUILDINGS_CACHE_FILENAME
        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        # Names starting with / are skipped as system names
        assert len(config.sections()) == 0

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_skips_system_names(self, mock_output, mock_appdata):
        """Test skips system names starting with / or $."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        self._create_recipes_json([
            '/Script/Engine.DataTable',
            '$NONE',
            'ArrayProperty',
            'BoolProperty',
            'None',
        ])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        cache_path = appdata / 'New Objects' / 'Build' / BUILDINGS_CACHE_FILENAME
        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        # No sections should be created from system names
        assert len(config.sections()) == 0

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_merges_with_existing_cache(self, mock_output, mock_appdata):
        """Test merging new values with existing cache file."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        # Create existing cache
        cache_dir = appdata / 'New Objects' / 'Build'
        cache_dir.mkdir(parents=True)
        cache_path = cache_dir / BUILDINGS_CACHE_FILENAME
        existing_config = configparser.ConfigParser()
        existing_config.add_section('Items')
        existing_config.set('Items', 'values', 'Item.OldItem')
        with open(cache_path, 'w', encoding='utf-8') as f:
            existing_config.write(f)

        self._create_recipes_json(['Item.NewItem'])

        success, _ = update_buildings_ini_from_json()
        assert success is True

        config = configparser.ConfigParser()
        config.read(cache_path, encoding='utf-8')
        values = config.get('Items', 'values')
        assert 'Item.OldItem' in values
        assert 'Item.NewItem' in values

    @patch('src.ui.shared_utils.get_appdata_dir')
    @patch('src.ui.shared_utils.get_output_dir')
    def test_invalid_json(self, mock_output, mock_appdata):
        """Test returns failure for invalid JSON."""
        mock_output.return_value = Path(self.temp_dir) / 'output'
        appdata = Path(self.temp_dir) / 'appdata'
        mock_appdata.return_value = appdata

        recipes_dir = (
            Path(self.temp_dir) / 'output' / 'jsondata' / 'Moria' / 'Content'
            / 'Tech' / 'Data' / 'Building'
        )
        recipes_dir.mkdir(parents=True)
        (recipes_dir / 'DT_ConstructionRecipes.json').write_text('not valid json')

        success, msg = update_buildings_ini_from_json()
        assert success is False
        assert 'JSON parse error' in msg


class TestConstants:
    """Tests for module-level constants."""

    def test_uasset_extensions(self):
        """Test UASSET_EXTENSIONS contains expected values."""
        assert '.uasset' in UASSET_EXTENSIONS
        assert '.umap' in UASSET_EXTENSIONS

    def test_buildings_cache_filename(self):
        """Test BUILDINGS_CACHE_FILENAME is set."""
        assert BUILDINGS_CACHE_FILENAME == 'buildings_cache.ini'
