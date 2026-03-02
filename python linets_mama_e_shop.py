import sqlite3
from datetime import datetime

# ==============================
# DATABASE CONNECTION
# ==============================
conn = sqlite3.connect("linets_mama_e_shop.db")
cursor = conn.cursor()

# ==============================
# CREATE TABLES
# ==============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT,
    buying_price REAL NOT NULL,
    selling_price REAL NOT NULL,
    current_stock INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 5,
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    change_type TEXT,
    quantity_changed INTEGER,
    date_recorded TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_amount REAL,
    payment_method TEXT,
    sale_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sale_items (
    sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    selling_price REAL,
    total_price REAL
)
""")

conn.commit()

# ==============================
# FUNCTIONS
# ==============================

def add_product():
    name = input("Product Name: ")
    category = input("Category: ")
    buying_price = float(input("Buying Price: "))
    selling_price = float(input("Selling Price: "))

    cursor.execute("""
        INSERT INTO products (product_name, category, buying_price, selling_price, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, category, buying_price, selling_price, datetime.now()))

    conn.commit()
    print("✅ Product Added Successfully!\n")


def add_stock():
    product_id = int(input("Product ID: "))
    quantity = int(input("Quantity to Add: "))

    cursor.execute("""
        UPDATE products
        SET current_stock = current_stock + ?
        WHERE product_id = ?
    """, (quantity, product_id))

    cursor.execute("""
        INSERT INTO stock_history (product_id, change_type, quantity_changed, date_recorded)
        VALUES (?, 'STOCK_IN', ?, ?)
    """, (product_id, quantity, datetime.now()))

    conn.commit()
    print("✅ Stock Added Successfully!\n")


def make_sale():
    product_id = int(input("Product ID: "))
    quantity = int(input("Quantity Sold: "))

    cursor.execute("SELECT selling_price, current_stock FROM products WHERE product_id = ?", (product_id,))
    result = cursor.fetchone()

    if result is None:
        print("❌ Product not found!\n")
        return

    selling_price, current_stock = result

    if quantity > current_stock:
        print("❌ Not enough stock!\n")
        return

    total_price = selling_price * quantity

    cursor.execute("""
        INSERT INTO sales (total_amount, payment_method, sale_date)
        VALUES (?, ?, ?)
    """, (total_price, "Cash", datetime.now()))

    sale_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO sale_items (sale_id, product_id, quantity, selling_price, total_price)
        VALUES (?, ?, ?, ?, ?)
    """, (sale_id, product_id, quantity, selling_price, total_price))

    cursor.execute("""
        UPDATE products
        SET current_stock = current_stock - ?
        WHERE product_id = ?
    """, (quantity, product_id))

    cursor.execute("""
        INSERT INTO stock_history (product_id, change_type, quantity_changed, date_recorded)
        VALUES (?, 'SALE', ?, ?)
    """, (product_id, -quantity, datetime.now()))

    conn.commit()
    print("✅ Sale Completed Successfully!\n")


def view_products():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    print("\n📦 PRODUCTS")
    print("-" * 50)
    for p in products:
        print(f"ID: {p[0]} | {p[1]} | Stock: {p[5]} | Selling: {p[4]}")
    print()


def view_stock_history():
    cursor.execute("SELECT * FROM stock_history")
    history = cursor.fetchall()

    print("\n📊 STOCK HISTORY")
    print("-" * 50)
    for h in history:
        print(h)
    print()


# ==============================
# MAIN MENU
# ==============================

def main():
    while True:
        print("===== LINETS MAMA E SHOP =====")
        print("1. Add Product")
        print("2. Add Stock")
        print("3. Make Sale")
        print("4. View Products")
        print("5. View Stock History")
        print("6. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            add_product()
        elif choice == "2":
            add_stock()
        elif choice == "3":
            make_sale()
        elif choice == "4":
            view_products()
        elif choice == "5":
            view_stock_history()
        elif choice == "6":
            print("Goodbye 👋")
            break
        else:
            print("Invalid choice!\n")


if __name__ == "__main__":
    main()
