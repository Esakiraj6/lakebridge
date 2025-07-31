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

    @staticmethod
    def _val_path(path: str) -> bool:
        """Validates a path for both existing files and writable files."""
        try:
            path_obj = Path(path) if not isinstance(path, Path) else path

            if path_obj.exists():
                return os.access(path_obj, os.W_OK)

            parent = path_obj.parent
            return parent.exists() and os.access(parent, os.W_OK)

        except (OSError, ValueError):
            logger.warning("Could not validate path: %s", path)
            return False

    def _get_source_directory(self) -> Path:
        """Get and validate the source directory from user input."""
        directory_str = self._prompts.question(
            "Enter full path to the source directory",
            default=Path.cwd().as_posix(),
            validate=self._val_path,
        )
        return Path(directory_str).resolve()

    def _get_result_file_path(self, directory: Path) -> Path:
        """Get the result file path - accepts either filename or full path."""
        filename = self._prompts.question(
            "Enter report file name or custom export path including file name without extension",
            default=f"{directory.as_posix()}/lakebridge-analyzer-results.xlsx",
            validate=self._val_path,
        )
        return (
            directory / Path(filename).with_suffix(".xlsx")
            if len(filename.split("/")) == 1
            else Path(filename).with_suffix(".xlsx")
        )

    def _run_prompt_analyzer(self):
        """Run the analyzer: prompt guided"""
        directory = self._get_source_directory()
        result = self._get_result_file_path(directory)

        platform = self._prompts.choice("Select the source technology", self.supported_source_technologies())
        technology = _PLATFORM_TO_SOURCE_TECHNOLOGY.get(platform)

        self._run_binary(directory, result, technology, self._is_debug)

        logger.info(f"Successfully Analyzed files in ${directory} for ${technology} and saved report to {result}")

    def _run_arg_analyzer(self, source_dir: str | None, results_dir: str | None, technology: str | None):
        """Run the analyzer: arg guided"""
        if source_dir is None or results_dir is None or technology is None:
            logger.error("All arguments (--source-directory, --report-file, --source-tech) must be provided")
            return

        if technology not in Analyzer.supported_source_technologies():
            logger.warning(f"Invalida source technology {technology}")
            technology = self._prompts.choice("Select the source technology", Analyzer.supported_source_technologies())

        if self._val_path(source_dir) and self._val_path(results_dir):
            self.analyze(Path(source_dir), Path(results_dir).with_suffix(".xlsx"), technology, self._is_debug)

    def run_analyzer(
        self, source_dir: str | None = None, results_dir: str | None = None, technology: str | None = None
    ):
        """Run the analyzer."""
        if not any([source_dir, results_dir, technology]):
            self._run_prompt_analyzer()
            return

        self._run_arg_analyzer(source_dir, results_dir, technology)
