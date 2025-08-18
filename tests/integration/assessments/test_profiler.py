from pathlib import Path
from unittest.mock import patch

import shutil
import tempfile
import yaml
import pytest

from databricks.labs.lakebridge.assessments.profiler import Profiler


def test_supported_source_technologies() -> None:
    """Test that supported source technologies are correctly returned"""
    profiler = Profiler()
    supported_platforms = profiler.supported_source_technologies()
    assert isinstance(supported_platforms, list)
    assert "synapse" in supported_platforms


def test_profile_unsupported_platform() -> None:
    """Test that profiling an unsupported platform raises ValueError"""
    profiler = Profiler()
    with pytest.raises(ValueError, match="Unsupported platform: invalidplatform"):
        profiler.profile("InvalidPlatform")


@patch(
    'databricks.labs.lakebridge.assessments.profiler.PLATFORM_TO_SOURCE_TECHNOLOGY',
    {"synapse": "tests/resources/assessments/pipeline_config_main.yml"},
)
@patch('databricks.labs.lakebridge.assessments.profiler.PRODUCT_PATH_PREFIX', Path(__file__).parent / "../../../")
def test_profile_execution() -> None:
    """Test successful profiling execution using actual pipeline configuration"""
    profiler = Profiler()
    profiler.profile("synapse")
    assert Path("/tmp/profiler_main/profiler_extract.db").exists(), "Profiler extract database should be created"


@patch(
    'databricks.labs.lakebridge.assessments.profiler.PLATFORM_TO_SOURCE_TECHNOLOGY',
    {"synapse": "tests/resources/assessments/synapse/pipeline_config_main.yml"},
)
def test_profile_execution_with_invalid_config() -> None:
    """Test profiling execution with invalid configuration"""
    with patch('pathlib.Path.exists', return_value=False):
        profiler = Profiler()
        with pytest.raises(FileNotFoundError):
            profiler.profile("synapse")


def test_profile_execution_config_override() -> None:
    """Test successful profiling execution using actual pipeline configuration with config file override"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy the YAML file and Python script to the temp directory
        prefix = Path(__file__).parent / ".." / ".."
        config_file_src = prefix / Path("resources/assessments/pipeline_config_absolute.yml")
        config_file_dest = Path(temp_dir) / config_file_src.name
        script_src = prefix / Path("resources/assessments/db_extract.py")
        script_dest = Path(temp_dir) / script_src.name
        shutil.copy(script_src, script_dest)

        with open(config_file_src, 'r', encoding="utf-8") as file:
            config_data = yaml.safe_load(file)
            for step in config_data['steps']:
                step['extract_source'] = str(script_dest)
        with open(config_file_dest, 'w', encoding="utf-8") as file:
            yaml.safe_dump(config_data, file)

        profiler = Profiler()
        profiler.profile(platform="Synapse", extractor=None, config_file=str(config_file_dest))
        assert Path(
            "/tmp/profiler_absolute/profiler_extract.db"
        ).exists(), "Profiler extract database should be created"
