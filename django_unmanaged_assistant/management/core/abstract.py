from abc import ABC, abstractmethod
from django.db.backends.base.base import BaseDatabaseWrapper


class DatabaseStatementHandler(ABC):
    """Abstract class for database statement handlers."""

    @abstractmethod
    def open_conn(self, *args, **kwargs): ...

    @abstractmethod
    def close_conn(self, *args, **kwargs): ...

    @abstractmethod
    def open_cursor(self, *args, **kwargs): ...

    @abstractmethod
    def close_cursor(self, *args, **kwargs): ...

    @abstractmethod
    def execute_query(self, query, *args, **kwargs): ...

    @abstractmethod
    def execute_query_with_params(self, query, params, *args, **kwargs): ...

    @abstractmethod
    def execute_query_with_named_params(self, query, params, *args, **kwargs): ...


class DatabaseHandler(ABC):
    """Abstract class for database handlers."""

    @abstractmethod
    def __init__(self, settings: dict, *args, **kwargs): ...

    @abstractmethod
    def get_default_schema(self): ...

    @abstractmethod
    def create_schema_if_not_exists(self, schema: str): ...

    @abstractmethod
    def table_exists(self, schema: str, table: str): ...

    @abstractmethod
    def column_exists(self, schema: str, table: str, column_name: str): ...

    @abstractmethod
    def get_field_db_type(self, field): ...

    @abstractmethod
    def process_field(self, model, schema, table, field): ...

    @abstractmethod
    def get_column_type(
        connection: BaseDatabaseWrapper,
        schema: str,
        table: str,
        column_name: str,
    ) -> str | None: ...

    @abstractmethod
    def get_formatted_table_name(
        connection: BaseDatabaseWrapper, schema: str, table: str
    ) -> str: ...
