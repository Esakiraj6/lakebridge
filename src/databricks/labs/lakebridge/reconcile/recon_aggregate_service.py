from datetime import datetime

from pyspark.sql import SparkSession
from databricks.sdk import WorkspaceClient

from databricks.labs.lakebridge.config import ReconcileConfig, TableRecon
from databricks.labs.lakebridge.reconcile import utils
from databricks.labs.lakebridge.reconcile.exception import DataSourceRuntimeException, ReconciliationException
from databricks.labs.lakebridge.reconcile.execute import Reconciliation
from databricks.labs.lakebridge.reconcile.recon_capture import (
    ReconIntermediatePersist,
    generate_final_reconcile_aggregate_output,
)
from databricks.labs.lakebridge.reconcile.recon_config import Table, Schema, AGG_RECONCILE_OPERATION_NAME
from databricks.labs.lakebridge.reconcile.recon_output_config import (
    ReconcileProcessDuration,
    AggregateQueryOutput,
    DataReconcileOutput,
)
from databricks.labs.lakebridge.reconcile.recon_service import ReconService
from databricks.labs.lakebridge.reconcile.schema_service import SchemaService
from databricks.labs.lakebridge.reconcile.table_service import NormalizeReconConfigService


class ReconAggregateService:
    @staticmethod
    def reconcile_aggregates(
        ws: WorkspaceClient,
        spark: SparkSession,
        table_recon: TableRecon,
        reconcile_config: ReconcileConfig,
        local_test_run: bool = False,
    ):
        reconciler, recon_capture = ReconService.create_recon_dependencies(ws, spark, reconcile_config, local_test_run)

        # Get the Aggregated Reconciliation Output for each table
        for table_conf in table_recon.tables:
            normalized_table_conf = NormalizeReconConfigService(
                reconciler.source, reconciler.target
            ).normalize_recon_table_config(table_conf)
            recon_process_duration = ReconcileProcessDuration(start_ts=str(datetime.now()), end_ts=None)
            try:
                src_schema, tgt_schema = SchemaService.get_normalized_schemas(
                    source=reconciler.source,
                    target=reconciler.target,
                    table_conf=normalized_table_conf,
                    database_config=reconcile_config.database_config,
                )
            except DataSourceRuntimeException as e:
                raise ReconciliationException(message=str(e)) from e

            assert normalized_table_conf.aggregates, "Aggregates must be defined for Aggregates Reconciliation"

            table_reconcile_agg_output_list: list[AggregateQueryOutput] = (
                ReconAggregateService._run_reconcile_aggregates(
                    reconciler=reconciler,
                    table_conf=normalized_table_conf,
                    src_schema=src_schema,
                    tgt_schema=tgt_schema,
                )
            )

            recon_process_duration.end_ts = str(datetime.now())

            # Persist the data to the delta tables
            recon_capture.store_aggregates_metrics(
                reconcile_agg_output_list=table_reconcile_agg_output_list,
                table_conf=normalized_table_conf,
                recon_process_duration=recon_process_duration,
            )

            (
                ReconIntermediatePersist(
                    spark=spark,
                    path=utils.generate_volume_path(normalized_table_conf, reconcile_config.metadata_config),
                ).clean_unmatched_df_from_volume()
            )

        return ReconService.verify_successful_reconciliation(
            generate_final_reconcile_aggregate_output(
                recon_id=recon_capture.recon_id,
                spark=spark,
                metadata_config=reconcile_config.metadata_config,
                local_test_run=local_test_run,
            ),
            operation_name=AGG_RECONCILE_OPERATION_NAME,
        )

    @staticmethod
    def _run_reconcile_aggregates(
        reconciler: Reconciliation,
        table_conf: Table,
        src_schema: list[Schema],
        tgt_schema: list[Schema],
    ) -> list[AggregateQueryOutput]:
        try:
            return reconciler.reconcile_aggregates(table_conf, src_schema, tgt_schema)
        except DataSourceRuntimeException as e:
            return [AggregateQueryOutput(reconcile_output=DataReconcileOutput(exception=str(e)), rule=None)]
