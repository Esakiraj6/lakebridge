import shutil
from collections.abc import Generator
from pathlib import Path

import pytest

from databricks.labs.lakebridge.install import MavenInstaller, TranspilerRepository, WheelInstaller, WorkspaceInstaller

# TODO: These should run as part of the integration tests, not a separate test suite.


@pytest.fixture()
def transpiler_repository(tmp_path: Path) -> Generator[TranspilerRepository, None, None]:
    resources_folder = Path(__file__).parent.parent.parent / "resources" / "transpiler_configs"
    labs_path = tmp_path / "labs"
    repository = TranspilerRepository(labs_path=labs_path)
    for transpiler in ("bladebridge", "morpheus"):
        install_directory = repository.transpilers_path() / transpiler / "lib"
        install_directory.mkdir(parents=True)
        source = resources_folder / transpiler / "lib" / "config.yml"
        target = install_directory / "config.yml"
        # Just the config file, not the whole thing: we're only testing the repository and transpiler metadata.
        shutil.copyfile(source, target)
    yield repository


def test_gets_maven_artifact_version() -> None:
    version = MavenInstaller.get_current_maven_artifact_version("com.databricks", "databricks-connect")
    assert version is not None
    check_valid_version(version)


def test_downloads_from_maven(tmp_path: Path) -> None:
    pom_path = tmp_path / "pom.xml"
    success = MavenInstaller.download_artifact_from_maven(
        "com.databricks", "databricks-connect", "16.0.0", pom_path, extension="pom"
    )
    assert success
    assert pom_path.exists()
    assert pom_path.stat().st_size == 5_684


def test_gets_pypi_artifact_version() -> None:
    version = WheelInstaller.get_latest_artifact_version_from_pypi("databricks-labs-remorph")
    assert version is not None
    check_valid_version(version)


def test_lists_all_transpiler_names(transpiler_repository: TranspilerRepository) -> None:
    transpiler_names = transpiler_repository.all_transpiler_names()
    assert transpiler_names == {'Morpheus', 'Bladebridge'}


def test_lists_all_dialects(transpiler_repository: TranspilerRepository) -> None:
    dialects = transpiler_repository.all_dialects()
    assert dialects == {
        'athena',
        'bigquery',
        'datastage',
        'greenplum',
        'informatica (desktop edition)',
        'mssql',
        'netezza',
        'oracle',
        'redshift',
        'snowflake',
        'synapse',
        'teradata',
        'tsql',
    }


def test_lists_dialect_transpilers(transpiler_repository: TranspilerRepository) -> None:
    transpilers = transpiler_repository.transpilers_with_dialect("snowflake")
    assert transpilers == {'Morpheus', 'Bladebridge'}
    transpilers = transpiler_repository.transpilers_with_dialect("datastage")
    assert transpilers == {'Bladebridge'}


def check_valid_version(version: str) -> None:
    parts = version.split(".")
    for _, part in enumerate(parts):
        try:
            _ = int(part)
        except ValueError:
            assert False, f"{version} does not look like a valid semver"


def test_java_version() -> None:
    result = WorkspaceInstaller.find_java()
    match result:
        case None:
            # Fine, no Java available.
            pass
        case (java_home, tuple(version)):
            assert java_home.exists() and version >= (11, 0, 0, 0)
        case _:
            pytest.fail(f"Unexpected result from WorkspaceInstaller.find_java(): {result!r}")
