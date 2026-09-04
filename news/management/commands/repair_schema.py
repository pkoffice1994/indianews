from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Repair missing news app tables/columns before normal migrations run."

    def handle(self, *args, **options):
        existing_tables = set(connection.introspection.table_names())
        news_models = [
            model
            for model in apps.get_app_config("news").get_models(include_auto_created=True)
            if model._meta.managed and model._meta.db_table.startswith("news_")
        ]

        with connection.schema_editor() as schema_editor:
            for model in news_models:
                table_name = model._meta.db_table
                if table_name not in existing_tables:
                    schema_editor.create_model(model)
                    existing_tables.add(table_name)
                    self.stdout.write(self.style.WARNING(f"Created missing table: {table_name}"))
                    continue

                with connection.cursor() as cursor:
                    existing_columns = {
                        column.name
                        for column in connection.introspection.get_table_description(
                            cursor, table_name
                        )
                    }
                for field in model._meta.local_fields:
                    if field.column in existing_columns:
                        continue
                    schema_editor.add_field(model, field)
                    existing_columns.add(field.column)
                    self.stdout.write(
                        self.style.WARNING(f"Added missing column: {table_name}.{field.column}")
                    )

        self.stdout.write(self.style.SUCCESS("Schema repair check complete."))
