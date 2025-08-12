import pytest
from pyspark.sql import DataFrame

from databricks.labs.lakebridge.reconcile.connectors.data_source import DataSource
from databricks.labs.lakebridge.reconcile.connectors.dialect_utils import DialectUtils
from databricks.labs.lakebridge.reconcile.connectors.models import NormalizedIdentifier
from databricks.labs.lakebridge.reconcile.normalize_recon_config_service import NormalizeReconConfigService
from databricks.labs.lakebridge.reconcile.recon_config import (
    JdbcReaderOptions,
    Schema,
)


class FakeDataSource(DataSource):

    def __init__(self, delimiter: str):
        self.delimiter = delimiter

    def get_schema(self, catalog: str | None, schema: str, table: str) -> list[Schema]:
        raise RuntimeError("Not implemented")

    def normalize_identifier(self, identifier: str) -> NormalizedIdentifier:
        return DialectUtils.normalize_identifier(identifier, self.delimiter, self.delimiter)

    def read_data(
        self, catalog: str | None, schema: str, table: str, query: str, options: JdbcReaderOptions | None
    ) -> DataFrame:
        raise RuntimeError("Not implemented")


@pytest.fixture
def fake_oracle_datasource() -> FakeDataSource:
    return FakeDataSource("\"")


@pytest.fixture
def fake_databricks_datasource() -> FakeDataSource:
    return FakeDataSource("`")


@pytest.fixture
def normalize_config_service(fake_databricks_datasource) -> NormalizeReconConfigService:
    return NormalizeReconConfigService(fake_databricks_datasource, fake_databricks_datasource)
    # If the config is not escaped or is ansi, then databricks can be used


@pytest.fixture
def normalized_table_conf_with_opts(normalize_config_service: NormalizeReconConfigService, table_conf_with_opts):
    return normalize_config_service.normalize_recon_table_config(table_conf_with_opts)
