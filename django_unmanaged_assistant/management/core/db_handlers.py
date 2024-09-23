from django.db.backends.base.base import BaseDatabaseWrapper
from management.core.abstract import DatabaseHandler, DatabaseStatementHandler


class DataBaseCoreHandler(DatabaseHandler):

    def types_are_compatible(self, existing_type: str, expected_type: str) -> bool:
        """
        Check if two database column types are compatible.

        This method checks if the existing database column type is compatible
        with the expected type based on the model field type.

        Args:
            existing_type (str): The existing database column type.
            expected_type (str): The expected database column type.

        Returns:
            bool: True if the types are compatible, False otherwise.
        """
        existing_type = existing_type.lower() if existing_type else ""
        expected_type = expected_type.lower() if expected_type else ""

        compatible_types = {
            "int": ["int", "integer", "smallint", "bigint"],
            "varchar": ["varchar", "char", "text", "nvarchar", "nchar"],
            "float": ["float", "real", "double precision"],
            "decimal": ["decimal", "numeric"],
            "datetime": ["datetime", "timestamp", "date", "time"],
            "bool": ["bool", "boolean", "bit"],
        }

        for compatible_list in compatible_types.values():
            if existing_type in compatible_list and expected_type in compatible_list:
                return True

        return False

    def parse_table_name(
        self, connection: BaseDatabaseWrapper, table_name: str
    ) -> tuple:
        """
        Parse the table name into schema and table parts.

        Returns a tuple of (schema, table).

        If the table name is not qualified with a schema, the default schema
        for the connection is used.

        Examples:
        - [schema].[table] -> (schema, table)
        - schema.table -> (schema, table)
        - table -> (default_schema, table)

        Args:
            connection (BaseDatabaseWrapper): The database connection.
            table_name (str): the table name to parse

        Returns:
            tuple: (schema, table)
        """
        if "[" in table_name and "]" in table_name:
            parts = table_name.split(".", 1)
            schema = parts[0].strip("[]")
            table = parts[1].strip("[]")
        elif "." in table_name:
            schema, table = table_name.split(".", 1)
        else:
            schema = self.get_default_schema(connection)
            table = table_name
        schema = schema.strip('"').strip("'")
        table = table.strip('"').strip("'")
        return schema, table


class PostgreSQLHandler(DatabaseHandler):

    def __init__(self, settings: dict, *args, **kwargs) -> None: ...

    def get_default_schema(self) -> str:
        return "public"


class MSSQLHandler(DatabaseHandler):

    def __init__(self, settings: dict, *args, **kwargs) -> None: ...

    def get_default_schema(self) -> str:
        return "dbo"


class SQLiteHandler(DatabaseHandler):

    def __init__(self, settings: dict, *args, **kwargs) -> None: ...

    def get_default_schema(self) -> str:
        return "main"


# class MySQLHandler(DatabaseHandler):

#     def __init__(self, settings: dict, *args, **kwargs) -> None: ...

#     def get_default_schema(self):
#         return 'public'
