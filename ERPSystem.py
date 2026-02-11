import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
import datetime
import os
from datetime import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class ERPSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated ERP System")
        self.root.geometry("1400x800")
        
        # Create database
        self.create_database()
        
        # Create user interface
        self.setup_ui()
        
    def create_database(self):
        """Create database and tables"""
        self.conn = sqlite3.connect('erp_system_english.db')
        self.cursor = self.conn.cursor()
        
        # Customers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_code TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                email TEXT,
                registration_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        # Suppliers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_code TEXT PRIMARY KEY,
                supplier_name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                email TEXT,
                registration_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        # Products table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_code TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                unit_of_measure TEXT,
                purchase_price REAL DEFAULT 0,
                sale_price REAL DEFAULT 0,
                minimum_limit INTEGER DEFAULT 10,
                date_added DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        # Inventory table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT,
                movement TEXT, -- 'in' or 'out'
                quantity INTEGER,
                date DATE DEFAULT CURRENT_DATE,
                reference TEXT, -- invoice number
                FOREIGN KEY (product_code) REFERENCES products(product_code)
            )
        ''')
        
        # Sales table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                invoice_number TEXT PRIMARY KEY,
                invoice_date DATE DEFAULT CURRENT_DATE,
                customer_code TEXT,
                total_invoice REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                net_invoice REAL DEFAULT 0,
                invoice_status TEXT DEFAULT 'open',
                FOREIGN KEY (customer_code) REFERENCES customers(customer_code)
            )
        ''')
        
        # Sales details table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT,
                product_code TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                FOREIGN KEY (invoice_number) REFERENCES sales(invoice_number),
                FOREIGN KEY (product_code) REFERENCES products(product_code)
            )
        ''')
        
        # Purchases table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                invoice_number TEXT PRIMARY KEY,
                invoice_date DATE DEFAULT CURRENT_DATE,
                supplier_code TEXT,
                total_invoice REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                net_invoice REAL DEFAULT 0,
                invoice_status TEXT DEFAULT 'open',
                FOREIGN KEY (supplier_code) REFERENCES suppliers(supplier_code)
            )
        ''')
        
        # Purchase details table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT,
                product_code TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                FOREIGN KEY (invoice_number) REFERENCES purchases(invoice_number),
                FOREIGN KEY (product_code) REFERENCES products(product_code)
            )
        ''')
        
        self.conn.commit()
        
    def setup_ui(self):
        """Create main user interface"""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Sales Report", command=self.show_sales_report)
        reports_menu.add_command(label="Inventory Report", command=self.show_inventory_report)
        reports_menu.add_command(label="Customers Report", command=self.show_customers_report)
        reports_menu.add_command(label="Suppliers Report", command=self.show_suppliers_report)
        
        # Create Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_customers_tab()
        self.create_suppliers_tab()
        self.create_products_tab()
        self.create_sales_tab()
        self.create_purchases_tab()
        self.create_inventory_tab()
        self.create_reports_tab()
        
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        
        # Metrics frame
        metrics_frame = ttk.LabelFrame(self.dashboard_tab, text="Key Metrics")
        metrics_frame.pack(fill='x', padx=10, pady=10)
        
        # Create metrics
        metrics = [
            ("Total Sales", self.get_total_sales, "#4CAF50"),
            ("Total Purchases", self.get_total_purchases, "#2196F3"),
            ("Net Profit", self.get_net_profit, "#FF9800"),
            ("Customer Count", self.get_customers_count, "#9C27B0"),
            ("Product Count", self.get_products_count, "#F44336"),
            ("Inventory Value", self.get_inventory_value, "#00BCD4")
        ]
        
        for i, (title, func, color) in enumerate(metrics):
            frame = ttk.Frame(metrics_frame)
            frame.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='nsew')
            
            lbl_title = tk.Label(frame, text=title, font=('Arial', 12, 'bold'))
            lbl_title.pack()
            
            lbl_value = tk.Label(frame, text=str(func()), font=('Arial', 18, 'bold'), fg=color)
            lbl_value.pack()
            
            # Update values every 30 seconds
            def update_value(label=title, value_func=func, lbl=lbl_value):
                lbl.config(text=str(value_func()))
                self.root.after(30000, lambda: update_value(label, value_func, lbl))
            
            self.root.after(1000, update_value)
            
        # Charts frame
        charts_frame = ttk.LabelFrame(self.dashboard_tab, text="Data Analytics")
        charts_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create charts
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Monthly sales chart
        sales_data = self.get_monthly_sales()
        axes[0, 0].bar(sales_data['month'], sales_data['sales'])
        axes[0, 0].set_title('Monthly Sales')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Top customers chart
        customers_data = self.get_top_customers()
        axes[0, 1].barh(customers_data['customer'], customers_data['sales'])
        axes[0, 1].set_title('Top Customers')
        
        # Inventory status chart
        inventory_data = self.get_inventory_status()
        axes[1, 0].pie(inventory_data['count'], labels=inventory_data['status'], autopct='%1.1f%%')
        axes[1, 0].set_title('Inventory Status')
        
        # Sales vs Purchases comparison
        comparison_data = self.get_sales_purchases_comparison()
        axes[1, 1].plot(comparison_data['month'], comparison_data['sales'], marker='o', label='Sales')
        axes[1, 1].plot(comparison_data['month'], comparison_data['purchases'], marker='s', label='Purchases')
        axes[1, 1].set_title('Sales vs Purchases')
        axes[1, 1].legend()
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Display charts in interface
        canvas = FigureCanvasTkAgg(fig, charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_customers_tab(self):
        """Create customers tab"""
        self.customers_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_tab, text="Customers")
        
        # Input frame
        input_frame = ttk.LabelFrame(self.customers_tab, text="Customer Information")
        input_frame.pack(fill='x', padx=10, pady=10)
        
        # Input fields
        fields = [
            ("Customer Code:", "customer_code"),
            ("Customer Name:", "customer_name"),
            ("Phone:", "phone"),
            ("Address:", "address"),
            ("Email:", "email")
        ]
        
        self.customer_entries = {}
        
        for i, (label, field) in enumerate(fields):
            lbl = ttk.Label(input_frame, text=label)
            lbl.grid(row=i, column=0, padx=10, pady=5, sticky='e')
            
            entry = ttk.Entry(input_frame, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            
            self.customer_entries[field] = entry
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        ttk.Button(buttons_frame, text="Add", command=self.add_customer).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Edit", command=self.edit_customer).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_customer).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Clear", command=self.clear_customer_fields).pack(side='left', padx=5)
        
        # Data table frame
        table_frame = ttk.LabelFrame(self.customers_tab, text="Customers List")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Create table
        self.customers_tree = ttk.Treeview(
            table_frame,
            yscrollcommand=scrollbar.set,
            selectmode='browse'
        )
        self.customers_tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.customers_tree.yview)
        
        # Table columns
        columns = ("Customer Code", "Customer Name", "Phone", "Address", "Email", "Registration Date")
        self.customers_tree['columns'] = columns
        self.customers_tree['show'] = 'headings'
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=150)
        
        # Bind row selection event
        self.customers_tree.bind('<<TreeviewSelect>>', self.on_customer_select)
        
        # Load data
        self.load_customers()
    
    def create_suppliers_tab(self):
        """Create suppliers tab"""
        self.suppliers_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.suppliers_tab, text="Suppliers")
        
        # Input frame
        input_frame = ttk.LabelFrame(self.suppliers_tab, text="Supplier Information")
        input_frame.pack(fill='x', padx=10, pady=10)
        
        # Input fields
        fields = [
            ("Supplier Code:", "supplier_code"),
            ("Supplier Name:", "supplier_name"),
            ("Phone:", "phone"),
            ("Address:", "address"),
            ("Email:", "email")
        ]
        
        self.supplier_entries = {}
        
        for i, (label, field) in enumerate(fields):
            lbl = ttk.Label(input_frame, text=label)
            lbl.grid(row=i, column=0, padx=10, pady=5, sticky='e')
            
            entry = ttk.Entry(input_frame, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            
            self.supplier_entries[field] = entry
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        ttk.Button(buttons_frame, text="Add", command=self.add_supplier).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Edit", command=self.edit_supplier).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_supplier).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Clear", command=self.clear_supplier_fields).pack(side='left', padx=5)
        
        # Data table frame
        table_frame = ttk.LabelFrame(self.suppliers_tab, text="Suppliers List")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Create table
        self.suppliers_tree = ttk.Treeview(
            table_frame,
            yscrollcommand=scrollbar.set,
            selectmode='browse'
        )
        self.suppliers_tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.suppliers_tree.yview)
        
        # Table columns
        columns = ("Supplier Code", "Supplier Name", "Phone", "Address", "Email", "Registration Date")
        self.suppliers_tree['columns'] = columns
        self.suppliers_tree['show'] = 'headings'
        
        for col in columns:
            self.suppliers_tree.heading(col, text=col)
            self.suppliers_tree.column(col, width=150)
        
        # Bind row selection event
        self.suppliers_tree.bind('<<TreeviewSelect>>', self.on_supplier_select)
        
        # Load data
        self.load_suppliers()
    
    def create_products_tab(self):
        """Create products tab"""
        self.products_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.products_tab, text="Products")
        
        # Input frame
        input_frame = ttk.LabelFrame(self.products_tab, text="Product Information")
        input_frame.pack(fill='x', padx=10, pady=10)
        
        # Input fields
        fields = [
            ("Product Code:", "product_code"),
            ("Product Name:", "product_name"),
            ("Unit of Measure:", "unit_of_measure"),
            ("Purchase Price:", "purchase_price"),
            ("Sale Price:", "sale_price"),
            ("Minimum Limit:", "minimum_limit")
        ]
        
        self.product_entries = {}
        
        for i, (label, field) in enumerate(fields):
            lbl = ttk.Label(input_frame, text=label)
            lbl.grid(row=i, column=0, padx=10, pady=5, sticky='e')
            
            entry = ttk.Entry(input_frame, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            
            self.product_entries[field] = entry
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        ttk.Button(buttons_frame, text="Add", command=self.add_product).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Edit", command=self.edit_product).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_product).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Clear", command=self.clear_product_fields).pack(side='left', padx=5)
        
        # Data table frame
        table_frame = ttk.LabelFrame(self.products_tab, text="Products List")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Create table
        self.products_tree = ttk.Treeview(
            table_frame,
            yscrollcommand=scrollbar.set,
            selectmode='browse'
        )
        self.products_tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.products_tree.yview)
        
        # Table columns
        columns = ("Product Code", "Product Name", "Unit", "Purchase Price", "Sale Price", "Min Limit", "Date Added")
        self.products_tree['columns'] = columns
        self.products_tree['show'] = 'headings'
        
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=120)
        
        # Bind row selection event
        self.products_tree.bind('<<TreeviewSelect>>', self.on_product_select)
        
        # Load data
        self.load_products()
    
    def create_sales_tab(self):
        """Create sales tab"""
        self.sales_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_tab, text="Sales")
        
        # Invoice header frame
        header_frame = ttk.LabelFrame(self.sales_tab, text="Invoice Information")
        header_frame.pack(fill='x', padx=10, pady=10)
        
        # First row
        ttk.Label(header_frame, text="Invoice Number:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.sales_invoice_entry = ttk.Entry(header_frame, width=20)
        self.sales_invoice_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(header_frame, text="Date:").grid(row=0, column=2, padx=10, pady=5, sticky='e')
        self.sales_date_entry = ttk.Entry(header_frame, width=20)
        self.sales_date_entry.grid(row=0, column=3, padx=10, pady=5)
        self.sales_date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
        # Second row
        ttk.Label(header_frame, text="Customer:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.sales_customer_combo = ttk.Combobox(header_frame, width=20, state='readonly')
        self.sales_customer_combo.grid(row=1, column=1, padx=10, pady=5)
        self.load_customers_combo()
        
        # Invoice items frame
        items_frame = ttk.LabelFrame(self.sales_tab, text="Invoice Items")
        items_frame.pack(fill='x', padx=10, pady=10)
        
        # Item input fields
        ttk.Label(items_frame, text="Product:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.sales_product_combo = ttk.Combobox(items_frame, width=20, state='readonly')
        self.sales_product_combo.grid(row=0, column=1, padx=10, pady=5)
        self.sales_product_combo.bind('<<ComboboxSelected>>', self.on_sales_product_select)
        self.load_products_combo()
        
        ttk.Label(items_frame, text="Quantity:").grid(row=0, column=2, padx=10, pady=5, sticky='e')
        self.sales_quantity_entry = ttk.Entry(items_frame, width=10)
        self.sales_quantity_entry.grid(row=0, column=3, padx=10, pady=5)
        
        ttk.Label(items_frame, text="Price:").grid(row=0, column=4, padx=10, pady=5, sticky='e')
        self.sales_price_entry = ttk.Entry(items_frame, width=10)
        self.sales_price_entry.grid(row=0, column=5, padx=10, pady=5)
        
        ttk.Button(items_frame, text="Add Item", command=self.add_sales_item).grid(row=0, column=6, padx=10, pady=5)
        
        # Invoice items table
        items_table_frame = ttk.Frame(self.sales_tab)
        items_table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(items_table_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.sales_items_tree = ttk.Treeview(
            items_table_frame,
            yscrollcommand=scrollbar.set,
            selectmode='browse',
            height=8
        )
        self.sales_items_tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.sales_items_tree.yview)
        
        columns = ("Product Code", "Product Name", "Quantity", "Price", "Total")
        self.sales_items_tree['columns'] = columns
        self.sales_items_tree['show'] = 'headings'
        
        for col in columns:
            self.sales_items_tree.heading(col, text=col)
            self.sales_items_tree.column(col, width=120)
        
        # Invoice totals frame
        totals_frame = ttk.LabelFrame(self.sales_tab, text="Invoice Totals")
        totals_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(totals_frame, text="Total:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.sales_total_label = ttk.Label(totals_frame, text="0.00", font=('Arial', 12, 'bold'))
        self.sales_total_label.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(totals_frame, text="Discount:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.sales_discount_entry = ttk.Entry(totals_frame, width=15)
        self.sales_discount_entry.grid(row=1, column=1, padx=10, pady=5)
        self.sales_discount_entry.insert(0, "0")
        
        ttk.Label(totals_frame, text="Net Total:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.sales_net_label = ttk.Label(totals_frame, text="0.00", font=('Arial', 14, 'bold'), foreground='green')
        self.sales_net_label.grid(row=2, column=1, padx=10, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(self.sales_tab)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="Save Invoice", command=self.save_sales_invoice).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="New Invoice", command=self.clear_sales_form).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Delete Item", command=self.delete_sales_item).pack(side='left', padx=5)
    
    def create_purchases_tab(self):
        """Create purchases tab"""
        self.purchases_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.purchases_tab, text="Purchases")
        
        # Invoice header frame
        header_frame = ttk.LabelFrame(self.purchases_tab, text="Invoice Information")
        header_frame.pack(fill='x', padx=10, pady=10)
        
        # First row
        ttk.Label(header_frame, text="Invoice Number:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.purchases_invoice_entry = ttk.Entry(header_frame, width=20)
        self.purchases_invoice_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(header_frame, text="Date:").grid(row=0, column=2, padx=10, pady=5, sticky='e')
        self.purchases_date_entry = ttk.Entry(header_frame, width=20)
        self.purchases_date_entry.grid(row=0, column=3, padx=10, pady=5)
        self.purchases_date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
        # Second row
        ttk.Label(header_frame, text="Supplier:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.purchases_supplier_combo = ttk.Combobox(header_frame, width=20, state='readonly')
        self.purchases_supplier_combo.grid(row=1, column=1, padx=10, pady=5)
        self.load_suppliers_combo()
        
        # Invoice items frame
        items_frame = ttk.LabelFrame(self.purchases_tab, text="Invoice Items")
        items_frame.pack(fill='x', padx=10, pady=10)
        
        # Item input fields
        ttk.Label(items_frame, text="Product:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.purchases_product_combo = ttk.Combobox(items_frame, width=20, state='readonly')
        self.purchases_product_combo.grid(row=0, column=1, padx=10, pady=5)
        self.purchases_product_combo.bind('<<ComboboxSelected>>', self.on_purchases_product_select)
        self.load_products_combo_purchases()
        
        ttk.Label(items_frame, text="Quantity:").grid(row=0, column=2, padx=10, pady=5, sticky='e')
        self.purchases_quantity_entry = ttk.Entry(items_frame, width=10)
        self.purchases_quantity_entry.grid(row=0, column=3, padx=10, pady=5)
        
        ttk.Label(items_frame, text="Price:").grid(row=0, column=4, padx=10, pady=5, sticky='e')
        self.purchases_price_entry = ttk.Entry(items_frame, width=10)
        self.purchases_price_entry.grid(row=0, column=5, padx=10, pady=5)
        
        ttk.Button(items_frame, text="Add Item", command=self.add_purchases_item).grid(row=0, column=6, padx=10, pady=5)
        
        # Invoice items table
        items_table_frame = ttk.Frame(self.purchases_tab)
        items_table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(items_table_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.purchases_items_tree = ttk.Treeview(
            items_table_frame,
            yscrollcommand=scrollbar.set,
            selectmode='browse',
            height=8
        )
        self.purchases_items_tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.purchases_items_tree.yview)
        
        columns = ("Product Code", "Product Name", "Quantity", "Price", "Total")
        self.purchases_items_tree['columns'] = columns
        self.purchases_items_tree['show'] = 'headings'
        
        for col in columns:
            self.purchases_items_tree.heading(col, text=col)
            self.purchases_items_tree.column(col, width=120)
        
        # Invoice totals frame
        totals_frame = ttk.LabelFrame(self.purchases_tab, text="Invoice Totals")
        totals_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(totals_frame, text="Total:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.purchases_total_label = ttk.Label(totals_frame, text="0.00", font=('Arial', 12, 'bold'))
        self.purchases_total_label.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(totals_frame, text="Discount:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.purchases_discount_entry = ttk.Entry(totals_frame, width=15)
        self.purchases_discount_entry.grid(row=1, column=1, padx=10, pady=5)
        self.purchases_discount_entry.insert(0, "0")
        
        ttk.Label(totals_frame, text="Net Total:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.purchases_net_label = ttk.Label(totals_frame, text="0.00", font=('Arial', 14, 'bold'), foreground='blue')
        self.purchases_net_label.grid(row=2, column=1, padx=10, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(self.purchases_tab)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="Save Invoice", command=self.save_purchases_invoice).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="New Invoice", command=self.clear_purchases_form).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Delete Item", command=self.delete_purchases_item).pack(side='left', padx=5)
    
    def create_inventory_tab(self):
        """Create inventory tab"""
        self.inventory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_tab, text="Inventory")
        
        # Search frame
        search_frame = ttk.LabelFrame(self.inventory_tab, text="Search")
        search_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(search_frame, text="Product:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.inventory_search_combo = ttk.Combobox(search_frame, width=30, state='readonly')
        self.inventory_search_combo.grid(row=0, column=1, padx=10, pady=5)
        self.load_products_combo_inventory()
        
        ttk.Button(search_frame, text="Show Stock", command=self.show_inventory).grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(search_frame, text="Show All", command=self.show_all_inventory).grid(row=0, column=3, padx=10, pady=5)
        
        # Inventory table
        table_frame = ttk.LabelFrame(self.inventory_tab, text="Inventory Status")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.inventory_tree = ttk.Treeview(
            table_frame,
            yscrollcommand=scrollbar.set,
            selectmode='browse'
        )
        self.inventory_tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.inventory_tree.yview)
        
        columns = ("Product Code", "Product Name", "Unit", "In", "Out", "Balance", "Min Limit", "Status")
        self.inventory_tree['columns'] = columns
        self.inventory_tree['show'] = 'headings'
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=120)
        
        # Load all inventory
        self.show_all_inventory()
    
    def create_reports_tab(self):
        """Create reports tab"""
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports")
        
        # Report selection frame
        selection_frame = ttk.LabelFrame(self.reports_tab, text="Select Report")
        selection_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(selection_frame, text="Report Type:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        
        self.report_type = tk.StringVar()
        reports = [
            ("Daily Sales", "sales_daily"),
            ("Monthly Sales", "sales_monthly"),
            ("Top Customers", "top_customers"),
            ("Low Stock", "low_stock"),
            ("Out of Stock", "out_of_stock")
        ]
        
        report_combo = ttk.Combobox(selection_frame, textvariable=self.report_type, width=30, state='readonly')
        report_combo['values'] = [name for name, _ in reports]
        report_combo.grid(row=0, column=1, padx=10, pady=5)
        report_combo.current(0)
        
        ttk.Button(selection_frame, text="Generate Report", command=self.generate_report).grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(selection_frame, text="Export", command=self.export_report).grid(row=0, column=3, padx=10, pady=5)
        
        # Report display frame
        display_frame = ttk.LabelFrame(self.reports_tab, text="Report Results")
        display_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(display_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.report_tree = ttk.Treeview(
            display_frame,
            yscrollcommand=scrollbar.set,
            selectmode='browse'
        )
        self.report_tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.report_tree.yview)
    
    # ===== Customer Functions =====
    
    def add_customer(self):
        """Add new customer"""
        try:
            data = {key: entry.get() for key, entry in self.customer_entries.items()}
            
            if not data['customer_code'] or not data['customer_name']:
                messagebox.showerror("Error", "Please enter customer code and name")
                return
            
            self.cursor.execute('''
                INSERT INTO customers (customer_code, customer_name, phone, address, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['customer_code'], data['customer_name'], data['phone'], 
                  data['address'], data['email']))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Customer added successfully")
            self.clear_customer_fields()
            self.load_customers()
            self.load_customers_combo()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This customer code already exists")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def edit_customer(self):
        """Edit selected customer"""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to edit")
            return
        
        try:
            data = {key: entry.get() for key, entry in self.customer_entries.items()}
            
            if not data['customer_code'] or not data['customer_name']:
                messagebox.showerror("Error", "Please enter customer code and name")
                return
            
            self.cursor.execute('''
                UPDATE customers 
                SET customer_name=?, phone=?, address=?, email=?
                WHERE customer_code=?
            ''', (data['customer_name'], data['phone'], data['address'], 
                  data['email'], data['customer_code']))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Customer updated successfully")
            self.clear_customer_fields()
            self.load_customers()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_customer(self):
        """Delete selected customer"""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to delete")
            return
        
        result = messagebox.askyesno("Confirm", "Are you sure you want to delete this customer?")
        if not result:
            return
        
        try:
            customer_code = self.customers_tree.item(selected[0])['values'][0]
            
            self.cursor.execute("DELETE FROM customers WHERE customer_code=?", (customer_code,))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Customer deleted successfully")
            self.clear_customer_fields()
            self.load_customers()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_customer_fields(self):
        """Clear all customer input fields"""
        for entry in self.customer_entries.values():
            entry.delete(0, tk.END)
    
    def on_customer_select(self, event):
        """Handle customer row selection"""
        selected = self.customers_tree.selection()
        if selected:
            values = self.customers_tree.item(selected[0])['values']
            fields = ['customer_code', 'customer_name', 'phone', 'address', 'email']
            
            for i, field in enumerate(fields):
                self.customer_entries[field].delete(0, tk.END)
                self.customer_entries[field].insert(0, values[i])
    
    def load_customers(self):
        """Load customers data into table"""
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        self.cursor.execute("SELECT * FROM customers ORDER BY customer_code")
        rows = self.cursor.fetchall()
        
        for row in rows:
            self.customers_tree.insert('', 'end', values=row)
    
    # ===== Supplier Functions =====
    
    def add_supplier(self):
        """Add new supplier"""
        try:
            data = {key: entry.get() for key, entry in self.supplier_entries.items()}
            
            if not data['supplier_code'] or not data['supplier_name']:
                messagebox.showerror("Error", "Please enter supplier code and name")
                return
            
            self.cursor.execute('''
                INSERT INTO suppliers (supplier_code, supplier_name, phone, address, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['supplier_code'], data['supplier_name'], data['phone'], 
                  data['address'], data['email']))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Supplier added successfully")
            self.clear_supplier_fields()
            self.load_suppliers()
            self.load_suppliers_combo()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This supplier code already exists")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def edit_supplier(self):
        """Edit selected supplier"""
        selected = self.suppliers_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a supplier to edit")
            return
        
        try:
            data = {key: entry.get() for key, entry in self.supplier_entries.items()}
            
            if not data['supplier_code'] or not data['supplier_name']:
                messagebox.showerror("Error", "Please enter supplier code and name")
                return
            
            self.cursor.execute('''
                UPDATE suppliers 
                SET supplier_name=?, phone=?, address=?, email=?
                WHERE supplier_code=?
            ''', (data['supplier_name'], data['phone'], data['address'], 
                  data['email'], data['supplier_code']))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Supplier updated successfully")
            self.clear_supplier_fields()
            self.load_suppliers()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_supplier(self):
        """Delete selected supplier"""
        selected = self.suppliers_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a supplier to delete")
            return
        
        result = messagebox.askyesno("Confirm", "Are you sure you want to delete this supplier?")
        if not result:
            return
        
        try:
            supplier_code = self.suppliers_tree.item(selected[0])['values'][0]
            
            self.cursor.execute("DELETE FROM suppliers WHERE supplier_code=?", (supplier_code,))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Supplier deleted successfully")
            self.clear_supplier_fields()
            self.load_suppliers()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_supplier_fields(self):
        """Clear all supplier input fields"""
        for entry in self.supplier_entries.values():
            entry.delete(0, tk.END)
    
    def on_supplier_select(self, event):
        """Handle supplier row selection"""
        selected = self.suppliers_tree.selection()
        if selected:
            values = self.suppliers_tree.item(selected[0])['values']
            fields = ['supplier_code', 'supplier_name', 'phone', 'address', 'email']
            
            for i, field in enumerate(fields):
                self.supplier_entries[field].delete(0, tk.END)
                self.supplier_entries[field].insert(0, values[i])
    
    def load_suppliers(self):
        """Load suppliers data into table"""
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        
        self.cursor.execute("SELECT * FROM suppliers ORDER BY supplier_code")
        rows = self.cursor.fetchall()
        
        for row in rows:
            self.suppliers_tree.insert('', 'end', values=row)
    
    # ===== Product Functions =====
    
    def add_product(self):
        """Add new product"""
        try:
            data = {key: entry.get() for key, entry in self.product_entries.items()}
            
            if not data['product_code'] or not data['product_name']:
                messagebox.showerror("Error", "Please enter product code and name")
                return
            
            self.cursor.execute('''
                INSERT INTO products (product_code, product_name, unit_of_measure, 
                                    purchase_price, sale_price, minimum_limit)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (data['product_code'], data['product_name'], data['unit_of_measure'],
                  float(data['purchase_price'] or 0), float(data['sale_price'] or 0),
                  int(data['minimum_limit'] or 10)))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Product added successfully")
            self.clear_product_fields()
            self.load_products()
            self.load_products_combo()
            self.load_products_combo_purchases()
            self.load_products_combo_inventory()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This product code already exists")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def edit_product(self):
        """Edit selected product"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to edit")
            return
        
        try:
            data = {key: entry.get() for key, entry in self.product_entries.items()}
            
            if not data['product_code'] or not data['product_name']:
                messagebox.showerror("Error", "Please enter product code and name")
                return
            
            self.cursor.execute('''
                UPDATE products 
                SET product_name=?, unit_of_measure=?, purchase_price=?, 
                    sale_price=?, minimum_limit=?
                WHERE product_code=?
            ''', (data['product_name'], data['unit_of_measure'],
                  float(data['purchase_price'] or 0), float(data['sale_price'] or 0),
                  int(data['minimum_limit'] or 10), data['product_code']))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Product updated successfully")
            self.clear_product_fields()
            self.load_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_product(self):
        """Delete selected product"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to delete")
            return
        
        result = messagebox.askyesno("Confirm", "Are you sure you want to delete this product?")
        if not result:
            return
        
        try:
            product_code = self.products_tree.item(selected[0])['values'][0]
            
            self.cursor.execute("DELETE FROM products WHERE product_code=?", (product_code,))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Product deleted successfully")
            self.clear_product_fields()
            self.load_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_product_fields(self):
        """Clear all product input fields"""
        for entry in self.product_entries.values():
            entry.delete(0, tk.END)
    
    def on_product_select(self, event):
        """Handle product row selection"""
        selected = self.products_tree.selection()
        if selected:
            values = self.products_tree.item(selected[0])['values']
            fields = ['product_code', 'product_name', 'unit_of_measure', 
                     'purchase_price', 'sale_price', 'minimum_limit']
            
            for i, field in enumerate(fields):
                self.product_entries[field].delete(0, tk.END)
                self.product_entries[field].insert(0, values[i])
    
    def load_products(self):
        """Load products data into table"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        self.cursor.execute("SELECT * FROM products ORDER BY product_code")
        rows = self.cursor.fetchall()
        
        for row in rows:
            self.products_tree.insert('', 'end', values=row)
    
    # ===== Sales Functions =====
    
    def load_customers_combo(self):
        """Load customers into combo box"""
        self.cursor.execute("SELECT customer_code, customer_name FROM customers ORDER BY customer_name")
        customers = self.cursor.fetchall()
        self.sales_customer_combo['values'] = [f"{code} - {name}" for code, name in customers]
    
    def load_products_combo(self):
        """Load products into sales combo box"""
        self.cursor.execute("SELECT product_code, product_name FROM products ORDER BY product_name")
        products = self.cursor.fetchall()
        self.sales_product_combo['values'] = [f"{code} - {name}" for code, name in products]
    
    def on_sales_product_select(self, event):
        """Auto-fill sale price when product is selected"""
        selection = self.sales_product_combo.get()
        if selection:
            product_code = selection.split(' - ')[0]
            self.cursor.execute("SELECT sale_price FROM products WHERE product_code=?", (product_code,))
            result = self.cursor.fetchone()
            if result:
                self.sales_price_entry.delete(0, tk.END)
                self.sales_price_entry.insert(0, result[0])
    
    def add_sales_item(self):
        """Add item to sales invoice"""
        try:
            product = self.sales_product_combo.get()
            quantity = self.sales_quantity_entry.get()
            price = self.sales_price_entry.get()
            
            if not product or not quantity or not price:
                messagebox.showerror("Error", "Please enter all item information")
                return
            
            product_code = product.split(' - ')[0]
            product_name = product.split(' - ')[1]
            quantity = int(quantity)
            price = float(price)
            total = quantity * price
            
            self.sales_items_tree.insert('', 'end', values=(product_code, product_name, quantity, price, total))
            
            self.sales_quantity_entry.delete(0, tk.END)
            self.sales_price_entry.delete(0, tk.END)
            
            self.calculate_sales_totals()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_sales_item(self):
        """Delete selected item from sales invoice"""
        selected = self.sales_items_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        self.sales_items_tree.delete(selected[0])
        self.calculate_sales_totals()
    
    def calculate_sales_totals(self):
        """Calculate invoice totals"""
        total = 0
        for item in self.sales_items_tree.get_children():
            values = self.sales_items_tree.item(item)['values']
            total += float(values[4])
        
        discount = float(self.sales_discount_entry.get() or 0)
        net = total - discount
        
        self.sales_total_label.config(text=f"{total:.2f}")
        self.sales_net_label.config(text=f"{net:.2f}")
    
    def save_sales_invoice(self):
        """Save sales invoice"""
        try:
            invoice_number = self.sales_invoice_entry.get()
            invoice_date = self.sales_date_entry.get()
            customer = self.sales_customer_combo.get()
            
            if not invoice_number or not customer:
                messagebox.showerror("Error", "Please enter invoice number and select customer")
                return
            
            if len(self.sales_items_tree.get_children()) == 0:
                messagebox.showerror("Error", "Please add at least one item to the invoice")
                return
            
            customer_code = customer.split(' - ')[0]
            total = float(self.sales_total_label.cget('text'))
            discount = float(self.sales_discount_entry.get() or 0)
            net = total - discount
            
            # Save invoice header
            self.cursor.execute('''
                INSERT INTO sales (invoice_number, invoice_date, customer_code, 
                                 total_invoice, discount, net_invoice, invoice_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (invoice_number, invoice_date, customer_code, total, discount, net, 'open'))
            
            # Save invoice items
            for item in self.sales_items_tree.get_children():
                values = self.sales_items_tree.item(item)['values']
                product_code = values[0]
                quantity = int(values[2])
                price = float(values[3])
                item_total = float(values[4])
                
                self.cursor.execute('''
                    INSERT INTO sales_details (invoice_number, product_code, quantity, price, total)
                    VALUES (?, ?, ?, ?, ?)
                ''', (invoice_number, product_code, quantity, price, item_total))
                
                # Update inventory
                self.cursor.execute('''
                    INSERT INTO inventory (product_code, movement, quantity, reference)
                    VALUES (?, ?, ?, ?)
                ''', (product_code, 'out', quantity, invoice_number))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Sales invoice saved successfully")
            self.clear_sales_form()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This invoice number already exists")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_sales_form(self):
        """Clear sales form"""
        self.sales_invoice_entry.delete(0, tk.END)
        self.sales_date_entry.delete(0, tk.END)
        self.sales_date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.sales_customer_combo.set('')
        self.sales_product_combo.set('')
        self.sales_quantity_entry.delete(0, tk.END)
        self.sales_price_entry.delete(0, tk.END)
        self.sales_discount_entry.delete(0, tk.END)
        self.sales_discount_entry.insert(0, "0")
        
        for item in self.sales_items_tree.get_children():
            self.sales_items_tree.delete(item)
        
        self.sales_total_label.config(text="0.00")
        self.sales_net_label.config(text="0.00")
    
    # ===== Purchases Functions =====
    
    def load_suppliers_combo(self):
        """Load suppliers into combo box"""
        self.cursor.execute("SELECT supplier_code, supplier_name FROM suppliers ORDER BY supplier_name")
        suppliers = self.cursor.fetchall()
        self.purchases_supplier_combo['values'] = [f"{code} - {name}" for code, name in suppliers]
    
    def load_products_combo_purchases(self):
        """Load products into purchases combo box"""
        self.cursor.execute("SELECT product_code, product_name FROM products ORDER BY product_name")
        products = self.cursor.fetchall()
        self.purchases_product_combo['values'] = [f"{code} - {name}" for code, name in products]
    
    def on_purchases_product_select(self, event):
        """Auto-fill purchase price when product is selected"""
        selection = self.purchases_product_combo.get()
        if selection:
            product_code = selection.split(' - ')[0]
            self.cursor.execute("SELECT purchase_price FROM products WHERE product_code=?", (product_code,))
            result = self.cursor.fetchone()
            if result:
                self.purchases_price_entry.delete(0, tk.END)
                self.purchases_price_entry.insert(0, result[0])
    
    def add_purchases_item(self):
        """Add item to purchase invoice"""
        try:
            product = self.purchases_product_combo.get()
            quantity = self.purchases_quantity_entry.get()
            price = self.purchases_price_entry.get()
            
            if not product or not quantity or not price:
                messagebox.showerror("Error", "Please enter all item information")
                return
            
            product_code = product.split(' - ')[0]
            product_name = product.split(' - ')[1]
            quantity = int(quantity)
            price = float(price)
            total = quantity * price
            
            self.purchases_items_tree.insert('', 'end', values=(product_code, product_name, quantity, price, total))
            
            self.purchases_quantity_entry.delete(0, tk.END)
            self.purchases_price_entry.delete(0, tk.END)
            
            self.calculate_purchases_totals()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_purchases_item(self):
        """Delete selected item from purchase invoice"""
        selected = self.purchases_items_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        self.purchases_items_tree.delete(selected[0])
        self.calculate_purchases_totals()
    
    def calculate_purchases_totals(self):
        """Calculate invoice totals"""
        total = 0
        for item in self.purchases_items_tree.get_children():
            values = self.purchases_items_tree.item(item)['values']
            total += float(values[4])
        
        discount = float(self.purchases_discount_entry.get() or 0)
        net = total - discount
        
        self.purchases_total_label.config(text=f"{total:.2f}")
        self.purchases_net_label.config(text=f"{net:.2f}")
    
    def save_purchases_invoice(self):
        """Save purchase invoice"""
        try:
            invoice_number = self.purchases_invoice_entry.get()
            invoice_date = self.purchases_date_entry.get()
            supplier = self.purchases_supplier_combo.get()
            
            if not invoice_number or not supplier:
                messagebox.showerror("Error", "Please enter invoice number and select supplier")
                return
            
            if len(self.purchases_items_tree.get_children()) == 0:
                messagebox.showerror("Error", "Please add at least one item to the invoice")
                return
            
            supplier_code = supplier.split(' - ')[0]
            total = float(self.purchases_total_label.cget('text'))
            discount = float(self.purchases_discount_entry.get() or 0)
            net = total - discount
            
            # Save invoice header
            self.cursor.execute('''
                INSERT INTO purchases (invoice_number, invoice_date, supplier_code, 
                                     total_invoice, discount, net_invoice, invoice_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (invoice_number, invoice_date, supplier_code, total, discount, net, 'open'))
            
            # Save invoice items
            for item in self.purchases_items_tree.get_children():
                values = self.purchases_items_tree.item(item)['values']
                product_code = values[0]
                quantity = int(values[2])
                price = float(values[3])
                item_total = float(values[4])
                
                self.cursor.execute('''
                    INSERT INTO purchase_details (invoice_number, product_code, quantity, price, total)
                    VALUES (?, ?, ?, ?, ?)
                ''', (invoice_number, product_code, quantity, price, item_total))
                
                # Update inventory
                self.cursor.execute('''
                    INSERT INTO inventory (product_code, movement, quantity, reference)
                    VALUES (?, ?, ?, ?)
                ''', (product_code, 'in', quantity, invoice_number))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Purchase invoice saved successfully")
            self.clear_purchases_form()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This invoice number already exists")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_purchases_form(self):
        """Clear purchases form"""
        self.purchases_invoice_entry.delete(0, tk.END)
        self.purchases_date_entry.delete(0, tk.END)
        self.purchases_date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.purchases_supplier_combo.set('')
        self.purchases_product_combo.set('')
        self.purchases_quantity_entry.delete(0, tk.END)
        self.purchases_price_entry.delete(0, tk.END)
        self.purchases_discount_entry.delete(0, tk.END)
        self.purchases_discount_entry.insert(0, "0")
        
        for item in self.purchases_items_tree.get_children():
            self.purchases_items_tree.delete(item)
        
        self.purchases_total_label.config(text="0.00")
        self.purchases_net_label.config(text="0.00")
    
    # ===== Inventory Functions =====
    
    def load_products_combo_inventory(self):
        """Load products into inventory combo box"""
        self.cursor.execute("SELECT product_code, product_name FROM products ORDER BY product_name")
        products = self.cursor.fetchall()
        self.inventory_search_combo['values'] = [f"{code} - {name}" for code, name in products]
    
    def show_inventory(self):
        """Show inventory for selected product"""
        selection = self.inventory_search_combo.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product")
            return
        
        product_code = selection.split(' - ')[0]
        
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        self.cursor.execute('''
            SELECT 
                p.product_code,
                p.product_name,
                p.unit_of_measure,
                COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'), 0) as in_quantity,
                COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'), 0) as out_quantity,
                (COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'), 0) -
                 COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'), 0)) as balance,
                p.minimum_limit,
                CASE 
                    WHEN (COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'), 0) -
                          COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'), 0)) <= 0 THEN 'Out of Stock'
                    WHEN (COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'), 0) -
                          COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'), 0)) < p.minimum_limit THEN 'Low'
                    ELSE 'Normal'
                END as status
            FROM products p
            WHERE p.product_code = ?
        ''', (product_code,))
        
        row = self.cursor.fetchone()
        if row:
            self.inventory_tree.insert('', 'end', values=row)
    
    def show_all_inventory(self):
        """Show all inventory"""
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        self.cursor.execute('''
            SELECT 
                p.product_code,
                p.product_name,
                p.unit_of_measure,
                COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'), 0) as in_quantity,
                COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'), 0) as out_quantity,
                (COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'), 0) -
                 COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'), 0)) as balance,
                p.minimum_limit,
                CASE 
                    WHEN (COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'), 0) -
                          COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'), 0)) <= 0 THEN 'Out of Stock'
                    WHEN (COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'), 0) -
                          COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'), 0)) < p.minimum_limit THEN 'Low'
                    ELSE 'Normal'
                END as status
            FROM products p
            ORDER BY p.product_code
        ''')
        
        rows = self.cursor.fetchall()
        for row in rows:
            self.inventory_tree.insert('', 'end', values=row)
    
    # ===== Reports Functions =====
    
    def generate_report(self):
        """Generate selected report"""
        # Clear previous report
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        report_type = self.report_type.get()
        
        if report_type == 'Daily Sales':
            self.generate_daily_sales_report()
        elif report_type == 'Monthly Sales':
            self.generate_monthly_sales_report()
        elif report_type == 'Top Customers':
            self.generate_top_customers_report()
        elif report_type == 'Low Stock':
            self.generate_low_stock_report()
        elif report_type == 'Out of Stock':
            self.generate_out_of_stock_report()
    
    def generate_daily_sales_report(self):
        """Generate daily sales report"""
        self.cursor.execute('''
            SELECT 
                s.invoice_number,
                s.invoice_date,
                c.customer_name,
                s.total_invoice,
                s.discount,
                s.net_invoice,
                s.invoice_status
            FROM sales s
            JOIN customers c ON s.customer_code = c.customer_code
            WHERE DATE(s.invoice_date) = DATE('now')
            ORDER BY s.invoice_number DESC
        ''')
        
        report_data = self.cursor.fetchall()
        
        # Setup report columns
        columns = ("Invoice Number", "Date", "Customer", "Total", "Discount", "Net Total", "Status")
        self.report_tree['columns'] = columns
        
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=120)
        
        # Fill data
        for row in report_data:
            self.report_tree.insert('', 'end', values=row)
    
    def generate_monthly_sales_report(self):
        """Generate monthly sales report"""
        self.cursor.execute('''
            SELECT 
                strftime('%Y-%m', s.invoice_date) as month,
                COUNT(*) as invoice_count,
                SUM(s.total_invoice) as total,
                SUM(s.discount) as discount,
                SUM(s.net_invoice) as net_total
            FROM sales s
            GROUP BY strftime('%Y-%m', s.invoice_date)
            ORDER BY month DESC
        ''')
        
        report_data = self.cursor.fetchall()
        
        # Setup report columns
        columns = ("Month", "Invoice Count", "Total", "Discount", "Net Total")
        self.report_tree['columns'] = columns
        
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=150)
        
        # Fill data
        for row in report_data:
            self.report_tree.insert('', 'end', values=row)
    
    def generate_top_customers_report(self):
        """Generate top customers report"""
        self.cursor.execute('''
            SELECT 
                c.customer_name,
                COUNT(s.invoice_number) as invoice_count,
                SUM(s.net_invoice) as total_purchases
            FROM customers c
            LEFT JOIN sales s ON c.customer_code = s.customer_code
            GROUP BY c.customer_code
            HAVING total_purchases > 0
            ORDER BY total_purchases DESC
            LIMIT 20
        ''')
        
        report_data = self.cursor.fetchall()
        
        # Setup report columns
        columns = ("Customer Name", "Invoice Count", "Total Purchases")
        self.report_tree['columns'] = columns
        
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=200)
        
        # Fill data
        for row in report_data:
            self.report_tree.insert('', 'end', values=row)
    
    def generate_low_stock_report(self):
        """Generate low stock report"""
        self.cursor.execute('''
            SELECT 
                p.product_name,
                (COALESCE((
                    SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'
                ), 0) -
                COALESCE((
                    SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'
                ), 0)) as balance,
                p.minimum_limit,
                CASE 
                    WHEN (COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'
                    ), 0) -
                    COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'
                    ), 0)) <= 0 THEN 'Out of Stock'
                    WHEN (COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'
                    ), 0) -
                    COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'
                    ), 0)) < p.minimum_limit THEN 'Low'
                    ELSE 'Normal'
                END as status
            FROM products p
            WHERE (COALESCE((
                SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'
            ), 0) -
            COALESCE((
                SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'
            ), 0)) < p.minimum_limit
            ORDER BY balance ASC
        ''')
        
        report_data = self.cursor.fetchall()
        
        # Setup report columns
        columns = ("Product Name", "Current Balance", "Minimum Limit", "Status")
        self.report_tree['columns'] = columns
        
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=150)
        
        # Fill data
        for row in report_data:
            self.report_tree.insert('', 'end', values=row)
    
    def generate_out_of_stock_report(self):
        """Generate out of stock report"""
        self.cursor.execute('''
            SELECT 
                p.product_name,
                (COALESCE((
                    SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'
                ), 0) -
                COALESCE((
                    SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'
                ), 0)) as balance,
                p.minimum_limit,
                CASE 
                    WHEN (COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'
                    ), 0) -
                    COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'
                    ), 0)) <= 0 THEN 'Out of Stock'
                    WHEN (COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'
                    ), 0) -
                    COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'
                    ), 0)) < p.minimum_limit THEN 'Low'
                    ELSE 'Normal'
                END as status
            FROM products p
            WHERE (COALESCE((
                SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'
            ), 0) -
            COALESCE((
                SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'
            ), 0)) < p.minimum_limit
            ORDER BY balance ASC
        ''')
        
        report_data = self.cursor.fetchall()
        
        # Setup report columns
        columns = ("Product Name", "Current Balance", "Minimum Limit", "Status")
        self.report_tree['columns'] = columns
        
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=150)
        
        # Fill data
        for row in report_data:
            self.report_tree.insert('', 'end', values=row)
    
    # ===== Dashboard Functions =====
    
    def get_total_sales(self):
        """Get total sales"""
        try:
            self.cursor.execute("SELECT SUM(net_invoice) FROM sales WHERE DATE(invoice_date) = DATE('now')")
            result = self.cursor.fetchone()[0]
            return f"{result or 0:.2f}"
        except:
            return "0.00"
    
    def get_total_purchases(self):
        """Get total purchases"""
        try:
            self.cursor.execute("SELECT SUM(net_invoice) FROM purchases WHERE DATE(invoice_date) = DATE('now')")
            result = self.cursor.fetchone()[0]
            return f"{result or 0:.2f}"
        except:
            return "0.00"
    
    def get_net_profit(self):
        """Get net profit"""
        try:
            sales = float(self.get_total_sales())
            purchases = float(self.get_total_purchases())
            profit = sales - purchases
            return f"{profit:.2f}"
        except:
            return "0.00"
    
    def get_customers_count(self):
        """Get customer count"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM customers")
            return self.cursor.fetchone()[0]
        except:
            return "0"
    
    def get_products_count(self):
        """Get product count"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM products")
            return self.cursor.fetchone()[0]
        except:
            return "0"
    
    def get_inventory_value(self):
        """Get inventory value"""
        try:
            self.cursor.execute('''
                SELECT SUM(
                    (COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'
                    ), 0) -
                    COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'
                    ), 0)) * p.purchase_price
                )
                FROM products p
            ''')
            result = self.cursor.fetchone()[0]
            return f"{result or 0:.2f}"
        except:
            return "0.00"
    
    def get_monthly_sales(self):
        """Get monthly sales"""
        # Dummy for demonstration - can be developed
        return pd.DataFrame({
            'month': ['January', 'February', 'March', 'April', 'May', 'June'],
            'sales': [15000, 18000, 22000, 19000, 25000, 28000]
        })
    
    def get_top_customers(self):
        """Get top customers"""
        # Dummy for demonstration - can be developed
        return pd.DataFrame({
            'customer': ['Customer 1', 'Customer 2', 'Customer 3', 'Customer 4', 'Customer 5'],
            'sales': [5000, 4500, 4000, 3500, 3000]
        })
    
    def get_inventory_status(self):
        """Get inventory status"""
        # Dummy for demonstration - can be developed
        return pd.DataFrame({
            'status': ['Normal', 'Low', 'Out of Stock'],
            'count': [50, 15, 5]
        })
    
    def get_sales_purchases_comparison(self):
        """Get sales vs purchases comparison"""
        # Dummy for demonstration - can be developed
        return pd.DataFrame({
            'month': ['January', 'February', 'March', 'April', 'May', 'June'],
            'sales': [15000, 18000, 22000, 19000, 25000, 28000],
            'purchases': [10000, 12000, 15000, 13000, 18000, 20000]
        })
    
    # ===== Helper Functions =====
    
    def validate_number(self, value):
        """Validate that value is numeric"""
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def export_data(self):
        """Export data to Excel"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Export all tables
                tables = {
                    'Customers': "SELECT * FROM customers",
                    'Suppliers': "SELECT * FROM suppliers",
                    'Products': "SELECT * FROM products",
                    'Sales': "SELECT * FROM sales",
                    'Sales_Details': "SELECT * FROM sales_details",
                    'Purchases': "SELECT * FROM purchases",
                    'Inventory': "SELECT * FROM inventory"
                }
                
                for sheet_name, query in tables.items():
                    df = pd.read_sql_query(query, self.conn)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            messagebox.showinfo("Success", f"Data exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An export error occurred: {str(e)}")
    
    def export_report(self):
        """Export report to Excel"""
        # Can be developed in future versions
        messagebox.showinfo("Export", "Export functionality will be developed in future versions")
    
    def show_sales_report(self):
        """Show sales report"""
        self.notebook.select(self.reports_tab)
        self.report_type.set('Daily Sales')
        self.generate_report()
    
    def show_inventory_report(self):
        """Show inventory report"""
        self.notebook.select(self.reports_tab)
        self.report_type.set('Low Stock')
        self.generate_report()
    
    def show_customers_report(self):
        """Show customers report"""
        self.notebook.select(self.reports_tab)
        self.report_type.set('Top Customers')
        self.generate_report()
    
    def show_suppliers_report(self):
        """Show suppliers report"""
        # Can be developed in future versions
        messagebox.showinfo("Reports", "This report will be developed in future versions")
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main function"""
    root = tk.Tk()
    app = ERPSystem(root)
    
    # Interface settings
    root.iconbitmap(default='')  # Can add an icon
    root.resizable(True, True)
    
    # Run application
    root.mainloop()

if __name__ == "__main__":
    main()