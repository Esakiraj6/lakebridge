import pytest
from databricks.labs.lakebridge.transpiler.sqlglot.dialect_utils import get_dialect
from sqlglot import transpile


class TestOracleVariableDeclarations:
    """Test Oracle variable declarations transpilation to Databricks."""

    @pytest.fixture
    def dialects(self):
        """Set up Oracle and Databricks dialects."""
        return get_dialect("oracle"), get_dialect("databricks")

    @pytest.mark.parametrize(
        "oracle_code,expected",
        [
            ("p_date_start NUMBER;", "DECLARE VARIABLE p_date_start BIGINT"),
            ("v_name VARCHAR2;", "DECLARE VARIABLE v_name STRING"),
            ("v_date DATE;", "DECLARE VARIABLE v_date DATE"),
            ("v_timestamp TIMESTAMP;", "DECLARE VARIABLE v_timestamp TIMESTAMP"),
            ("v_char CHAR;", "DECLARE VARIABLE v_char STRING"),
            ("some_var VARCHAR;", "DECLARE VARIABLE some_var STRING"),
            ("counter INTEGER;", "DECLARE VARIABLE counter BIGINT"),
            ("amount DECIMAL;", "DECLARE VARIABLE amount DECIMAL"),
            ("ratio FLOAT;", "DECLARE VARIABLE ratio DOUBLE"),
            ("description CLOB;", "DECLARE VARIABLE description STRING"),
        ],
    )
    def test_oracle_variable_declarations(self, dialects, oracle_code, expected):
        """Test that Oracle variable declarations are converted to DECLARE VARIABLE statements."""
        oracle_dialect, databricks_dialect = dialects
        result = transpile(oracle_code, read=oracle_dialect, write=databricks_dialect)
        assert len(result) == 1
        assert result[0] == expected

    def test_regular_aliases_still_work(self, dialects):
        """Test that regular column aliases in SELECT statements are not affected."""
        oracle_dialect, databricks_dialect = dialects
        sql = "SELECT column_name AS alias_name FROM table1;"
        result = transpile(sql, read=oracle_dialect, write=databricks_dialect)
        assert len(result) == 1
        assert "AS alias_name" in result[0]
        assert "DECLARE VARIABLE" not in result[0]

    def test_mixed_statements(self, dialects):
        """Test that variable declarations work alongside other SQL statements."""
        oracle_dialect, databricks_dialect = dialects
        # Note: This might need to be tested as separate statements depending on parser capabilities
        statements = [
            "p_count NUMBER;",
            "SELECT COUNT(*) FROM users;",
        ]

        for stmt in statements:
            result = transpile(stmt, read=oracle_dialect, write=databricks_dialect)
            assert len(result) == 1
            if "NUMBER;" in stmt:
                assert result[0].startswith("DECLARE VARIABLE")
            else:
                assert "SELECT" in result[0]
