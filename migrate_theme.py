import sqlite3
from pathlib import Path

database_path = Path(__file__).resolve().parent / "instance" / "anchor.db"

if not database_path.exists():
    raise FileNotFoundError(
        f"Database not found at: {database_path}"
    )

connection = sqlite3.connect(database_path)

try:
    columns = connection.execute(
        "PRAGMA table_info(user)"
    ).fetchall()

    if not columns:
        raise RuntimeError(
            "The user table was not found. Check the database path."
        )

    column_names = [column[1] for column in columns]

    if "theme" not in column_names:
        connection.execute(
            "ALTER TABLE user ADD COLUMN theme "
            "VARCHAR(30) NOT NULL DEFAULT 'anchor_classic'"
        )
        print("Added the theme column.")
    else:
        print("The theme column already exists.")

    if "doodle_style" not in column_names:
        connection.execute(
            "ALTER TABLE user ADD COLUMN doodle_style "
            "VARCHAR(20) NOT NULL DEFAULT 'off'"
        )
        print("Added the doodle_style column.")
    else:
        print("The doodle_style column already exists.")

    connection.commit()
    print("Database migration completed successfully.")

finally:
    connection.close()