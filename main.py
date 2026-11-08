import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# --- Database Setup & Auto-Seeding ---
connection = sqlite3.connect("inventory.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS spare_parts (
    id INTEGER PRIMARY KEY,
    part_name TEXT NOT NULL,
    stock_quantity INTEGER NOT NULL,
    price_eur REAL NOT NULL
)
""")

# If the database is empty, automatically fill it with Leibinger parts
cursor.execute("SELECT COUNT(*) FROM spare_parts")
if cursor.fetchone()[0] == 0:
    leibinger_parts = [
        ("Leibinger 7-Digit Rotary Numbering Machine", 12, 245.50),
        ("Leibinger Numbering Wheel", 45, 18.00),
        ("Leibinger Plunger Spring", 120, 2.50),
        ("Leibinger Operating Lever", 30, 42.00),
        ("Leibinger Retaining Ring", 250, 0.80),
        ("Leibinger Ink Pad / Cartridge", 85, 12.50)
    ]
    for part in leibinger_parts:
        cursor.execute("INSERT INTO spare_parts (part_name, stock_quantity, price_eur) VALUES (?, ?, ?)", part)
    connection.commit()

# --- Functions ---
def refresh_table():
    for item in tree.get_children():
        tree.delete(item)
        
    cursor.execute("SELECT id, part_name, stock_quantity, price_eur FROM spare_parts ORDER BY id")
    rows = cursor.fetchall()
    
    for i, row in enumerate(rows):
        tag = "even" if i % 2 == 0 else "odd"
        tree.insert("", tk.END, values=row, tags=(tag,))

def clear_entries():
    part_id_var.set("")
    part_name_var.set("")
    stock_quantity_var.set("")
    price_eur_var.set("")
    barcode_var.set("")
    status_var.set("")

def on_row_select(event):
    selected = tree.selection()
    if not selected:
        return
    item = tree.item(selected[0])
    values = item['values']
    
    part_id_var.set(values[0])
    part_name_var.set(values[1])
    stock_quantity_var.set(values[2])
    price_eur_var.set(values[3])

def add_spare_part():
    name = part_name_var.get().strip()
    stock = stock_quantity_var.get().strip()
    price = price_eur_var.get().strip()
    
    if not name or not stock or not price:
        messagebox.showerror("Error", "All fields are required.")
        return
        
    try:
        stock = int(stock)
        price = float(price)
        if stock < 0 or price < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Stock and price must be valid positive numbers.")
        return
        
    cursor.execute("INSERT INTO spare_parts (part_name, stock_quantity, price_eur) VALUES (?, ?, ?)", (name, stock, price))
    connection.commit()
    status_var.set(f"Added successfully with ID {cursor.lastrowid}.")
    refresh_table()
    clear_entries()

def update_stock_quantity():
    part_id = part_id_var.get().strip()
    stock = stock_quantity_var.get().strip()
    
    if not part_id or not stock:
        messagebox.showerror("Error", "Part ID and new Stock are required.")
        return
        
    try:
        stock = int(stock)
    except ValueError:
        messagebox.showerror("Error", "Stock must be a valid number.")
        return
        
    cursor.execute("SELECT id FROM spare_parts WHERE id = ?", (part_id,))
    if not cursor.fetchone():
        messagebox.showerror("Error", f"No part found with ID {part_id}.")
        return
        
    cursor.execute("UPDATE spare_parts SET stock_quantity = ? WHERE id = ?", (stock, part_id))
    connection.commit()
    status_var.set(f"Stock for ID {part_id} updated.")
    refresh_table()

def update_part_name():
    part_id = part_id_var.get().strip()
    name = part_name_var.get().strip()
    
    if not part_id or not name:
        messagebox.showerror("Error", "Part ID and new Name are required.")
        return
        
    cursor.execute("SELECT id FROM spare_parts WHERE id = ?", (part_id,))
    if not cursor.fetchone():
        messagebox.showerror("Error", f"No part found with ID {part_id}.")
        return
        
    cursor.execute("UPDATE spare_parts SET part_name = ? WHERE id = ?", (name, part_id))
    connection.commit()
    status_var.set(f"Name for ID {part_id} updated.")
    refresh_table()

def delete_spare_part():
    part_id = part_id_var.get().strip()
    
    if not part_id:
        messagebox.showerror("Error", "Part ID is required.")
        return
        
    cursor.execute("SELECT part_name FROM spare_parts WHERE id = ?", (part_id,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("Error", f"No part found with ID {part_id}.")
        return
        
    if messagebox.askyesno("Confirm", f"Delete '{row[0]}' (ID {part_id})?"):
        cursor.execute("DELETE FROM spare_parts WHERE id = ?", (part_id,))
        connection.commit()
        status_var.set(f"Part ID {part_id} deleted.")
        refresh_table()
        clear_entries()

def process_barcode(event):
    scanned_id = barcode_var.get().strip()
    if not scanned_id:
        return
        
    cursor.execute("SELECT stock_quantity, part_name FROM spare_parts WHERE id = ?", (scanned_id,))
    row = cursor.fetchone()
    
    if not row:
        status_var.set(f"Barcode ID {scanned_id} not found.")
        barcode_var.set("")
        return
        
    current_stock = row[0]
    part_name = row[1]
    
    if current_stock > 0:
        new_stock = current_stock - 1
        cursor.execute("UPDATE spare_parts SET stock_quantity = ? WHERE id = ?", (new_stock, scanned_id))
        connection.commit()
        status_var.set(f"Scan Success: '{part_name}' stock reduced to {new_stock}.")
    else:
        status_var.set(f"Warning: '{part_name}' is out of stock (0).")
        
    barcode_var.set("")
    refresh_table()

def on_close():
    connection.close()
    root.destroy()

# --- GUI Setup ---
root = tk.Tk()
root.title("Spare Parts Inventory")
root.geometry("800x650")
root.configure(bg="#f3f7fb")

# Variables
part_id_var = tk.StringVar()
part_name_var = tk.StringVar()
stock_quantity_var = tk.StringVar()
price_eur_var = tk.StringVar()
barcode_var = tk.StringVar()
status_var = tk.StringVar()

# Header
header = tk.Frame(root, bg="#1f4e79", padx=20, pady=16)
header.pack(fill=tk.X)
tk.Label(header, text="Spare Parts Inventory", bg="#1f4e79", fg="#ffffff", font=("Segoe UI", 18, "bold")).pack(anchor=tk.W)
tk.Label(header, text="Add, update, and remove parts stored in inventory.db", bg="#1f4e79", fg="#d6e4f0", font=("Segoe UI", 10)).pack(anchor=tk.W, pady=(4, 0))

# Body Frame
body = tk.Frame(root, bg="#f3f7fb", padx=16, pady=12)
body.pack(fill=tk.BOTH, expand=True)

# Top Section: Barcode Scanner
barcode_frame = tk.Frame(body, bg="#f3f7fb")
barcode_frame.pack(fill=tk.X, pady=(0, 10))
tk.Label(barcode_frame, text="Quick Scan (Barcode ID):", bg="#f3f7fb", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
barcode_entry = ttk.Entry(barcode_frame, textvariable=barcode_var, width=20)
barcode_entry.pack(side=tk.LEFT, padx=10)
barcode_entry.bind("<Return>", process_barcode)
tk.Label(barcode_frame, text="(Type ID and press Enter to reduce stock by 1)", bg="#f3f7fb", fg="gray", font=("Segoe UI", 9)).pack(side=tk.LEFT)

# Treeview (Table)
table_frame = tk.Frame(body, bg="#ffffff")
table_frame.pack(fill=tk.BOTH, expand=True)

columns = ("id", "part_name", "stock_quantity", "price_eur")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
tree.heading("id", text="ID")
tree.heading("part_name", text="Part name")
tree.heading("stock_quantity", text="Stock")
tree.heading("price_eur", text="Price (EUR)")
tree.column("id", width=80, anchor=tk.CENTER)
tree.column("part_name", width=360, anchor=tk.W)
tree.column("stock_quantity", width=140, anchor=tk.CENTER)
tree.column("price_eur", width=160, anchor=tk.E)
tree.tag_configure("even", background="#ffffff")
tree.tag_configure("odd", background="#f3f7fb")
tree.bind("<<TreeviewSelect>>", on_row_select)

scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Form Section
form_frame = tk.Frame(body, bg="#ffffff", pady=10)
form_frame.pack(fill=tk.X, pady=(12, 0))

fields = (
    (0, 0, "Part ID", part_id_var),
    (0, 2, "Part name", part_name_var),
    (1, 0, "Stock quantity", stock_quantity_var),
    (1, 2, "Price (EUR)", price_eur_var),
)
for row, col, label, var in fields:
    tk.Label(form_frame, text=label, bg="#ffffff").grid(row=row, column=col, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(form_frame, textvariable=var, width=28).grid(row=row, column=col+1, sticky=tk.EW, padx=5, pady=5)

# Buttons
buttons_frame = tk.Frame(form_frame, bg="#ffffff")
buttons_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=10)
ttk.Button(buttons_frame, text="Add Part", command=add_spare_part).pack(side=tk.LEFT, padx=5)
ttk.Button(buttons_frame, text="Update Stock", command=update_stock_quantity).pack(side=tk.LEFT, padx=5)
ttk.Button(buttons_frame, text="Update Name", command=update_part_name).pack(side=tk.LEFT, padx=5)
ttk.Button(buttons_frame, text="Delete Part", command=delete_spare_part).pack(side=tk.LEFT, padx=5)
ttk.Button(buttons_frame, text="Clear", command=clear_entries).pack(side=tk.LEFT, padx=5)

# Status Label
tk.Label(form_frame, textvariable=status_var, fg="blue", bg="#ffffff").grid(row=3, column=0, columnspan=4, sticky=tk.W, padx=5)

# Personal Signature
tk.Label(form_frame, text="Made by Derin Rodoslu", fg="gray", bg="#ffffff", font=("Segoe UI", 8)).grid(row=4, column=0, columnspan=4, sticky=tk.E, padx=5, pady=5)

refresh_table()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
