import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


class InventorySystem:

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Inventory Management System")
        self.root.geometry("900 integrity_check")
        self.root.geometry("900x550")
        self.root.configure(bg="#f4f6f9")

        # Initialize Database
        self.conn = sqlite3.connect("inventory.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        # UI Styles
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview.Heading",
            font=("Arial", 11, "bold"),
            background="#2c3e50",
            foreground="white",
        )
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.map("Treeview", background=[("selected", "#3498db")])

        # Title Banner
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(
            title_frame,
            text="📦 INVENTORY MANAGEMENT SYSTEM",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        title_label.pack(pady=15)

        # Main Layout Splitting (Left Form, Right Data Grid)
        main_frame = tk.Frame(self.root, bg="#f4f6f9")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Side: Entry Fields Form
        form_frame = tk.LabelFrame(
            main_frame,
            text=" Item Management Form ",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=15,
            pady=15,
        )
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        tk.Label(form_frame, text="Item Name:", font=("Arial", 10), bg="white").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.name_entry = tk.Entry(
            form_frame, font=("Arial", 10), width=22, bd=2, relief=tk.GROOVE
        )
        self.name_entry.grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Category:", font=("Arial", 10), bg="white").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.category_entry = tk.Entry(
            form_frame, font=("Arial", 10), width=22, bd=2, relief=tk.GROOVE
        )
        self.category_entry.grid(row=1, column=1, pady=5)

        tk.Label(form_frame, text="Quantity:", font=("Arial", 10), bg="white").grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.qty_entry = tk.Entry(
            form_frame, font=("Arial", 10), width=22, bd=2, relief=tk.GROOVE
        )
        self.qty_entry.grid(row=2, column=1, pady=5)

        tk.Label(
            form_frame, text="Price per Unit ($):", font=("Arial", 10), bg="white"
        ).grid(row=3, column=0, sticky="w", pady=5)
        self.price_entry = tk.Entry(
            form_frame, font=("Arial", 10), width=22, bd=2, relief=tk.GROOVE
        )
        self.price_entry.grid(row=3, column=1, pady=5)

        # Control Buttons
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        tk.Button(
            btn_frame,
            text="➕ Add Item",
            font=("Arial", 10, "bold"),
            bg="#2ecc71",
            fg="white",
            width=18,
            command=self.add_item,
            bd=0,
            cursor="hand2",
        ).pack(pady=4)
        tk.Button(
            btn_frame,
            text="🔄 Update Selected",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            width=18,
            command=self.update_item,
            bd=0,
            cursor="hand2",
        ).pack(pady=4)
        tk.Button(
            btn_frame,
            text="🗑️ Delete Selected",
            font=("Arial", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            width=18,
            command=self.delete_item,
            bd=0,
            cursor="hand2",
        ).pack(pady=4)
        tk.Button(
            btn_frame,
            text="🧹 Clear Fields",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            width=18,
            command=self.clear_entries,
            bd=0,
            cursor="hand2",
        ).pack(pady=4)

        # Right Side: Data Visualization Table
        data_frame = tk.Frame(main_frame, bg="white")
        data_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        columns = ("id", "name", "category", "quantity", "price", "total")
        self.tree = ttk.Treeview(data_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Item Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("quantity", text="Stock Qty")
        self.tree.heading("price", text="Price ($)")
        self.tree.heading("total", text="Total Value ($)")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=150)
        self.tree.column("category", width=100)
        self.tree.column("quantity", width=80, anchor="center")
        self.tree.column("price", width=80, anchor="center")
        self.tree.column("total", width=100, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.get_selected_row)

        # Summary Status Bar at the bottom
        self.summary_label = tk.Label(
            self.root,
            text="Total Items: 0 | Total Inventory Valuation: $0.00",
            font=("Arial", 11, "bold"),
            bg="#bdc3c7",
            fg="#2c3e50",
        )
        self.summary_label.pack(fill=tk.X, side=tk.BOTTOM)

        self.populate_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL
            )
        """)
        self.conn.commit()

    def populate_table(self):
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.cursor.execute(
            "SELECT id, name, category, quantity, price, (quantity * price) FROM"
            " inventory"
        )
        rows = self.cursor.fetchall()

        total_qty = 0
        total_value = 0.0

        for row in rows:
            self.tree.insert("", tk.END, values=row)
            total_qty += row[3]  # Fixed: indexing array correctly
            total_value += row[5]

        self.summary_label.config(
            text=(
                f"📊 Total Units in Stock: {total_qty}   |   💰 Total Inventory"
                f" Valuation: ${total_value:,.2f}"
            )
        )

    def add_item(self):
        name = self.name_entry.get().strip()
        cat = self.category_entry.get().strip()
        qty = self.qty_entry.get().strip()
        price = self.price_entry.get().strip()

        if not (name and qty and price):
            messagebox.showerror(
                "Validation Error", "All fields except Category are required!"
            )
            return

        try:
            self.cursor.execute(
                "INSERT INTO inventory (name, category, quantity, price) VALUES"
                " (?, ?, ?, ?)",
                (name, cat, int(qty), float(price)),
            )
            self.conn.commit()
            self.populate_table()
            self.clear_entries()
            messagebox.showinfo(
                "Success", f"'{name}' successfully added to inventory."
            )
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Error", f"An item with the name '{name}' already exists."
            )
        except ValueError:
            messagebox.showerror(
                "Type Error", "Quantity must be an integer; Price must be a decimal."
            )

    def get_selected_row(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
        values = self.tree.item(selected_item, "values")

        self.clear_entries()
        self.name_entry.insert(0, values[1])
        self.category_entry.insert(0, values[2])
        self.qty_entry.insert(0, values[3])
        self.price_entry.insert(0, values[4])

    def update_item(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning(
                "Selection Missing", "Please select an item from the grid to update."
            )
            return

        item_id = self.tree.item(selected_item, "values")[0]
        name = self.name_entry.get().strip()
        cat = self.category_entry.get().strip()
        qty = self.qty_entry.get().strip()
        price = self.price_entry.get().strip()

        try:
            self.cursor.execute(
                "UPDATE inventory SET name=?, category=?, quantity=?, price=? WHERE"
                " id=?",
                (name, cat, int(qty), float(price), item_id),
            )
            self.conn.commit()
            self.populate_table()
            self.clear_entries()
            messagebox.showinfo("Updated", "Item record updated successfully.")
        except ValueError:
            messagebox.showerror(
                "Type Error", "Please verify inputs are numeric before updating."
            )
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Another item already uses that name.")

    def delete_item(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning(
                "Selection Missing", "Select an item from the table grid to delete.")
