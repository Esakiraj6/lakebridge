from databricks.labs.lakebridge.config import DatabaseConfig
from databricks.labs.lakebridge.reconcile.connectors.data_source import DataSource
from databricks.labs.lakebridge.reconcile.recon_config import Schema, Table


class SchemaService:

    @staticmethod
    def get_schemas(
        source: DataSource,
        target: DataSource,
        table_conf: Table,
        database_config: DatabaseConfig,
    ) -> tuple[list[Schema], list[Schema]]:
        src_schema = source.get_schema(
            catalog=database_config.source_catalog,
            schema=database_config.source_schema,
            table=table_conf.source_name,
        )

        tgt_schema = target.get_schema(
            catalog=database_config.target_catalog,
            schema=database_config.target_schema,
            table=table_conf.target_name,
        )

        sanitized_src_schema = SchemaService.escape_schema(src_schema)
        sanitized_tgt_schema = SchemaService.escape_schema(tgt_schema)

        return sanitized_src_schema, sanitized_tgt_schema

    @staticmethod
    def escape_schema(columns: list[Schema]) -> list[Schema]:
        return [SchemaService._escape_schema_column(c) for c in columns]

    @staticmethod
    def _escape_schema_column(column: Schema) -> Schema:
        return Schema(
            column_name=SchemaService.escape_column(column.column_name),
            data_type=column.data_type,
            is_escaped=True
        )

    @staticmethod
    def escape_column(column: str) -> str:
        return f"`{column}`"
