from databricks.labs.lakebridge.reconcile.connectors.models import NormalizedIdentifier


class DialectUtils:
    _ANSI_IDENTIFIER_DELIMITER = "`"

    @staticmethod
    def normalize_identifier(
        identifier: str, source_start_delimiter: str, source_end_delimiter: str
    ) -> NormalizedIdentifier:
        identifier = identifier.strip().lower()

        ansi = DialectUtils._normalize_identifier_source_agnostic(
            identifier,
            source_start_delimiter,
            source_end_delimiter,
            DialectUtils._ANSI_IDENTIFIER_DELIMITER,
            DialectUtils._ANSI_IDENTIFIER_DELIMITER,
        )

        if ansi == identifier:
            source = DialectUtils._normalize_identifier_source_agnostic(
                identifier,
                DialectUtils._ANSI_IDENTIFIER_DELIMITER,
                DialectUtils._ANSI_IDENTIFIER_DELIMITER,
                source_start_delimiter,
                source_end_delimiter,
            )
        else:
            source = DialectUtils._normalize_identifier_source_agnostic(
                identifier, source_start_delimiter, source_end_delimiter, source_start_delimiter, source_end_delimiter
            )

        return NormalizedIdentifier(ansi, source)

    @staticmethod
    def _normalize_identifier_source_agnostic(
        identifier: str,
        source_start_delimiter: str,
        source_end_delimiter: str,
        expected_source_start_delimiter: str,
        expected_source_end_delimiter: str,
    ) -> str:
        if identifier == "" or identifier is None:
            return ""

        if DialectUtils._is_already_delimited(
            identifier, expected_source_start_delimiter, expected_source_end_delimiter
        ):
            return identifier

        if DialectUtils._is_already_delimited(identifier, source_start_delimiter, source_end_delimiter):
            stripped_identifier = identifier.removeprefix(source_start_delimiter).removesuffix(source_end_delimiter)
        else:
            stripped_identifier = identifier
        return f"{expected_source_start_delimiter}{stripped_identifier}{expected_source_end_delimiter}"

    @staticmethod
    def _is_already_delimited(identifier: str, start_delimiter: str, end_delimiter: str) -> bool:
        return identifier.startswith(start_delimiter) and identifier.endswith(end_delimiter)
