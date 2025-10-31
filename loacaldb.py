import sqlite3


def change_column_name(db_name, table_name, old_column_name, new_column_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name}")
    conn.commit()
    conn.close()

def show_table_rows(db_name, table_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    for row in rows:
        print(row)
    conn.close()
    
def add_column_to_table(db_name, table_name, column_name, data_type):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type}")
    conn.commit()
    conn.close()
    
add_column_to_table("main.db", "rentals", "gear_name", "TEXT")

# show_table_rows("main.db", "seller")
