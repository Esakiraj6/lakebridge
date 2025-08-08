from pathlib import Path
import pytest
import duckdb

from databricks.labs.lakebridge.assessments.profiler_validator import (
    get_profiler_extract_path,
    EmptyTableValidationCheck,
    build_validation_report,
)
from integration.assessments.utils.profiler_extract_utils import build_mock_synapse_extract


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


@pytest.fixture(scope="module")
def mock_synapse_profiler_extract():
    synapse_extract_path = build_mock_synapse_extract()
    return synapse_extract_path


def test_get_profiler_extract_path(pipeline_config_path, failure_pipeline_config_path):
    # Parse `extract_folder` **with** a trailing "/" character
    expected_db_path = "/tmp/extracts/profiler_extract.db"
    profiler_db_path = get_profiler_extract_path(pipeline_config_path)
    assert profiler_db_path == expected_db_path

    # Parse `extract_folder` **without** a trailing "/" character
    expected_db_path = "tests/resources/assessments/profiler_extract.db"
    profiler_db_path = get_profiler_extract_path(failure_pipeline_config_path)
    assert profiler_db_path == expected_db_path


def test_validate_non_empty_tables(mock_synapse_profiler_extract):
    with duckdb.connect(database=mock_synapse_profiler_extract) as duck_conn:
        validation_checks = []
        # Get a list of all tables in profiler extract
        # Alternatively, this can be a pre-defined list (follow-up test case)
        tables = duck_conn.execute("SHOW ALL TABLES").fetchall()
        for table in tables:
            fq_table_name = f"{table[0]}.{table[1]}.{table[2]}"
            empty_check = EmptyTableValidationCheck(fq_table_name)
            validation_checks.append(empty_check)
        report = build_validation_report(validation_checks, duck_conn)
        assert len(report) == 3
