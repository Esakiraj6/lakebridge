from pathlib import Path

PRODUCT_NAME = "lakebridge"
PRODUCT_PATH_PREFIX = Path.home() / ".databricks" / "labs" / PRODUCT_NAME / "lib"

PLATFORM_TO_SOURCE_TECHNOLOGY = {
    "synapse": "src/databricks/labs/lakebridge/resources/assessments/synapse/pipeline_config.yml",
}

# TODO modify this PLATFORM_TO_SOURCE_TECHNOLOGY.keys() once all platforms are supported
PROFILER_SOURCE_SYSTEM = ["mssql", "synapse"]

CONNECTOR_REQUIRED = {
    "synapse": False,
    "mssql": True,
}
