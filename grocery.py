import sqlite3
import os
import sys
from datetime import datetime 
import tkinter as tk
from tkinter import messagebox

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "grocery_store.db")

products = []
sales = []

def create_database(): 
    conn = sqlite3.connect(DB_PATH) 
 
    cursor = conn.cursor() 
 
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS products ( 
            id TEXT PRIMARY KEY, 
            name TEXT, 
            category TEXT, 
            price REAL, 
            quantity INTEGER 
        ) 
    """) 

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY,
        date TEXT,
        total REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id TEXT,
            product_name TEXT,
            quantity INTEGER,
            price REAL,
            subtotal REAL
        )
    """)

    conn.commit() 
    conn.close()

def get_positive_float(message):
    while True:
        try:
            value = float(input(message))

            if value <= 0:
                print("Value must be greater than 0.")
                continue

            return value

        except ValueError:
            print("Please enter a valid number.")


def get_non_negative_int(message):
    while True:
        try:
            value = int(input(message))

            if value < 0:
                print("Value cannot be negative.")
                continue

            return value

        except ValueError:
            print("Please enter a whole number.")


def add_product():
    print("\n--Add Product--")

    product_id = input("Enter product ID: ")
    name = input("Enter product name: ")
    category = input("Enter categotry: ")
    price = get_positive_float("Enter price: ")
    quantity = get_non_negative_int("Enter quantity: ")

    product = {
        "id": product_id,
        "name": name,
        "category": category,
        "price": price,
        "quantity": quantity
    }

    products.append(product)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (id, name, category, price, quantity)
        VALUES (?, ?, ?, ?, ?)
    """, (
        product["id"],
        product["name"],
        product["category"],
        product["price"],
        product["quantity"]
    ))

    conn.commit()
    conn.close()

    print("Prodcut added successfully!")


def view_products():
    print("\n---View Product---")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products_from_db = cursor.fetchall()

    conn.close()

    if len(products_from_db) == 0:
        print("No products found.")
        return

    for product in products_from_db:
        print(
            f"ID: {product[0]} | "
            f"Name: {product[1]} | "
            f"Category: {product[2]} | "
            f"Price: Rs.{product[3]} | "
            f"Quantity: {product[4]}"
        )

def search_product():
    print("\n--- Search Product ---")

    product_id = input("Enter product ID: ")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    conn.close()

    if product is None:
        print("Product not found.")
        return

    print(f"ID: {product[0]}")
    print(f"Name: {product[1]}")
    print(f"Category: {product[2]}")
    print(f"Price: Rs.{product[3]}")
    print(f"Quantity: {product[4]}")

def update_product():
    print("\n--- Update Product ---")

    product_id = input("Enter product ID: ")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Find the product
    cursor.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        print("Product not found.")
        conn.close()
        return

    print(f"Current name: {product[1]}")
    print(f"Current category: {product[2]}")
    print(f"Current price: {product[3]}")
    print(f"Current quantity: {product[4]}")

    name = input("Enter new name: ")
    category = input("Enter new category: ")
    price = float(input("Enter new price: "))
    quantity = int(input("Enter new quantity: "))

    cursor.execute("""
        UPDATE products
        SET name = ?, category = ?, price = ?, quantity = ?
        WHERE id = ?
    """, (
        name,
        category,
        price,
        quantity,
        product_id
    ))

    conn.commit()
    conn.close()

    print("Product updated successfully!")

def delete_product():
    print("\n--- Delete Product ---")

    product_id = input("Enter product ID: ")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        print("Product not found.")
        conn.close()
        return

    print(f"Product found: {product[1]}")

    confirm = input("Are you sure you want to delete this product? (yes/no): ")

    if confirm.lower() == "yes":
        cursor.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )

        conn.commit()
        print("Product deleted successfully!")

    else:
        print("Deletion cancelled.")

    conn.close()

def create_bill():
    print("\n--- Create Bill ---")

    cart = []
    total = 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    while True:
        product_id = input("Enter product ID (or 'done' to finish): ")

        if product_id.lower() == "done":
            break

        # Find product in database
        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )

        product = cursor.fetchone()

        if product is None:
            print("Product not found.")
            continue

        print(f"Product: {product[1]}")
        print(f"Price: Rs.{product[3]}")
        print(f"Available stock: {product[4]}")

        quantity = int(input("Enter quantity: "))

        if quantity <= 0:
            print("Quantity must be greater than 0.")
            continue

        if quantity > product[4]:
            print("Not enough stock available.")
            continue

        subtotal = product[3] * quantity

        cart_item = {
            "product_id": product[0],
            "name": product[1],
            "price": product[3],
            "quantity": quantity,
            "subtotal": subtotal
            }

        cart.append(cart_item)

        # Reduce stock in database
        new_quantity = product[4] - quantity

        cursor.execute(
            "UPDATE products SET quantity = ? WHERE id = ?",
            (new_quantity, product_id)
        )

        total += subtotal

        print(f"{product[1]} added to bill.")
        print(f"Subtotal: Rs. {subtotal}")

    if len(cart) == 0:
        print("No items purchased.")
        conn.close()
        return

    conn.commit()
    conn.close()

    print("\n==============================")
    print("         GROCERY BILL")
    print("==============================")

    for item in cart:
        print(
            f"{item['name']} - "
            f"{item['quantity']} x Rs.{item['price']} "
            f"= Rs.{item['subtotal']}"
        )

    print("------------------------------")
    print(f"Total: Rs. {total}")
    print("==============================")
    print("Thank you for shopping!")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT MAX(sale_id) FROM sales"
        )
        
    last_sale_id = cursor.fetchone()[0]
    
    if last_sale_id is None:
        sale_id = 1

    else:
        sale_id = last_sale_id + 1
        
    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
    INSERT INTO sales (sale_id, date, total)
    VALUES (?, ?, ?)
    """, (
        sale_id,
        sale_date,
        total
        ))
        
    for item in cart:
        cursor.execute("""
        INSERT INTO sale_items
        (sale_id, product_id, product_name, quantity, price, subtotal)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            sale_id,
            item["product_id"],
            item["name"],
            item["quantity"],
            item["price"],
            item["subtotal"]
            ))
    conn.commit()
    conn.close()
    
    print("Sale recorded successfully!")

def restock_product():
    print("\n--- Restock Product ---")

    product_id = input("Enter product ID: ")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT quantity FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        print("Product not found.")
        conn.close()
        return

    print(f"Current stock: {product[0]}")

    quantity = int(input("Enter quantity to add: "))

    if quantity <= 0:
        print("Quantity must be greater than 0.")
        conn.close()
        return

    new_quantity = product[0] + quantity

    cursor.execute(
        "UPDATE products SET quantity = ? WHERE id = ?",
        (new_quantity, product_id)
    )

    conn.commit()
    conn.close()

    print("Stock updated successfully!")
    print(f"New stock: {new_quantity}")

def low_stock_products():
    print("\n--- Low Stock Products ---")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE quantity <= 5"
    )

    products = cursor.fetchall()

    conn.close()

    if len(products) == 0:
        print("No products are low in stock.")
        return

    for product in products:
        print(
            f"ID: {product[0]} | "
            f"Name: {product[1]} | "
            f"Stock: {product[4]}"
        )
        
def inventory_summary():
    print("\n--- Inventory Summary ---")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total number of products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Total quantity in stock
    cursor.execute("SELECT SUM(quantity) FROM products")
    total_stock = cursor.fetchone()[0]

    # Number of low-stock products
    cursor.execute(
        "SELECT COUNT(*) FROM products WHERE quantity <= 5"
    )
    low_stock_count = cursor.fetchone()[0]

    conn.close()

    if total_stock is None:
        total_stock = 0

    print(f"Total Products: {total_products}")
    print(f"Total Items in Stock: {total_stock}")
    print(f"Low Stock Products: {low_stock_count}")

def view_sales():
    print("\n--- Sales History ---")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sales")
    sales_from_db = cursor.fetchall()

    if len(sales_from_db) == 0:
        print("No sales recorded.")
        conn.close()
        return

    for sale in sales_from_db:
        sale_id = sale[0]
        sale_date = sale[1]
        total = sale[2]

        print("\n==============================")
        print(f"Sale ID: {sale_id}")
        print(f"Date: {sale_date}")
        print("Items:")

        cursor.execute("""
            SELECT product_name, quantity, price, subtotal
            FROM sale_items
            WHERE sale_id = ?
        """, (sale_id,))

        items = cursor.fetchall()

        for item in items:
            print(
                f"  {item[0]} - "
                f"{item[1]} x Rs.{item[2]} "
                f"= Rs.{item[3]}"
            )

        print(f"Total: Rs.{total}")
        print("==============================")

    conn.close()


def main():
    create_database()

    while True:

        print("\n==============================")
        print("  GROCERY STORE MANAGEMENT  ")
        print("=============================")

        print("1. Add Product")
        print("2. View Products")
        print("3. Search Product")
        print("4. Update Product")
        print("5. Delete Product")
        print("6. Create Bill")
        print("7. Restock Product")
        print("8. Low Stock Products")
        print("9. Inventory Summary")
        print("10. Sales History")
        print("11. Exit")

        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            add_product()

        elif choice == "2":
            view_products()
            
        elif choice == "3":
            search_product()

        elif choice == "4":
            update_product()

        elif choice == "5":
            delete_product()

        elif choice == "6":
            create_bill()
        
        elif choice == "7":
            restock_product()

        elif choice == "8":
            low_stock_products()

        elif choice == "9":
            inventory_summary()

        elif choice == "10":
            view_sales()

        elif choice == "11":
            print("Thank you for using the system!")
            break
        else:
             print("invalid choice. Please try again.")

def add_product_gui():
    window = tk.Toplevel()
    window.title("Add Product")
    window.geometry("400x400")

    tk.Label(
        window,
        text="ADD PRODUCT",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    tk.Label(window, text="Product ID").pack()
    id_entry = tk.Entry(window, width=30)
    id_entry.pack(pady=5)

    tk.Label(window, text="Product Name").pack()
    name_entry = tk.Entry(window, width=30)
    name_entry.pack(pady=5)

    tk.Label(window, text="Category").pack()
    category_entry = tk.Entry(window, width=30)
    category_entry.pack(pady=5)

    tk.Label(window, text="Price").pack()
    price_entry = tk.Entry(window, width=30)
    price_entry.pack(pady=5)

    tk.Label(window, text="Quantity").pack()
    quantity_entry = tk.Entry(window, width=30)
    quantity_entry.pack(pady=5)

    def save_product():
        product_id = id_entry.get()
        name = name_entry.get()
        category = category_entry.get()

        try:
            price = float(price_entry.get())
            quantity = int(quantity_entry.get())
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Price must be a number and quantity must be a whole number."
            )
            return

        if product_id == "" or name == "" or category == "":
            messagebox.showerror(
                "Missing Information",
                "Please fill in all fields."
            )
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO products
                (id, name, category, price, quantity)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product_id,
                name,
                category,
                price,
                quantity
            ))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Product added successfully!"
            )

            id_entry.delete(0, tk.END)
            name_entry.delete(0, tk.END)
            category_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
            quantity_entry.delete(0, tk.END)

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Error",
                "Product ID already exists."
            )

        conn.close()

    tk.Button(
        window,
        text="Add Product",
        width=20,
        command=save_product
    ).pack(pady=20)

def view_products_gui():
    window = tk.Toplevel()
    window.title("View Products")
    window.geometry("700x500")

    tk.Label(
        window,
        text="PRODUCT LIST",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    text_box = tk.Text(
        window,
        width=80,
        height=20
    )
    text_box.pack(padx=20, pady=10)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products_from_db = cursor.fetchall()

    conn.close()

    if len(products_from_db) == 0:
        text_box.insert(tk.END, "No products found.")
        return

    for product in products_from_db:
        text_box.insert(
            tk.END,
            f"ID: {product[0]}\n"
            f"Name: {product[1]}\n"
            f"Category: {product[2]}\n"
            f"Price: Rs.{product[3]}\n"
            f"Quantity: {product[4]}\n"
            f"{'-' * 50}\n"
        )

def search_product_gui():
    window = tk.Toplevel()
    window.title("Search Product")
    window.geometry("500x400")

    tk.Label(
        window,
        text="SEARCH PRODUCT",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    tk.Label(
        window,
        text="Enter Product ID:"
    ).pack()

    id_entry = tk.Entry(window, width=30)
    id_entry.pack(pady=10)

    result_box = tk.Text(
        window,
        width=55,
        height=12
    )
    result_box.pack(pady=10)

    def search():
        product_id = id_entry.get()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )

        product = cursor.fetchone()

        conn.close()

        result_box.delete("1.0", tk.END)

        if product is None:
            result_box.insert(tk.END, "Product not found.")
            return

        result_box.insert(
            tk.END,
            f"ID: {product[0]}\n"
            f"Name: {product[1]}\n"
            f"Category: {product[2]}\n"
            f"Price: Rs.{product[3]}\n"
            f"Quantity: {product[4]}"
        )

    tk.Button(
        window,
        text="Search",
        width=20,
        command=search
    ).pack(pady=10)

def search_product_gui():
    window = tk.Toplevel()
    window.title("Search Product")
    window.geometry("500x400")

    tk.Label(
        window,
        text="SEARCH PRODUCT",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    tk.Label(
        window,
        text="Enter Product ID:"
    ).pack()

    id_entry = tk.Entry(window, width=30)
    id_entry.pack(pady=10)

    result_box = tk.Text(
        window,
        width=55,
        height=12
    )
    result_box.pack(pady=10)

    def search():
        product_id = id_entry.get()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )

        product = cursor.fetchone()

        conn.close()

        result_box.delete("1.0", tk.END)

        if product is None:
            result_box.insert(tk.END, "Product not found.")
            return

        result_box.insert(
            tk.END,
            f"ID: {product[0]}\n"
            f"Name: {product[1]}\n"
            f"Category: {product[2]}\n"
            f"Price: Rs.{product[3]}\n"
            f"Quantity: {product[4]}"
        )

    tk.Button(
        window,
        text="Search",
        width=20,
        command=search
    ).pack(pady=10)

def update_product_gui():
    window = tk.Toplevel()
    window.title("Update Product")
    window.geometry("500x500")

    tk.Label(
        window,
        text="UPDATE PRODUCT",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    tk.Label(window, text="Product ID").pack()
    id_entry = tk.Entry(window, width=30)
    id_entry.pack(pady=5)

    tk.Label(window, text="New Name").pack()
    name_entry = tk.Entry(window, width=30)
    name_entry.pack(pady=5)

    tk.Label(window, text="New Category").pack()
    category_entry = tk.Entry(window, width=30)
    category_entry.pack(pady=5)

    tk.Label(window, text="New Price").pack()
    price_entry = tk.Entry(window, width=30)
    price_entry.pack(pady=5)

    tk.Label(window, text="New Quantity").pack()
    quantity_entry = tk.Entry(window, width=30)
    quantity_entry.pack(pady=5)

    def update():
        product_id = id_entry.get()

        try:
            price = float(price_entry.get())
            quantity = int(quantity_entry.get())
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Price must be a number and quantity must be a whole number."
            )
            return

        name = name_entry.get()
        category = category_entry.get()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )

        product = cursor.fetchone()

        if product is None:
            messagebox.showerror(
                "Error",
                "Product not found."
            )
            conn.close()
            return

        cursor.execute("""
            UPDATE products
            SET name = ?, category = ?, price = ?, quantity = ?
            WHERE id = ?
        """, (
            name,
            category,
            price,
            quantity,
            product_id
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Product updated successfully!"
        )

        window.destroy()

    tk.Button(
        window,
        text="Update Product",
        width=20,
        command=update
    ).pack(pady=20)

def delete_product_gui():
    window = tk.Toplevel()
    window.title("Delete Product")
    window.geometry("400x250")

    tk.Label(
        window,
        text="DELETE PRODUCT",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    tk.Label(window, text="Product ID").pack()

    id_entry = tk.Entry(window, width=30)
    id_entry.pack(pady=10)

    def delete():
        product_id = id_entry.get()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )

        product = cursor.fetchone()

        if product is None:
            messagebox.showerror("Error", "Product not found.")
            conn.close()
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete {product[1]}?"
        )

        if confirm:
            cursor.execute(
                "DELETE FROM products WHERE id = ?",
                (product_id,)
            )

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Product deleted successfully!"
            )

        conn.close()
        window.destroy()

    tk.Button(
        window,
        text="Delete Product",
        width=20,
        command=delete
    ).pack(pady=20)

def restock_product_gui():
    window = tk.Toplevel()
    window.title("Restock Product")
    window.geometry("400x300")

    tk.Label(
        window,
        text="RESTOCK PRODUCT",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    tk.Label(window, text="Product ID").pack()

    id_entry = tk.Entry(window, width=30)
    id_entry.pack(pady=5)

    tk.Label(window, text="Quantity to Add").pack()

    quantity_entry = tk.Entry(window, width=30)
    quantity_entry.pack(pady=5)

    def restock():
        product_id = id_entry.get()

        try:
            quantity = int(quantity_entry.get())
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Quantity must be a whole number."
            )
            return

        if quantity <= 0:
            messagebox.showerror(
                "Invalid Input",
                "Quantity must be greater than 0."
            )
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT quantity FROM products WHERE id = ?",
            (product_id,)
        )

        product = cursor.fetchone()

        if product is None:
            messagebox.showerror(
                "Error",
                "Product not found."
            )
            conn.close()
            return

        new_quantity = product[0] + quantity

        cursor.execute(
            "UPDATE products SET quantity = ? WHERE id = ?",
            (new_quantity, product_id)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            f"Stock updated!\nNew stock: {new_quantity}"
        )

        window.destroy()

    tk.Button(
        window,
        text="Restock",
        width=20,
        command=restock
    ).pack(pady=20)

def low_stock_products_gui():
    window = tk.Toplevel()
    window.title("Low Stock Products")
    window.geometry("650x450")

    tk.Label(
        window,
        text="LOW STOCK PRODUCTS",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    text_box = tk.Text(
        window,
        width=70,
        height=20
    )
    text_box.pack(padx=20, pady=10)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE quantity <= 5"
    )

    products = cursor.fetchall()

    conn.close()

    if len(products) == 0:
        text_box.insert(
            tk.END,
            "No products are low in stock."
        )
        return

    for product in products:
        text_box.insert(
            tk.END,
            f"ID: {product[0]}\n"
            f"Name: {product[1]}\n"
            f"Category: {product[2]}\n"
            f"Stock: {product[4]}\n"
            f"{'-' * 50}\n"
        )

def inventory_summary_gui():
    window = tk.Toplevel()
    window.title("Inventory Summary")
    window.geometry("450x350")

    tk.Label(
        window,
        text="INVENTORY SUMMARY",
        font=("Arial", 18, "bold")
    ).pack(pady=30)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantity) FROM products")
    total_stock = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM products WHERE quantity <= 5"
    )
    low_stock_count = cursor.fetchone()[0]

    conn.close()

    if total_stock is None:
        total_stock = 0

    tk.Label(
        window,
        text=f"Total Products: {total_products}",
        font=("Arial", 13)
    ).pack(pady=10)

    tk.Label(
        window,
        text=f"Total Items in Stock: {total_stock}",
        font=("Arial", 13)
    ).pack(pady=10)

    tk.Label(
        window,
        text=f"Low Stock Products: {low_stock_count}",
        font=("Arial", 13)
    ).pack(pady=10)

def view_sales_gui():
    window = tk.Toplevel()
    window.title("Sales History")
    window.geometry("700x600")

    tk.Label(
        window,
        text="SALES HISTORY",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    text_box = tk.Text(
        window,
        width=80,
        height=30
    )
    text_box.pack(padx=20, pady=10)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sales")
    sales_from_db = cursor.fetchall()

    if len(sales_from_db) == 0:
        text_box.insert(
            tk.END,
            "No sales recorded."
        )
        conn.close()
        return

    for sale in sales_from_db:

        sale_id = sale[0]
        sale_date = sale[1]
        total = sale[2]

        text_box.insert(
            tk.END,
            "\n==============================\n"
        )

        text_box.insert(
            tk.END,
            f"Sale ID: {sale_id}\n"
            f"Date: {sale_date}\n"
            f"Items:\n"
        )

        cursor.execute("""
            SELECT product_name, quantity, price, subtotal
            FROM sale_items
            WHERE sale_id = ?
        """, (sale_id,))

        items = cursor.fetchall()

        for item in items:
            text_box.insert(
                tk.END,
                f"  {item[0]} - "
                f"{item[1]} x Rs.{item[2]} "
                f"= Rs.{item[3]}\n"
            )

        text_box.insert(
            tk.END,
            f"Total: Rs.{total}\n"
            "==============================\n"
        )

    conn.close()

def create_bill_gui():
    window = tk.Toplevel()
    window.title("Create Bill")
    window.geometry("700x600")

    tk.Label(
        window,
        text="CREATE BILL",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    input_frame = tk.Frame(window)
    input_frame.pack(pady=10)

    tk.Label(
        input_frame,
        text="Product ID:"
    ).grid(row=0, column=0, padx=5)

    id_entry = tk.Entry(input_frame, width=20)
    id_entry.grid(row=0, column=1, padx=5)

    tk.Label(
        input_frame,
        text="Quantity:"
    ).grid(row=0, column=2, padx=5)

    quantity_entry = tk.Entry(input_frame, width=10)
    quantity_entry.grid(row=0, column=3, padx=5)

    cart = []

    bill_box = tk.Text(
        window,
        width=75,
        height=20
    )
    bill_box.pack(pady=15)

    total_label = tk.Label(
        window,
        text="Total: Rs. 0",
        font=("Arial", 14, "bold")
    )
    total_label.pack(pady=5)

    def add_to_bill():

        product_id = id_entry.get()

        try:
            quantity = int(quantity_entry.get())
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Quantity must be a whole number."
            )
            return

        if quantity <= 0:
            messagebox.showerror(
                "Invalid Input",
                "Quantity must be greater than 0."
            )
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )

        product = cursor.fetchone()

        if product is None:
            messagebox.showerror(
                "Error",
                "Product not found."
            )
            conn.close()
            return

        if quantity > product[4]:
            messagebox.showerror(
                "Error",
                "Not enough stock available."
            )
            conn.close()
            return

        subtotal = product[3] * quantity

        cart.append({
            "product_id": product[0],
            "name": product[1],
            "price": product[3],
            "quantity": quantity,
            "subtotal": subtotal
        })

        conn.close()

        bill_box.insert(
            tk.END,
            f"{product[1]} - "
            f"{quantity} x Rs.{product[3]} "
            f"= Rs.{subtotal}\n"
        )

        total = sum(item["subtotal"] for item in cart)

        total_label.config(
            text=f"Total: Rs. {total}"
        )

        id_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)

    def finish_bill():

        if len(cart) == 0:
            messagebox.showerror(
                "Error",
                "No items added to bill."
            )
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        total = sum(
            item["subtotal"]
            for item in cart
        )

        # Check stock again and reduce it
        for item in cart:

            cursor.execute(
                "SELECT quantity FROM products WHERE id = ?",
                (item["product_id"],)
            )

            product = cursor.fetchone()

            if product is None:
                conn.close()
                messagebox.showerror(
                    "Error",
                    f"Product {item['product_id']} not found."
                )
                return

            if item["quantity"] > product[0]:
                conn.close()
                messagebox.showerror(
                    "Error",
                    f"Not enough stock for {item['name']}."
                )
                return

        # Reduce stock
        for item in cart:

            cursor.execute(
                "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                (item["quantity"], item["product_id"])
            )

        # Generate sale ID
        cursor.execute(
            "SELECT MAX(sale_id) FROM sales"
        )

        last_sale_id = cursor.fetchone()[0]

        if last_sale_id is None:
            sale_id = 1
        else:
            sale_id = last_sale_id + 1

        sale_date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Save sale
        cursor.execute("""
            INSERT INTO sales
            (sale_id, date, total)
            VALUES (?, ?, ?)
        """, (
            sale_id,
            sale_date,
            total
        ))

        # Save sale items
        for item in cart:

            cursor.execute("""
                INSERT INTO sale_items
                (sale_id, product_id, product_name,
                 quantity, price, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                sale_id,
                item["product_id"],
                item["name"],
                item["quantity"],
                item["price"],
                item["subtotal"]
            ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            f"Sale recorded successfully!\n"
            f"Sale ID: {sale_id}\n"
            f"Total: Rs. {total}"
        )

        window.destroy()

    tk.Button(
        input_frame,
        text="Add to Bill",
        command=add_to_bill
    ).grid(row=1, column=0, columnspan=4, pady=15)

    tk.Button(
        window,
        text="Finish Bill",
        width=20,
        command=finish_bill
    ).pack(pady=10)

def reset_system():
    confirm = messagebox.askyesno(
        "Reset System",
        "This will delete ALL products and sales.\n\n"
        "Are you sure you want to reset the system?"
    )

    if not confirm:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM sale_items")
    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM products")

    conn.commit()
    conn.close()

    messagebox.showinfo(
        "Reset Complete",
        "The grocery store system has been reset successfully."
    )

def start_gui():
    create_database()

    window = tk.Tk()

    window.title("Grocery Store Management System")
    window.geometry("700x600")

    title = tk.Label(
        window,
        text="GROCERY STORE MANAGEMENT SYSTEM",
        font=("Arial", 20, "bold")
    )
    title.pack(pady=30)

    subtitle = tk.Label(
        window,
        text="Inventory & Billing System",
        font=("Arial", 12)
    )
    subtitle.pack(pady=5)

    button_frame = tk.Frame(window)
    button_frame.pack(pady=30)

    tk.Button(
        button_frame,
        text="Add Product",
        width=25,
        command=add_product_gui
    ).grid(row=0, column=0, padx=10, pady=10)

    tk.Button(
        button_frame,
        text="View Products",
        width=25,
        command=view_products_gui
    ).grid(row=1, column=0, padx=10, pady=10)

    tk.Button(
        button_frame,
        text="Search Product",
        width=25,
        command=search_product_gui
    ).grid(row=2, column=0, padx=10, pady=10)

    tk.Button(
        button_frame,
        text="Update Product",
        width=25,
        command=update_product_gui
    ).grid(row=3, column=0, padx=10, pady=10)

    tk.Button(
        button_frame,
        text="Delete Product",
        width=25,
        command=delete_product_gui
    ).grid(row=4, column=0, padx=10, pady=10)

    tk.Button(
        button_frame,
        text="Create Bill",
        width=25,
        command=create_bill_gui
    ).grid(row=0, column=1, padx=10, pady=10)

    tk.Button(
        button_frame,
        text="Restock Product",
        width=25,
        command=restock_product_gui
    ).grid(row=1, column=1, padx=10, pady=10)

    tk.Button(
        button_frame,
        text="Low Stock Products",
        width=25,
        command=low_stock_products_gui
    ).grid(row=2, column=1, padx=10, pady=10)

    tk.Button(
        button_frame,
        text="Inventory Summary",
        width=25,
        command=inventory_summary_gui
    ).grid(row=3, column=1, padx=10, pady=10)

    tk.Button(
        button_frame,
        text="Sales History",
        width=25,
        command=view_sales_gui
    ).grid(row=4, column=1, padx=10, pady=10)

    tk.Button(
        window,
        text="Reset System",
        width=20,
        command=reset_system
        ).pack(pady=5)

    tk.Button(
        window,
        text="Exit",
        width=20,
        command=window.destroy
    ).pack(pady=20)

    window.mainloop()

if __name__ == "__main__":
    start_gui()