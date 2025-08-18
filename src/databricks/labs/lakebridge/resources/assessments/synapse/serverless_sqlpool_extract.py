import json
import sys
from databricks.labs.lakebridge.resources.assessments.synapse.common.functions import (
    arguments_loader,
    get_config,
    save_resultset_to_db,
    get_serverless_database_groups,
    get_max_column_value_duckdb,
    set_logger,
)
from databricks.labs.lakebridge.resources.assessments.synapse.common.queries import SynapseQueries
from databricks.labs.lakebridge.resources.assessments.synapse.common.connector import (
    create_credential_manager,
    get_sqlpool_reader,
)
from sqlalchemy import text


def execute():
    logger = set_logger(__name__)
    db_path, creds_file = arguments_loader(desc="Synapse Synapse Serverless SQL Pool Extract Script")

    cred_manager = create_credential_manager(creds_file)
    config = cred_manager.get_credentials("synapse")["workspace"]

    try:
        synapse_workspace_settings = get_config(creds_file)["synapse"]
        synapse_profiler_settings = synapse_workspace_settings["profiler"]

        if not synapse_profiler_settings.get("exclude_serverless_sql_pool", False):

            # Databases
            database_query = SynapseQueries.list_databases()
            connection = get_sqlpool_reader(config, 'master', 'serverless_sql_endpoint')
            result = connection.execute(text(database_query))
            save_resultset_to_db(result, "serverless_databases", db_path, mode="overwrite")

            serverless_database_groups_in_scope = get_serverless_database_groups(db_path)
            logger.info(f"serverless db in scope: {serverless_database_groups_in_scope}")

            for idx, collation_name in enumerate(serverless_database_groups_in_scope):
                mode = "overwrite" if idx == 0 else "append"
                databases = serverless_database_groups_in_scope[collation_name]

                for db_name in databases:
                    connection = get_sqlpool_reader(config, db_name, 'serverless_sql_endpoint')
                    # tables
                    table_name = 'serverless_tables'
                    table_query = SynapseQueries.list_tables(db_name)
                    logger.info(f"Loading '{table_name}' for pool: %s", db_name)
                    result = connection.execute(text(table_query))
                    save_resultset_to_db(result, table_name, db_path, mode=mode)

                    # columns
                    table_name = "serverless_columns"
                    column_query = SynapseQueries.list_columns(db_name)
                    logger.info(f"Loading '{table_name}' for pool: %s", db_name)
                    result = connection.execute(text(column_query))
                    save_resultset_to_db(result, table_name, db_path, mode=mode)

                    # views
                    table_name = "serverless_views"
                    view_query = SynapseQueries.list_views(db_name)
                    logger.info(f"Loading '{table_name}' for pool: %s", db_name)
                    result = connection.execute(text(view_query))
                    save_resultset_to_db(result, table_name, db_path, mode=mode)

                    # Routines
                    table_name = "serverless_routines"
                    view_query = SynapseQueries.list_routines(db_name, True)
                    logger.info(f"Loading '{table_name}' for pool: %s", db_name)
                    result = connection.execute(text(view_query))
                    save_resultset_to_db(result, table_name, db_path, mode=mode)

                    mode = "append"

            pool_name = "serverless"
            # Data Processed
            table_name = "serverless_data_processed"
            logger.info(f"Loading '{table_name}' for pool: %s", pool_name)
            data_processed_query = SynapseQueries.data_processed(pool_name)

            session_result = connection.execute(text(data_processed_query))
            save_resultset_to_db(session_result, table_name, db_path, mode="append")

            # Activity Extract:
            table_name = "serverless_sessions"
            logger.info(f"Loading '{table_name}' for pool: %s", pool_name)
            prev_max_login_time = get_max_column_value_duckdb("login_time", table_name, db_path)
            session_query = SynapseQueries.list_serverless_sessions(pool_name, prev_max_login_time)

            session_result = connection.execute(text(session_query))
            save_resultset_to_db(session_result, table_name, db_path, mode="append")

            table_name = "serverless_session_requests"
            logger.info(f"Loading '{table_name}' for pool: %s", pool_name)
            prev_max_end_time = get_max_column_value_duckdb("start_time", table_name, db_path)
            session_request_query = SynapseQueries.list_serverless_requests(pool_name, prev_max_end_time)

            session_request_result = connection.execute(text(session_request_query))
            save_resultset_to_db(session_request_result, table_name, db_path, mode="append")

            table_name = "serverless_query_stats"
            logger.info(f"Loading '{table_name}' for pool: %s", pool_name)
            max_last_execution_time = get_max_column_value_duckdb("last_execution_time", table_name, db_path)
            query_stats = SynapseQueries.list_query_stats(max_last_execution_time)

            session_result = connection.execute(text(query_stats))
            save_resultset_to_db(session_result, table_name, db_path, mode="append")

            table_name = "serverless_requests_history"
            logger.info(f"Loading '{table_name}' for pool: %s", pool_name)
            max_end_time = get_max_column_value_duckdb("end_time", table_name, db_path)
            query_history = SynapseQueries.query_requests_history(max_end_time)

            session_request_result = connection.execute(text(query_history))
            save_resultset_to_db(session_request_result, table_name, db_path, mode="append")

        else:
            logger.info("'exclude_serverless_sql_pool' configuration is set to True.Skipping Serverless Pool extracts.")

        print(json.dumps({"status": "success", "message": "Data loaded successfully"}))

    except Exception as e:
        logger.error(f"Failed to extract info for Synapse Serverless SQL Pool: {str(e)}")
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    execute()
