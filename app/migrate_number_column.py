"""
Safe SQLite migration to alter `order_numbers.number` to nullable and non-unique

Run from the repo root with the project's Python environment:

    python app/migrate_number_column.py

This script rebuilds the `order_numbers` table into a new table with the desired
schema, copies existing data, then replaces the old table — preserving all rows.
"""
from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        print("Inspecting current `order_numbers` schema:")
        info = conn.execute(text("PRAGMA table_info(order_numbers);")).fetchall()
        for row in info:
            print(row)

        try:
            conn.execute(text("PRAGMA foreign_keys=off;"))
            conn.execute(text("BEGIN TRANSACTION;"))

            conn.execute(text(
                """
                CREATE TABLE order_numbers_new (
                    id INTEGER PRIMARY KEY,
                    number TEXT,
                    retoure INTEGER DEFAULT 0,
                    creation_date DATETIME
                );
                """
            ))

            conn.execute(text(
                """
                INSERT INTO order_numbers_new (id, number, creation_date)
                SELECT id, number, creation_date FROM order_numbers;
                """
            ))

            conn.execute(text("DROP TABLE order_numbers;"))
            conn.execute(text("ALTER TABLE order_numbers_new RENAME TO order_numbers;"))

            conn.execute(text("COMMIT;"))
            print("Migration completed successfully.")
        except Exception as exc:
            conn.execute(text("ROLLBACK;"))
            print("Migration failed, rolled back. Error:", exc)
        finally:
            conn.execute(text("PRAGMA foreign_keys=on;"))

if __name__ == '__main__':
    migrate()
