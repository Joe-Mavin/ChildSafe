import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("child_registry.db")
cursor = conn.cursor()

# Check if the children table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='children'")
table_exists = cursor.fetchone()

if table_exists:
    # Check if the gender column already exists in the children table
    cursor.execute("PRAGMA table_info(children)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    if 'gender' not in column_names:
        # Alter the existing children table to add the "gender" column
        cursor.execute("""
            ALTER TABLE children
            ADD COLUMN gender TEXT
        """)
else:
    # Create a new children table with the specified properties including "gender"
    cursor.execute("""
        CREATE TABLE children (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            huduma_number TEXT UNIQUE NOT NULL,
            dob DATE NOT NULL,
            gender TEXT,
            mother_first_name TEXT NOT NULL,
            mother_last_name TEXT NOT NULL,
            father_first_name TEXT NOT NULL,
            father_last_name TEXT NOT NULL,  -- Fixed the typo here
            mother_contact TEXT NOT NULL,
            father_contact TEXT NOT NULL,
            county TEXT NOT NULL,
            sub_county TEXT NOT NULL,
            ward TEXT NOT NULL,
            picture TEXT NOT NULL
        )
    """)

# Commit the changes and close the connection
conn.commit()
conn.close()


