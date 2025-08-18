#!/usr/bin/env python3

"""Test script to verify Oracle variable declaration transpilation."""

import sys

sys.path.insert(0, 'src')

from sqlglot import transpile
from databricks.labs.lakebridge.transpiler.sqlglot.dialect_utils import get_dialect


def test_current_behavior():
    """Test current transpilation behavior."""
    test_cases = [
        ("p_date_start NUMBER;", "DECLARE VARIABLE p_date_start BIGINT"),
        ("v_name VARCHAR2;", "DECLARE VARIABLE v_name STRING"),
        ("v_date DATE;", "DECLARE VARIABLE v_date DATE"),
        ("v_timestamp TIMESTAMP;", "DECLARE VARIABLE v_timestamp TIMESTAMP"),
        ("v_char CHAR;", "DECLARE VARIABLE v_char STRING"),
    ]

    oracle_dialect = get_dialect("oracle")
    databricks_dialect = get_dialect("databricks")

    for oracle_code, expected in test_cases:
        print(f"\nOriginal Oracle code: {oracle_code}")
        print(f"Expected Databricks output: {expected}")

        try:
            # Test transpilation using local dialects
            result = transpile(oracle_code, read=oracle_dialect, write=databricks_dialect)
            print(f"Actual Databricks output: {result}")

            if result and result[0] == expected:
                print("✅ PASSED")
            else:
                print("❌ FAILED")
        except Exception as e:
            print(f"❌ ERROR: {e}")

    # Test to make sure regular aliases still work
    print("\n--- Testing regular aliases ---")
    regular_alias = "SELECT column_name AS alias_name FROM table1;"
    try:
        result = transpile(regular_alias, read=oracle_dialect, write=databricks_dialect)
        print(f"Regular alias: {regular_alias}")
        print(f"Output: {result}")
        if "AS alias_name" in result[0]:
            print("✅ Regular aliases still work")
        else:
            print("❌ Regular aliases broken")
    except Exception as e:
        print(f"❌ ERROR with regular alias: {e}")


if __name__ == "__main__":
    test_current_behavior()
