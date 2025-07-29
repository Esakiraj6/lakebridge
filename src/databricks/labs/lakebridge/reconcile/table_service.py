import dataclasses

from databricks.labs.lakebridge.reconcile.recon_config import Table, Aggregate, ColumnMapping, Transformation, \
    ColumnThresholds
from databricks.labs.lakebridge.reconcile.schema_service import SchemaService


class TableService:
    @staticmethod
    def escape_recon_tables_configs(tables: list[Table]) -> list[Table]:
        return [TableService.escape_recon_table_config(t) for t in tables]

    @staticmethod
    def escape_recon_table_config(table: Table) -> Table:
        escaped_table = dataclasses.replace(table)

        TableService._escape_sampling(escaped_table)
        TableService._escape_aggs(escaped_table)
        TableService._escape_join_cols(escaped_table)
        TableService._escape_select_cols(escaped_table)
        TableService._escape_drop_cols(escaped_table)
        TableService._escape_col_mappings(escaped_table)
        TableService._escape_transformations(escaped_table)
        TableService._escape_col_thresholds(escaped_table)

        escaped_table.is_columns_escaped = True
        return escaped_table

    @staticmethod
    def _escape_sampling(table: Table):
        escaped_sampling = dataclasses.replace(table.sampling_options)
        escaped_sampling.stratified_columns = [SchemaService.escape_column(c) for c in
                                               escaped_sampling.stratified_columns]
        table.sampling_options = escaped_sampling
        return table

    @staticmethod
    def _escape_aggs(table: Table):
        escaped = [TableService._escape_agg(a) for a in table.aggregates]
        table.aggregates = escaped
        return table

    @staticmethod
    def _escape_agg(agg: Aggregate) -> Aggregate:
        escaped = dataclasses.replace(agg)
        escaped.agg_columns = [SchemaService.escape_column(c) for c in escaped.agg_columns]
        escaped.group_by_columns = [SchemaService.escape_column(c) for c in escaped.group_by_columns]
        return escaped

    @staticmethod
    def _escape_join_cols(table: Table):
        table.join_columns = [SchemaService.escape_column(c) for c in table.join_columns]
        return table

    @staticmethod
    def _escape_select_cols(table: Table):
        table.select_columns = [SchemaService.escape_column(c) for c in table.select_columns]
        return table

    @staticmethod
    def _escape_drop_cols(table: Table):
        table.drop_columns = [SchemaService.escape_column(c) for c in table.drop_columns]
        return table

    @staticmethod
    def _escape_col_mappings(table: Table):
        table.column_mapping = [TableService._escape_col_mapping(m) for m in table.column_mapping]
        return table

    @staticmethod
    def _escape_col_mapping(mapping: ColumnMapping):
        return ColumnMapping(
            source_name=SchemaService.escape_column(mapping.source_name),
            target_name=SchemaService.escape_column(mapping.target_name),
        )

    @staticmethod
    def _escape_transformations(table: Table):
        table.transformations = [TableService._escape_transformation(t) for t in table.transformations]
        return table

    @staticmethod
    def _escape_transformation(transform: Transformation):
        escaped = dataclasses.replace(transform)
        escaped.column_name = SchemaService.escape_column(transform.column_name)
        return escaped

    @staticmethod
    def _escape_col_thresholds(table: Table):
        table.column_thresholds = [TableService._escape_col_threshold(t) for t in table.column_thresholds]
        return table

    @staticmethod
    def _escape_col_threshold(threshold: ColumnThresholds):
        escaped = dataclasses.replace(threshold)
        escaped.column_name = SchemaService.escape_column(threshold.column_name)
        return escaped

    # TODO implement
    @staticmethod
    def _escape_filters(table: Table):
        return table
