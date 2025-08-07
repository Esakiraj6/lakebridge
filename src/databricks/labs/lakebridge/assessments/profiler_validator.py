from typing import List
from dataclasses import dataclass
from pyspark.sql import (SparkSession, DataFrame)
from duckdb import DuckDBPyConnection


@dataclass(frozen=True)
class ValidationOutcome:
    """A data class that holds the outcome of a table validation check."""
    table: str
    column: str | None
    strategy: str
    outcome: str
    severity: str


class ValidationStrategy:
    """Abstract class for validating a Profiler table"""

    def validate(self, connection: DuckDBPyConnection) -> ValidationOutcome:
        raise NotImplementedError


class NullValidationCheck(ValidationStrategy):
    """Concrete class for validating null values in a profiler table"""

    def __init__(self, table, column, severity="WARN"):
        self.name = self.__class__.__name__
        self.table = table
        self.column = column
        self.severity = severity

    def validate(self, connection: DuckDBPyConnection) -> ValidationOutcome:
        """
        Validates that a column does not contain null values.
        input:
          connection: a DuckDB connection object
        """
        row_count = connection.execute(f"SELECT COUNT(*) FROM {self.table} WHERE {self.column} IS NULL").fetchone()[0]
        outcome = "PASS" if row_count > 0 else "FAIL"
        return ValidationOutcome(self.table, self.column, self.name, outcome, self.severity)


class EmptyTableValidationCheck(ValidationStrategy):
    """Concrete class for validating empty tables from a profiler run."""

    def __init__(self, table, severity="WARN"):
        self.name = self.__class__.__name__
        self.table = table
        self.severity = severity

    def validate(self, connection) -> ValidationOutcome:
        """Validates that a table is not empty.
        input:
          connection: a DuckDB connection object
        returns:
          a ValidationOutcome object
        """
        row_count = connection.execute(f"SELECT COUNT(*) FROM {self.table}").fetchone()[0]
        outcome = "PASS" if row_count > 0 else "FAIL"
        return ValidationOutcome(self.table, None, self.name, outcome, self.severity)


def build_validation_report(validations: List[ValidationStrategy],
                            connection: DuckDBPyConnection) -> list[ValidationOutcome]:
    """
    Builds a list of ValidationOutcomes from list of validation checks.
    input:
      validations: a list of ValidationStrategy objects
      connection: a DuckDB connection object
    returns: a list of ValidationOutcomes
    """
    validation_report = []
    for v in validations:
        validation_report.append(v.validate(connection))
    return validation_report
