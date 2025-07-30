from databricks.labs.lakebridge.config import DatabaseConfig
from databricks.labs.lakebridge.reconcile.connectors.data_source import DataSource
from databricks.labs.lakebridge.reconcile.recon_config import Schema, Table


class SchemaService:

    @staticmethod
    def get_normalized_schemas(
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

        sanitized_src_schema = SchemaService.normalize_schema(source, src_schema)
        sanitized_tgt_schema = SchemaService.normalize_schema(target, tgt_schema)

        return sanitized_src_schema, sanitized_tgt_schema

    @staticmethod
    def normalize_schema(data_source: DataSource, columns: list[Schema]) -> list[Schema]:
        return [SchemaService._normalize_schema_column(data_source, c) for c in columns]

    @staticmethod
    def _normalize_schema_column(data_source: DataSource, column: Schema) -> Schema:
        return Schema(
            column_name=data_source.normalize_identifier(column.column_name),
            data_type=column.data_type,
            is_escaped=True
        )
