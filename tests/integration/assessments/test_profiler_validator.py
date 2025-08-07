from pathlib import Path
import pytest

from databricks.labs.lakebridge.assessments.profiler_validator import get_profiler_extract_path


@pytest.fixture(scope="module")
def pipeline_config_path():
    prefix = Path(__file__).parent
    config_path = f"{prefix}/../../resources/assessments/pipeline_config.yml"
    return config_path


@pytest.fixture(scope="module")
def failure_pipeline_config_path():
    prefix = Path(__file__).parent
    config_path = f"{prefix}/../../resources/assessments/pipeline_config_python_failure.yml"
    return config_path


def test_get_profiler_extract_path(pipeline_config_path, failure_pipeline_config_path):
    # Parse `extract_folder` **with** a trailing "/" character
    expected_db_path = "/tmp/extracts/profiler_extract.db"
    profiler_db_path = get_profiler_extract_path(pipeline_config_path)
    assert profiler_db_path == expected_db_path

    # Parse `extract_folder` **without** a trailing "/" character
    expected_db_path = "tests/resources/assessments/profiler_extract.db"
    profiler_db_path = get_profiler_extract_path(failure_pipeline_config_path)
    assert profiler_db_path == expected_db_path
