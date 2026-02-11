import sqlite3
from tkinter import ttk, messagebox


class SupplierDB:
    def __init__(self, db_name="erp.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_supplier(self, name, phone, address):
        query = "INSERT INTO suppliers (name, phone, address) VALUES (?, ?, ?)"
        self.conn.execute(query, (name, phone, address))
        self.conn.commit()

    def update_supplier(self, supplier_id, name, phone, address):
        query = """
        UPDATE suppliers
        SET name = ?, phone = ?, address = ?
        WHERE id = ?
        """
        self.conn.execute(query, (name, phone, address, supplier_id))
        self.conn.commit()

    def get_all_suppliers(self):
        cursor = self.conn.execute("SELECT * FROM suppliers ORDER BY id DESC")
        return cursor.fetchall()


class SupplierUI:
    def __init__(self, parent):
        self.db = SupplierDB()
        self.selected_id = None

        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== Inputs =====
        form = ttk.LabelFrame(frame, text="Supplier Info")
        form.pack(fill="x", pady=5)

        ttk.Label(form, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(form)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Phone:").grid(row=1, column=0, padx=5, pady=5)
        self.phone_entry = ttk.Entry(form)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Address:").grid(row=2, column=0, padx=5, pady=5)
        self.address_entry = ttk.Entry(form)
        self.address_entry.grid(row=2, column=1, padx=5, pady=5)

        # ===== Buttons =====
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Add", command=self.add_supplier).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update", command=self.update_supplier).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_suppliers).pack(side="left", padx=5)

        # ===== Table =====
        columns = ("ID", "Name", "Phone", "Address")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.refresh_suppliers()

    # ================= Logic =================

    def add_supplier(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()

        if not name:
            messagebox.showwarning("Warning", "Name is required")
            return

        self.db.add_supplier(name, phone, address)
        self.clear_fields()
        self.refresh_suppliers()

    def update_supplier(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Select a supplier first")
            return

        name = self.name_entry.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()

        self.db.update_supplier(self.selected_id, name, phone, address)
        self.clear_fields()
        self.refresh_suppliers()

    def refresh_suppliers(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for supplier in self.db.get_all_suppliers():
            self.tree.insert("", "end", values=supplier)

    def on_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return

        values = self.tree.item(selected, "values")
        self.selected_id = values[0]

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, values[1])

        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(0, values[2])

        self.address_entry.delete(0, "end")
        self.address_entry.insert(0, values[3])

    def clear_fields(self):
        self.selected_id = None
        self.name_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.address_entry.delete(0, "end")
