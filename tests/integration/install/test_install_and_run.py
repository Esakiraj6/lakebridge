from pathlib import Path
from email import policy
from email.message import Message
from email.parser import Parser as EmailParser

from databricks.labs.lakebridge.config import TranspileConfig, TranspileResult
from databricks.labs.lakebridge.install import TranspilerRepository, WheelInstaller, MavenInstaller
from databricks.labs.lakebridge.transpiler.lsp.lsp_engine import LSPEngine
from databricks.labs.lakebridge.transpiler.transpile_engine import TranspileEngine


def process_email_content(msg: str) -> str | None:
    parser = EmailParser(policy=policy.default)
    message: Message = parser.parsestr(msg)
    result: str | None = None
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_maintype() != "multipart":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                assert charset == "utf-8", "Only UTF-8 is supported for now"
                result = (payload.decode(charset) if isinstance(payload, bytes) else str(payload)).rstrip("\n")
                break
    return result


def format_transpiled(sql: str) -> str:
    parts = sql.lower().split("\n")
    stripped = [s.strip() for s in parts]
    sql = " ".join(stripped)
    return sql


async def run_lsp_operations(
    engine: TranspileEngine,
    transpile_config: TranspileConfig,
    input_source: Path,
    sql_code: str,
) -> TranspileResult:
    """Helper function to run LSP operations."""
    await engine.initialize(transpile_config)
    dialect = transpile_config.source_dialect
    assert dialect is not None
    input_file = input_source / "some_query.sql"
    result = await engine.transpile(dialect, "databricks", sql_code, input_file)
    await engine.shutdown()
    return result


# TODO: Remove this test? We really want to test the latest published version.
async def test_installs_and_runs_local_bladebridge(bladebridge_artifact: Path, tmp_path: Path) -> None:
    labs_path = tmp_path / "labs"
    input_source = labs_path / "input_source"
    output_folder = labs_path / "output_folder"
    transpiler_repository = TranspilerRepository(labs_path)
    await _install_and_run_local_bladebridge(transpiler_repository, bladebridge_artifact, input_source, output_folder)


async def _install_and_run_local_bladebridge(
    transpiler_repository: TranspilerRepository,
    bladebridge_artifact: Path,
    input_source: Path,
    output_folder: Path,
) -> None:
    WheelInstaller(transpiler_repository, "bladebridge", "databricks-bb-plugin", bladebridge_artifact).install()
    config_path = transpiler_repository.transpiler_config_path("Bladebridge")
    lsp_engine = TranspileEngine.load_engine(config_path)
    transpile_config = TranspileConfig(
        transpiler_config_path=str(config_path),
        source_dialect="oracle",
        input_source=str(input_source),
        output_folder=str(output_folder),
        sdk_config={"cluster_id": "test_cluster"},
        skip_validation=False,
        catalog_name="catalog",
        schema_name="schema",
    )

    sql_code = "select * from employees"
    result = await run_lsp_operations(lsp_engine, transpile_config, input_source, sql_code)
    transpiled = process_email_content(result.transpiled_code)
    assert transpiled == sql_code


async def test_installs_and_runs_pypi_bladebridge(tmp_path: Path) -> None:
    labs_path = tmp_path / "labs"
    input_source = labs_path / "input_source"
    output_folder = labs_path / "output_folder"
    transpiler_repository = TranspilerRepository(labs_path)
    await _install_and_run_pypi_bladebridge(transpiler_repository, input_source, output_folder)


async def _install_and_run_pypi_bladebridge(
    transpiler_repository: TranspilerRepository,
    input_source: Path,
    output_folder: Path,
) -> None:
    WheelInstaller(transpiler_repository, "bladebridge", "databricks-bb-plugin").install()
    config_path = transpiler_repository.transpiler_config_path("Bladebridge")
    engine = TranspileEngine.load_engine(config_path)
    transpile_config = TranspileConfig(
        transpiler_config_path=str(config_path),
        source_dialect="oracle",
        input_source=str(input_source),
        output_folder=str(output_folder),
        sdk_config={"cluster_id": "test_cluster"},
        skip_validation=False,
        catalog_name="catalog",
        schema_name="schema",
    )

    sql_code = "select * from employees"
    result = await run_lsp_operations(engine, transpile_config, input_source, sql_code)
    transpiled = process_email_content(result.transpiled_code)
    assert transpiled == sql_code


# TODO: Remove this test? We really want to test the latest published version.
async def test_installs_and_runs_local_morpheus(morpheus_artifact: Path, tmp_path: Path) -> None:
    labs_path = tmp_path / "labs"
    input_source = labs_path / "input_source"
    output_folder = labs_path / "output_folder"
    transpiler_repository = TranspilerRepository(labs_path)
    await _install_and_run_local_morpheus(transpiler_repository, morpheus_artifact, input_source, output_folder)


async def _install_and_run_local_morpheus(
    transpiler_repository: TranspilerRepository,
    morpheus_artifact: Path,
    input_source: Path,
    output_folder: Path,
) -> None:
    MavenInstaller(
        transpiler_repository, "morpheus", "com.databricks.labs", "databricks-morph-plugin", morpheus_artifact
    ).install()
    config_path = transpiler_repository.transpiler_config_path("Morpheus")
    engine = LSPEngine.from_config_path(config_path)
    transpile_config = TranspileConfig(
        transpiler_config_path=str(config_path),
        source_dialect="snowflake",
        input_source=str(input_source),
        output_folder=str(output_folder),
        sdk_config={"cluster_id": "test_cluster"},
        skip_validation=False,
        catalog_name="catalog",
        schema_name="schema",
    )

    sql_code = "select * from employees;"
    result = await run_lsp_operations(engine, transpile_config, input_source, sql_code)
    transpiled = format_transpiled(result.transpiled_code)
    assert transpiled == sql_code


async def test_installs_and_runs_maven_morpheus(tmp_path: Path) -> None:
    labs_path = tmp_path / "labs"
    input_source = labs_path / "input_source"
    output_folder = labs_path / "output_folder"
    transpiler_repository = TranspilerRepository(labs_path)
    await _install_and_run_maven_morpheus(transpiler_repository, input_source, output_folder)


async def _install_and_run_maven_morpheus(
    transpiler_repository: TranspilerRepository,
    input_source: Path,
    output_folder: Path,
) -> None:
    MavenInstaller(transpiler_repository, "morpheus", "com.databricks.labs", "databricks-morph-plugin").install()
    config_path = transpiler_repository.transpiler_config_path("Morpheus")
    engine = LSPEngine.from_config_path(config_path)
    transpile_config = TranspileConfig(
        transpiler_config_path=str(config_path),
        source_dialect="snowflake",
        input_source=str(input_source),
        output_folder=str(output_folder),
        sdk_config={"cluster_id": "test_cluster"},
        skip_validation=False,
        catalog_name="catalog",
        schema_name="schema",
    )

    sql_code = "select * from employees;"
    result = await run_lsp_operations(engine, transpile_config, input_source, sql_code)
    transpiled = format_transpiled(result.transpiled_code)
    assert transpiled == sql_code
