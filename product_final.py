# product_master.py

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ------------------ Initialize Product DB ------------------
def init_product_db():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

# ------------------ Save Product ------------------
def save_product(name, category, price, stock, desc, entry_fields):
    if not name or not price.replace('.', '', 1).isdigit() or not stock.isdigit():
        messagebox.showerror("Input Error", "Please enter valid name, price, and stock quantity.")
        return

    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, price, stock, description)
        VALUES (?, ?, ?, ?, ?)
    """, (name, category, float(price), int(stock), desc))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Product '{name}' added successfully.")
    for e in entry_fields:
        e.delete(0, tk.END)
    load_products()

# ------------------ Load All Products ------------------
def load_products():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()

# ------------------ Main Product Master Window ------------------
def open_product_master():
    win = tk.Tk()
    win.title("Product Master - Smart Store")
    win.geometry("800x600")
    win.configure(bg="lightblue")

    tk.Label(win, text="Product Master", font=("Arial", 16, "bold"), bg="lightblue").pack(pady=10)

    frame = tk.Frame(win, bg="lightblue")
    frame.pack(pady=10)

    labels = ["Product Name", "Category", "Price", "Stock Qty", "Description"]
    entries = []

    for i, lbl in enumerate(labels):
        tk.Label(frame, text=lbl + ":", font=("Arial", 10), bg="lightblue").grid(row=i, column=0, sticky="e", padx=5, pady=5)
        ent = tk.Entry(frame, width=30)
        ent.grid(row=i, column=1, padx=5, pady=5)
        entries.append(ent)

    def submit_product():
        name = entries[0].get().strip()
        category = entries[1].get().strip()
        price = entries[2].get().strip()
        stock = entries[3].get().strip()
        desc = entries[4].get().strip()
        save_product(name, category, price, stock, desc, entries)

    tk.Button(frame, text="Save Product", command=submit_product, bg="green", fg="white", font=("Arial", 10)).grid(row=5, column=1, pady=10)

    # Treeview for product display
    global tree
    tree = ttk.Treeview(win, columns=("ID", "Name", "Category", "Price", "Stock", "Description"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=100 if col != "Description" else 200)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    init_product_db()
    load_products()
    win.mainloop()

# Run the window
if __name__ == "__main__":
    open_product_master()
