#  Main_new.py final version 
#    |
#   orders.db
#   products.db
#     |
#   product_final.py
#   invoices\invoice_1.txt
# https://chatgpt.com/c/684ebd9d-4a20-8006-b589-b3893831b24a


import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

# ------------------ Database Setup ------------------

def init_order_db():
    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            product_name TEXT,
            qty INTEGER,
            price REAL,
            total REAL,
            received REAL,
            due REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()


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


# ------------------ Load Product Data ------------------

def load_products():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return {name: price for name, price in rows}


# ------------------ Place New Order ------------------

def open_order_form():
    order_win = tk.Toplevel(root)
    order_win.title("Place New Order")
    order_win.geometry("400x400")
    order_win.configure(bg="lightgreen")

    tk.Label(order_win, text="Place New Order", font=("Arial", 14, "bold"), bg="lightgreen").pack(pady=10)

    frame = tk.Frame(order_win, bg="lightgreen")
    frame.pack(pady=10)

    tk.Label(frame, text="Customer Name:", bg="lightgreen").grid(row=0, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(frame, width=30)
    entry_name.grid(row=0, column=1, pady=5)

    product_dict = load_products()
    tk.Label(frame, text="Product:", bg="lightgreen").grid(row=1, column=0, sticky="e", pady=5)
    combo_product = ttk.Combobox(frame, values=list(product_dict.keys()), width=27)
    combo_product.grid(row=1, column=1, pady=5)

    tk.Label(frame, text="Quantity:", bg="lightgreen").grid(row=2, column=0, sticky="e", pady=5)
    entry_qty = tk.Entry(frame, width=30)
    entry_qty.grid(row=2, column=1, pady=5)

    tk.Label(frame, text="Price (₹):", bg="lightgreen").grid(row=3, column=0, sticky="e", pady=5)
    entry_price = tk.Entry(frame, width=30)
    entry_price.grid(row=3, column=1, pady=5)

    tk.Label(frame, text="Received (₹):", bg="lightgreen").grid(row=4, column=0, sticky="e", pady=5)
    entry_received = tk.Entry(frame, width=30)
    entry_received.grid(row=4, column=1, pady=5)

    def submit_order():
        name = entry_name.get().strip()
        product = combo_product.get()
        qty = entry_qty.get()
        price = entry_price.get()
        received = entry_received.get()

        if not (name and product and qty.isdigit() and price.replace('.', '', 1).isdigit() and received.replace('.', '', 1).isdigit()):
            messagebox.showerror("Error", "Please fill all fields with valid data.")
            return

        qty = int(qty)
        price = float(price)
        received = float(received)
        total = qty * price
        due = total - received
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check stock
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        cursor.execute("SELECT stock FROM products WHERE name=?", (product,))
        row = cursor.fetchone()
        if row:
            stock = row[0]
            if stock == 0:
                messagebox.showerror("Out of Stock", f"Stock is 0 for {product}. Cannot proceed.")
                return
            elif qty > stock:
                messagebox.showerror("Low Stock", f"Only {stock} items available. Reduce quantity.")
                return
            else:
                # Reduce stock
                new_stock = stock - qty
                cursor.execute("UPDATE products SET stock=? WHERE name=?", (new_stock, product))
        else:
            messagebox.showerror("Error", "Product not found in stock database.")
            return
        conn.commit()
        conn.close()

        # Save to orders DB
        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (customer_name, product_name, qty, price, total, received, due, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, product, qty, price, total, received, due, date))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Order placed successfully!")
        order_win.destroy()

    tk.Button(order_win, text="Submit Order", command=submit_order, bg="darkgreen", fg="white").pack(pady=20)


# ------------------ View Orders ------------------

def view_orders():
    view_win = tk.Toplevel(root)
    view_win.title("Received Orders")
    view_win.geometry("800x400")
    tree = ttk.Treeview(view_win, columns=("ID", "Customer", "Product", "Qty", "Price", "Total", "Received", "Due", "Date"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=90)
    tree.pack(fill="both", expand=True)
    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    for row in c.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()


# ------------------ Search Order By ID + Print Invoice ------------------

def search_order_by_id():
    search_win = tk.Toplevel(root)
    search_win.title("Search Order by ID")
    search_win.geometry("400x350")
    search_win.configure(bg="lightyellow")

    tk.Label(search_win, text="Enter Order ID:", font=("Arial", 12), bg="lightyellow").pack(pady=10)
    entry_id = tk.Entry(search_win, width=30)
    entry_id.pack(pady=5)

    result_label = tk.Label(search_win, text="", bg="lightyellow", font=("Arial", 11))
    result_label.pack(pady=10)

    def print_invoice(order):
        folder_path = "invoices"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, f"invoice_{order[0]}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Smart Store - Invoice\n")
            f.write("========================\n")
            f.write(f"Order ID: {order[0]}\n")
            f.write(f"Customer Name: {order[1]}\n")
            f.write(f"Product: {order[2]}\n")
            f.write(f"Quantity: {order[3]}\n")
            f.write(f"Unit Price: ₹{order[4]:.2f}\n")
            f.write(f"Total: ₹{order[5]:.2f}\n")
            f.write(f"Received: ₹{order[6]:.2f}\n")
            f.write(f"Due: ₹{order[7]:.2f}\n")
            f.write(f"Date: {order[8]}\n")
            f.write("========================\n")
        messagebox.showinfo("Saved", f"Invoice saved at:\n{file_path}")

    def search():
        order_id = entry_id.get().strip()
        if not order_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid numeric Order ID.")
            return

        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (int(order_id),))
        order = cursor.fetchone()
        conn.close()

        if order:
            info = f"""
Order ID: {order[0]}
Customer: {order[1]}
Product: {order[2]}
Qty: {order[3]}
Unit Price: ₹{order[4]:.2f}
Total: ₹{order[5]:.2f}
Received: ₹{order[6]:.2f}
Due: ₹{order[7]:.2f}
Date: {order[8]}
"""
            result_label.config(text=info.strip(), justify="left", fg="darkgreen")
            tk.Button(search_win, text="🖨️ Print Invoice", command=lambda: print_invoice(order), bg="darkgreen", fg="white").pack(pady=5)
        else:
            result_label.config(text="Order not found!", fg="red")

    tk.Button(search_win, text="Search", command=search, bg="blue", fg="white").pack(pady=10)


# ------------------ Daily Sales Summary ------------------

def view_sales_summary():
    win = tk.Toplevel(root)
    win.title("Sales Summary")
    win.geometry("420x300")
    win.configure(bg="lightblue")

    tk.Label(win, text="Daily Sales Summary", font=("Arial", 13, "bold"), bg="lightblue").pack(pady=10)

    tree = ttk.Treeview(win, columns=("Date", "Total", "Received", "Due"), show="headings", height=10)
    tree.heading("Date", text="Date")
    tree.heading("Total", text="Total (₹)")
    tree.heading("Received", text="Received (₹)")
    tree.heading("Due", text="Due (₹)")

    tree.column("Date", width=100)
    tree.column("Total", width=90, anchor="e")
    tree.column("Received", width=100, anchor="e")
    tree.column("Due", width=90, anchor="e")

    tree.pack(fill="both", expand=True, padx=10, pady=5)

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date(date), 
               SUM(total), 
               SUM(received),
               SUM(due)
        FROM orders
        GROUP BY date(date)
        ORDER BY date(date) DESC
    """)
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()


# ------------------ Main GUI ------------------

root = tk.Tk()
root.title("Order Management System")
root.geometry("400x500")
root.configure(bg="orange")

init_order_db()
init_product_db()

tk.Label(root, text="Developed By Sybertech", bg="darkblue", fg="white", font=("Arial", 12, "bold")).pack(fill="x")
tk.Label(root, text="Online Order Manager", font=("Arial", 18, "bold"), bg="orange").pack(pady=20)

tk.Button(root, text="🟢 Place New Order", command=open_order_form, width=25, bg="green", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="📋 View Received Orders", command=view_orders, width=25, bg="blue", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="🔍 Search by Order ID", command=search_order_by_id, width=25, bg="purple", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="📊 Daily Sales Summary", command=view_sales_summary, width=25, bg="darkorange", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="📊 Exit", command=exit, width=25, bg="red", fg="white", font=("Arial", 12)).pack(pady=5)

tk.Label(root, text="Welcome to my store: Smart Store", bd=1, relief=tk.SUNKEN, anchor='w', bg="gray", fg="white", font=("Arial", 10)).pack(side="bottom", fill="x")

root.mainloop()
