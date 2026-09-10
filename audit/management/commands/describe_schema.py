"""Print the tables of this project and the rules the database enforces on them.

    python manage.py describe_schema

Read from the running database rather than from the models, on purpose. The
models say what the schema is meant to be; only the database says what it is.
Two constraints once sat in the models and not in the database for long enough
that nobody knew, and a report built from the models would have printed them
anyway.

It sits beside `verify_integrity` because both answer the same kind of question
— what is true of this database right now — and someone looking for either
looks in the same place.

Which tables to describe comes from the application registry, so the tables
Django keeps for itself stay out and the ones this project designed stay in.
"""

import re

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection

#: The apps whose tables this project designed. Django's own tables exist to
#: make the framework work and say nothing about the domain.
OUR_APPS = ["accounts", "companies", "products", "verification", "audit"]

#: Marks a constraint name Django built rather than one this project chose.
#: Django hashes part of the columns into the name, which is what the eight hex
#: characters are, and ends the plain ones in a fixed suffix.
GENERATED_NAME = re.compile(r"_[0-9a-f]{8}(_|$)|_(pkey|key|uniq|check)$")

#: What each constraint letter means in `pg_constraint.contype`, in the order
#: the report shows them: identity first, then the rules, then the links.
CONSTRAINT_KINDS = [
    ("p", "primary key"),
    ("u", "unique"),
    ("c", "check"),
    ("f", "foreign key"),
]


class Command(BaseCommand):
    help = "Describe every table of this project and the rules the database enforces on it."

    def handle(self, *args, **options):
        tables = self._our_tables()

        self.stdout.write(self.style.MIGRATE_HEADING("OriginPass — what the database enforces"))
        self.stdout.write(
            f"{self._server_version()} · {len(tables)} tables · "
            "read from the running database, not from the models"
        )

        columns = self._columns(tables)
        constraints = self._constraints(tables)
        indexes = self._indexes(tables)

        for table in tables:
            self.stdout.write("")
            self.stdout.write(self.style.MIGRATE_LABEL(table))
            self._write_columns(columns.get(table, []))
            self._write_constraints(constraints.get(table, {}))
            self._write_indexes(indexes.get(table, []))

        self.stdout.write("")
        self.stdout.write(
            f"{sum(len(k.get('c', [])) for k in constraints.values())} check constraints and "
            f"{sum(len(k.get('u', [])) for k in constraints.values())} unique constraints are "
            "rules the application cannot go around, because they are held by the database "
            "rather than by the code that writes to it."
        )

    # ---- what to describe ----

    def _our_tables(self):
        """The tables of this project, in the order the apps are listed."""
        return [
            model._meta.db_table
            for app_label in OUR_APPS
            for model in apps.get_app_config(app_label).get_models()
        ]

    def _server_version(self):
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version")
            return f"PostgreSQL {cursor.fetchone()[0]}"

    # ---- what the database says ----

    def _columns(self, tables):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name, column_name, data_type, character_maximum_length,
                       is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = ANY(%s)
                ORDER BY table_name, ordinal_position
                """,
                [tables],
            )
            rows = cursor.fetchall()

        by_table = {}
        for table, name, data_type, length, nullable, default in rows:
            by_table.setdefault(table, []).append(
                {
                    "name": name,
                    "type": f"{data_type}({length})" if length else data_type,
                    "nullable": nullable == "YES",
                    "generated": bool(default and "nextval" in default),
                }
            )
        return by_table

    def _constraints(self, tables):
        """Grouped by table and by kind, with the definition Postgres renders itself."""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT conrelid::regclass::text, contype, conname, pg_get_constraintdef(oid)
                FROM pg_constraint
                WHERE connamespace = 'public'::regnamespace
                  AND conrelid::regclass::text = ANY(%s)
                ORDER BY conrelid::regclass::text, conname
                """,
                [tables],
            )
            rows = cursor.fetchall()

        by_table = {}
        for table, kind, name, definition in rows:
            by_table.setdefault(table, {}).setdefault(kind, []).append((name, definition))
        return by_table

    def _indexes(self, tables):
        """Only the ones no constraint already created, so nothing is listed twice."""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT i.tablename, i.indexname, i.indexdef
                FROM pg_indexes i
                WHERE i.schemaname = 'public'
                  AND i.tablename = ANY(%s)
                  AND NOT EXISTS (
                      SELECT 1 FROM pg_constraint c
                      WHERE c.conname = i.indexname
                        AND c.connamespace = 'public'::regnamespace
                  )
                ORDER BY i.tablename, i.indexname
                """,
                [tables],
            )
            rows = cursor.fetchall()

        by_table = {}
        for table, name, definition in rows:
            by_table.setdefault(table, []).append((name, definition))
        return by_table

    # ---- how to show it ----

    def _write_columns(self, columns):
        if not columns:
            return
        width = max(len(column["name"]) for column in columns)
        for column in columns:
            notes = []
            if column["nullable"]:
                notes.append("null")
            if column["generated"]:
                notes.append("generated")
            trailer = f"  {', '.join(notes)}" if notes else ""
            self.stdout.write(f"    {column['name']:<{width}}  {column['type']}{trailer}")

    def _write_constraints(self, by_kind):
        """The rule in words first, then the definition that proves it.

        Postgres renders a check with every cast it inserted, which is faithful
        and close to unreadable. The constraint's own name is the sentence the
        rule was written to be, so it leads, and the rendered definition
        follows indented as the evidence for it.
        """
        for kind, label in CONSTRAINT_KINDS:
            for name, definition in by_kind.get(kind, []):
                self.stdout.write(f"    {label:<12} {self._as_words(name, definition)}")
                if kind == "c":
                    self.stdout.write(f"    {'':<12}   {definition}")

    def _as_words(self, name, definition):
        """What this constraint is for, taken from its name when we chose the name.

        A name we chose is a sentence about the domain and says more than the
        definition ever will. A name Django generated says less, so the
        definition speaks instead.
        """
        if GENERATED_NAME.search(name):
            return self._plainly(definition)
        return name.replace("_", " ")

    def _plainly(self, definition):
        """Drop the parts of a generated definition that carry no meaning here.

        Kept to plain ASCII: this prints to whatever console the machine has,
        and the Windows default cannot encode an arrow.
        """
        return (
            definition.replace("PRIMARY KEY ", "")
            .replace("UNIQUE ", "")
            .replace("FOREIGN KEY ", "")
            .replace(" DEFERRABLE INITIALLY DEFERRED", "")
            .replace(") REFERENCES ", ") -> ")
        )

    def _write_indexes(self, indexes):
        for name, definition in indexes:
            using = definition.split(" USING ", 1)[-1]
            self.stdout.write(f"    {'index':<12} {using}  named {name}")
