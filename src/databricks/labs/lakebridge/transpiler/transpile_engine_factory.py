from pathlib import Path

from databricks.labs.lakebridge.transpiler.lsp.lsp_engine import LSPEngine
from databricks.labs.lakebridge.transpiler.sqlglot.sqlglot_engine import SqlglotEngine
from databricks.labs.lakebridge.transpiler.transpile_engine import TranspileEngine


class TranspileEngineFactory:
    @staticmethod
    def build_transpile_engine(transpiler_config_path: Path) -> TranspileEngine:
        # TODO remove this once sqlglot transpiler is pluggable
        if str(transpiler_config_path) == "sqlglot":
            return SqlglotEngine()
        if not transpiler_config_path.exists():
            raise ValueError(
                f"Error: Invalid value for '--transpiler-config-path': '{str(transpiler_config_path)}', file does not exist."
            )

        return LSPEngine.from_config_path(transpiler_config_path)
