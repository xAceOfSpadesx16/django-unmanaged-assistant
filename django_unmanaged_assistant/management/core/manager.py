from __future__ import annotations
from typing import TYPE_CHECKING, Generator

from contextlib import ExitStack, contextmanager
from django.apps import AppConfig
from django.conf import settings, LazySettings
from django.db import connections, models
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.models import Field, Model
from django.db.utils import ProgrammingError
from dataclasses import dataclass
from management.core.db_handlers import (
    PostgreSQLHandler,
    MySQLHandler,
    SQLiteHandler,
    MSSQLHandler,
)


if TYPE_CHECKING:
    from management.core.abstract import DatabaseHandler
    from django.apps.registry import (
        Apps,
    )  # apps type class - from django.apps import apps


class ModelData:
    model: type[Model]
    database_settings: dict
    django_database: str

    def __init__(
        self, model: Model, database_settings: dict, django_database: str
    ) -> None:
        self.model = model
        self.database_settings = database_settings
        self.django_database = django_database

    @property
    def app_label(self) -> str:
        return self.model._meta.app_label

    @property
    def table_name(self) -> str:
        return self.model._meta.db_table


class DatabaseManager:
    """Class for database managers."""

    def __init__(self, settings: LazySettings) -> None:
        self.settings = settings
        self.handlers = {}

    def model_dispatcher(
        self, model: type[Model], settings: LazySettings
    ) -> DatabaseHandler:
        """
        TODO: refactor this to dispatch ModelData
        append ModelData to especific handler and append it to self.handlers dict
        based on the APP_TO_DATABASE_MAPPING defined in settings and model._meta.app_label
        """

        # TODO: Add support for dbrouters if they exist?

        model_app = model._meta.app_label

    def is_app_eligible(self, app_config: AppConfig) -> bool:
        """
        Check if the app is eligible for processing.

        Args:
            app_config (AppConfig): The Django app configuration.

        Returns:
            bool: True if the app is eligible for processing, False otherwise.
        """
        app_name = app_config.name.split(".")[-1]
        exclude_path = getattr(self.settings, "EXCLUDE_UNMANAGED_PATH", "site-packages")
        is_local_app = exclude_path not in app_config.path
        is_additional_app = app_name in getattr(
            settings, "ADDITIONAL_UNMANAGED_TABLE_APPS", []
        )
        return is_local_app or is_additional_app

    def collect_unmanaged_models(self, app_config: AppConfig) -> None:
        """
        Collect unmanaged models from the given app configuration.

        Args:
            app_config (AppConfig): The Django app configuration.

        Returns:
            None
        """
        for model in app_config.get_models():
            if not model._meta.managed:
                app_database = self.settings.APP_TO_DATABASE_MAPPING.get(
                    app_config.label
                )
                setting_database = self.settings.DATABASES.get(app_database)
                ModelData(model, setting_database, app_database)

    def process_models(self) -> None:
        """
        Process the unmanaged models.

        This method groups the models by database connection and processes
        each model for each connection.

        Returns:
            None
        """
        models_by_connection = {}
        for model in self.models_to_process:
            # Get the default database
            db_alias = "default"
            # TODO: Add support for dbrouters if they exist?
            if settings.APP_TO_DATABASE_MAPPING:
                db_name = settings.APP_TO_DATABASE_MAPPING.get(model._meta.app_label)
                if db_name:
                    db_alias = db_name
            connection = connections[db_alias]
            if connection not in models_by_connection:
                models_by_connection[connection] = []
            models_by_connection[connection].append(model)

        # Process models for each connection
        for connection, models in models_by_connection.items():
            self.connection = connection
            with connection.schema_editor() as schema_editor:
                with ExitStack() as stack:
                    # Apply temporary table names to all models
                    for model in models:
                        stack.enter_context(
                            self.temporary_table_name(model, connection)
                        )

                    # Now process each model
                    for model in models:
                        self.create_table_for_model(connection, schema_editor, model)

    @contextmanager
    def temporary_table_name(
        self, model: type[Model], connection: BaseDatabaseWrapper
    ) -> Generator[str, None, None]:
        """
        Context manager to temporarily change the db_table name of a model.

        Args:
            model (type[Model]): The Django model class.
            connection (BaseDatabaseWrapper): The database connection.

        Yields:
            str: The formatted table name for the model.
        """
        original_db_table = model._meta.db_table
        if not connection.vendor == "sqlite":
            schema, table = self.handler.parse_table_name(
                connection, original_db_table
            )  # viene del handler
            formatted_table_name = self.handler.get_formatted_table_name(
                connection, schema, table
            )  # viene del handler
            model._meta.db_table = formatted_table_name
        try:
            yield
        finally:
            model._meta.db_table = original_db_table
