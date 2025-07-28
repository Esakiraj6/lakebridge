from pathlib import Path

from databricks.labs.lakebridge.transpiler.lsp.lsp_engine import LSPEngine
from databricks.labs.lakebridge.transpiler.sqlglot.sqlglot_engine import SqlglotEngine
from databricks.labs.lakebridge.transpiler.transpile_engine_factory import TranspileEngineFactory
from tests.unit.conftest import path_to_resource


def test_build_sqlglot_engine():
    engine = TranspileEngineFactory.build_transpile_engine("sqlglot")
    assert isinstance(engine, SqlglotEngine)


def test_build_lsp_engine():
    config_path = path_to_resource("lsp_transpiler", "lsp_config.yml")
    engine = TranspileEngineFactory.build_transpile_engine(Path(config_path))
    assert isinstance(engine, LSPEngine)
