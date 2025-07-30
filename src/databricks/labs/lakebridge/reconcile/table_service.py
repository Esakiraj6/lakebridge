import dataclasses

from databricks.labs.lakebridge.reconcile.connectors.data_source import DataSource
from databricks.labs.lakebridge.reconcile.recon_config import (
    Table,
    Aggregate,
    ColumnMapping,
    Transformation,
    ColumnThresholds,
)


class NormalizeReconConfigService:
    def __init__(self, source: DataSource):
        self.data_source = source

    def normalize_recon_table_config(self, table: Table) -> Table:
        escaped_table = dataclasses.replace(table)

        self._normalize_sampling(escaped_table)
        self._normalize_aggs(escaped_table)
        self._normalize_join_cols(escaped_table)
        self._normalize_select_cols(escaped_table)
        self._normalize_drop_cols(escaped_table)
        self._normalize_col_mappings(escaped_table)
        self._normalize_transformations(escaped_table)
        self._normalize_col_thresholds(escaped_table)

        escaped_table.is_columns_escaped = True
        return escaped_table

    def _normalize_sampling(self, table: Table):
        if table.sampling_options:
            escaped_sampling = dataclasses.replace(table.sampling_options)
            escaped_sampling.stratified_columns = (
                [self.data_source.normalize_identifier(c) for c in escaped_sampling.stratified_columns]
                if escaped_sampling.stratified_columns
                else None
            )
            table.sampling_options = escaped_sampling
        return table

    def _normalize_aggs(self, table: Table):
        escaped = [self._normalize_agg(a) for a in table.aggregates] if table.aggregates else None
        table.aggregates = escaped
        return table

    def _normalize_agg(self, agg: Aggregate) -> Aggregate:
        escaped = dataclasses.replace(agg)
        escaped.agg_columns = [self.data_source.normalize_identifier(c) for c in escaped.agg_columns]
        escaped.group_by_columns = (
            [self.data_source.normalize_identifier(c) for c in escaped.group_by_columns]
            if escaped.group_by_columns
            else None
        )
        return escaped

    def _normalize_join_cols(self, table: Table):
        table.join_columns = (
            [self.data_source.normalize_identifier(c) for c in table.join_columns] if table.join_columns else None
        )
        return table

    def _normalize_select_cols(self, table: Table):
        table.select_columns = (
            [self.data_source.normalize_identifier(c) for c in table.select_columns] if table.select_columns else None
        )
        return table

    def _normalize_drop_cols(self, table: Table):
        table.drop_columns = (
            [self.data_source.normalize_identifier(c) for c in table.drop_columns] if table.drop_columns else None
        )
        return table

    def _normalize_col_mappings(self, table: Table):
        table.column_mapping = (
            [self._normalize_col_mapping(m) for m in table.column_mapping] if table.column_mapping else None
        )
        return table

    def _normalize_col_mapping(self, mapping: ColumnMapping):
        return ColumnMapping(
            source_name=self.data_source.normalize_identifier(mapping.source_name),
            target_name=self.data_source.normalize_identifier(mapping.target_name),
        )

    def _normalize_transformations(self, table: Table):
        table.transformations = (
            [self._normalize_transformation(t) for t in table.transformations] if table.transformations else None
        )
        return table

    def _normalize_transformation(self, transform: Transformation):
        escaped = dataclasses.replace(transform)
        escaped.column_name = self.data_source.normalize_identifier(transform.column_name)
        return escaped

    def _normalize_col_thresholds(self, table: Table):
        table.column_thresholds = (
            [self._normalize_col_threshold(t) for t in table.column_thresholds] if table.column_thresholds else None
        )
        return table

    def _normalize_col_threshold(self, threshold: ColumnThresholds):
        escaped = dataclasses.replace(threshold)
        escaped.column_name = self.data_source.normalize_identifier(threshold.column_name)
        return escaped

    # TODO implement
    def _normalize_filters(self, table: Table):
        return table
