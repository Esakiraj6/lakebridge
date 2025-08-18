import logging
from pathlib import Path

from databricks.labs.lakebridge.assessments.pipeline import PipelineClass
from databricks.labs.lakebridge.assessments.profiler_config import PipelineConfig
from databricks.labs.lakebridge.connections.database_manager import DatabaseManager
from databricks.labs.lakebridge.connections.credential_manager import (
    create_credential_manager,
)
from databricks.labs.lakebridge.connections.env_getter import EnvGetter
from databricks.labs.lakebridge.assessments import (
    PRODUCT_NAME,
    PRODUCT_PATH_PREFIX,
    PLATFORM_TO_SOURCE_TECHNOLOGY,
    CONNECTOR_REQUIRED,
)

logger = logging.getLogger(__name__)


class Profiler:

    @classmethod
    def supported_source_technologies(cls) -> list[str]:
        return list(PLATFORM_TO_SOURCE_TECHNOLOGY.keys())

    @staticmethod
    def path_modifier(config_file: str | Path) -> PipelineConfig:
        # TODO: Make this work install during developer mode
        config = PipelineClass.load_config_from_yaml(config_file)
        for step in config.steps:
            step.extract_source = f"{PRODUCT_PATH_PREFIX}/{step.extract_source}"
        return config

    def profile(self, platform: str, extractor: DatabaseManager | None = None, config_file: str | Path | None = None):
        platform = platform.lower()
        if config_file:
            pipeline_config = PipelineClass.load_config_from_yaml(config_file)
        else:
            config_path = PLATFORM_TO_SOURCE_TECHNOLOGY.get(platform, None)
            if not config_path:
                raise ValueError(f"Unsupported platform: {platform}")
            config_full_path = self._locate_config(config_path)
            pipeline_config = Profiler.path_modifier(config_full_path)
        self._execute(platform, pipeline_config, extractor)

    def _setup_extractor(self, platform: str) -> DatabaseManager | None:
        if not CONNECTOR_REQUIRED[platform]:
            return None
        cred_manager = create_credential_manager(PRODUCT_NAME, EnvGetter())
        connect_config = cred_manager.get_credentials(platform)
        return DatabaseManager(platform, connect_config)

    def _execute(self, platform: str, pipeline_config: PipelineConfig, extractor=None):
        try:
            if extractor is None:
                extractor = self._setup_extractor(platform)

            result = PipelineClass(pipeline_config, extractor).execute()
            logger.info(f"Profile execution has completed successfully for {platform} for more info check: {result}.")
        except FileNotFoundError as e:
            logger.error(f"Configuration file not found for source {platform}: {e}")
            raise FileNotFoundError(f"Configuration file not found for source {platform}: {e}") from e
        except Exception as e:
            logger.error(f"Error executing pipeline for source {platform}: {e}")
            raise RuntimeError(f"Pipeline execution failed for source {platform} : {e}") from e

    def _locate_config(self, config_path: str) -> Path:
        config_file = PRODUCT_PATH_PREFIX / config_path
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        return config_file
