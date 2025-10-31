from datetime import datetime, timedelta
import sqlite3

def create_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Seller table
    c.execute('''CREATE TABLE IF NOT EXISTS seller (
        seller_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT UNIQUE,
        password TEXT,
        rating REAL DEFAULT 0,
        total_rentals INTEGER DEFAULT 0
    )''')

    # Customer table
    c.execute('''CREATE TABLE IF NOT EXISTS customer (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT UNIQUE,
        password TEXT,
        safety_deposit_balance REAL DEFAULT 0,
        platform_fee_rate REAL DEFAULT 0.04,
        active_rentals INTEGER DEFAULT 0
    )''')

    # Gear items (products)
    c.execute('''CREATE TABLE IF NOT EXISTS gear_items (
        gear_id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id INTEGER,
        gear_name TEXT,
        category TEXT,
        price_per_day REAL,
        description TEXT,
        FOREIGN KEY (seller_id) REFERENCES seller(seller_id)
    )''')

    conn.commit()
    conn.close()

# ---------- User Functions ----------
def insert_seller(db_name, name, phone, email, password):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("INSERT INTO seller (name, phone, email, password) VALUES (?, ?, ?, ?)",
              (name, phone, email, password))
    conn.commit()
    conn.close()

def insert_customer(db_name, name, phone, email, password):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("INSERT INTO customer (name, phone, email, password) VALUES (?, ?, ?, ?)",
              (name, phone, email, password))
    conn.commit()
    conn.close()

def get_seller(db_name, email):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM seller WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    return row

def get_customer(db_name, email):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM customer WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    return row

# ---------- Product Functions ----------
def insert_gear(db_name, seller_id, seller_name, gear_name, category, price_per_day, security_deposit, quantity, description):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        INSERT INTO gear_items 
        (seller_id, seller_name, gear_name, category, price_per_day, security_deposit, quantity, description, image_path, is_available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, 1)
    ''', (seller_id, seller_name, gear_name, category, price_per_day, security_deposit, quantity, description))
    conn.commit()
    conn.close()


def get_all_gear(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM gear_items")
    rows = c.fetchall()
    conn.close()
    return rows

def get_gear_by_ids(db_name, ids):
    if not ids:
        return []
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    placeholders = ','.join('?' * len(ids))
    c.execute(f"SELECT * FROM gear_items WHERE gear_id IN ({placeholders})", ids)
    rows = c.fetchall()
    conn.close()
    return rows

def get_gear_by_seller(db_name, seller_id):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM gear_items WHERE seller_id=?", (seller_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_recent_gear(db_name, limit=4):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM gear_items ORDER BY gear_id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def search_gear(db_name, query):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    like_query = f"%{query}%"
    c.execute("""
        SELECT * FROM gear_items
        WHERE (gear_name LIKE ? OR category LIKE ?) AND is_available=1
    """, (like_query, like_query))
    rows = c.fetchall()
    conn.close()
    return rows

def update_gear(db_name, gear_id, gear_name, category, price_per_day, security_deposit, quantity, description):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        UPDATE gear_items
        SET gear_name=?, category=?, price_per_day=?, security_deposit=?, quantity=?, description=?
        WHERE gear_id=?
    ''', (gear_name, category, price_per_day, security_deposit, quantity, description, gear_id))
    conn.commit()
    conn.close()


def get_gear_by_id(db_name, gear_id):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM gear_items WHERE gear_id=?", (gear_id,))
    row = c.fetchone()
    conn.close()
    return row




def insert_rental(db_name, customer_id, seller_id, gear_id, gear_name, total_cost):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    end_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")  # example: 3-day rental
    deposit_collected = int(total_cost * 0.5)
    platform_fee = round(total_cost * 0.04, 2)

    c.execute("""
        INSERT INTO rentals (
            customer_id, seller_id, gear_id, gear_name,
            start_date, end_date, total_cost, status,
            deposit_collected, platform_fee, returned_on
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_id, seller_id, gear_id, gear_name,
        start_date, end_date, total_cost, "active",
        deposit_collected, platform_fee, None
    ))

    conn.commit()
    conn.close()


def update_gear_availability(db_name, gear_id, is_available):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("UPDATE gear_items SET is_available=? WHERE gear_id=?", (1 if is_available else 0, gear_id))
    conn.commit()
    conn.close()
    
def get_rentals_by_customer(db_name, customer_id):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("""
        SELECT gear_name, start_date, end_date, total_cost,
               status, deposit_collected, platform_fee, returned_on
        FROM rentals
        WHERE customer_id=?
        ORDER BY start_date DESC
    """, (customer_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def delete_gear(db_name, gear_id):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("DELETE FROM gear_items WHERE gear_id=?", (gear_id,))
    conn.commit()
    conn.close()