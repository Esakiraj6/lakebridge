import os
from pathlib import Path

from databricks.labs.blueprint.entrypoint import get_logger
from databricks.labs.blueprint.tui import Prompts

from databricks.labs.bladespector.analyzer import Analyzer, _PLATFORM_TO_SOURCE_TECHNOLOGY

logger = get_logger(__file__)


class LakebridgeAnalyzer(Analyzer):
    def __init__(self, prompts: Prompts, is_debug: bool = False):
        self._prompts = prompts
        self._is_debug = is_debug
        super().__init__()

    def _get_source_directory(self) -> Path:
        """Get and validate the source directory from user input."""
        directory_str = self._prompts.question(
            "Enter full path to the source directory",
            default=Path.cwd().as_posix(),
            validate=lambda p: Path(p).exists() and os.access(p, os.W_OK),
        )
        return Path(directory_str).resolve()

    def _get_result_file_path(self, directory: Path) -> Path:
        """Get the result file path - accepts either filename or full path."""
        filename = self._prompts.question(
            "Enter report file name or custom export path including file name without extension",
            default=f"{directory.as_posix()}/lakebridge-analyzer-results.xlsx",
            validate=lambda p: Path(p).parent.exists() and os.access(Path(p).parent, os.W_OK),
        )
        return (
            directory / Path(filename).with_suffix(".xlsx")
            if len(filename.split("/")) == 1
            else Path(filename).with_suffix(".xlsx")
        )

    def run_analyzer(self):
        """Run the analyzer."""
        directory = self._get_source_directory()
        result = self._get_result_file_path(directory)

        platform = self._prompts.choice("Select the source technology", self.supported_source_technologies())
        technology = _PLATFORM_TO_SOURCE_TECHNOLOGY.get(platform)

        self._run_binary(directory, result, technology, self._is_debug)

        logger.info(f"Successfully Analyzed files in ${directory} for ${technology} and saved report to {result}")
