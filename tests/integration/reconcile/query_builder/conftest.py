import pytest
from pyspark.sql import DataFrame

from tests.conftest import oracle_schema_fixture_factory, ansi_schema_fixture_factory
from databricks.labs.lakebridge.reconcile.connectors.data_source import DataSource
from databricks.labs.lakebridge.reconcile.connectors.dialect_utils import DialectUtils
from databricks.labs.lakebridge.reconcile.connectors.models import NormalizedIdentifier
from databricks.labs.lakebridge.reconcile.normalize_recon_config_service import NormalizeReconConfigService
from databricks.labs.lakebridge.reconcile.recon_config import (
    JdbcReaderOptions,
    Schema,
    Transformation,
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


@pytest.fixture
def snowflake_table_conf_with_opts(normalize_config_service: NormalizeReconConfigService, table_conf_with_opts):
    conf = normalize_config_service.normalize_recon_table_config(table_conf_with_opts)
    conf.transformations = [  # SQL has to be valid
        Transformation(column_name="`s_address`", source="trim(\"s_address\")", target="trim(`s_address_t`)"),
        Transformation(column_name="`s_phone`", source="trim(\"s_phone\")", target="trim(`s_phone_t`)"),
        Transformation(column_name="`s_name`", source="trim(\"s_name\")", target="trim(`s_name`)"),
    ]
    if conf.filters:
        conf.filters.source = "\"s_name\"='t' and \"s_address\"='a'"
    return conf


@pytest.fixture
def table_schema_oracle_ansi(table_schema):
    src_schema, tgt_schema = table_schema
    src_schema = [oracle_schema_fixture_factory(s.column_name, s.data_type) for s in src_schema]
    tgt_schema = [ansi_schema_fixture_factory(s.column_name, s.data_type) for s in tgt_schema]
    return src_schema, tgt_schema

@pytest.fixture
def table_schema_ansi_ansi(table_schema):
    src_schema, tgt_schema = table_schema
    src_schema = [ansi_schema_fixture_factory(s.column_name, s.data_type) for s in src_schema]
    tgt_schema = [ansi_schema_fixture_factory(s.column_name, s.data_type) for s in tgt_schema]
    return src_schema, tgt_schema
