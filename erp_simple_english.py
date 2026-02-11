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
        self.root.title("Integrated ERP System - Simplified Version")
        self.root.geometry("1200x700")
        
        # Setup colors
        self.setup_colors()
        
        # Create database
        self.create_database()
        
        # Create user interface
        self.setup_ui()
        
    def setup_colors(self):
        """Setup system colors"""
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50'
        }
        
    def create_database(self):
        """Create database and tables"""
        self.conn = sqlite3.connect('erp_system.db', check_same_thread=False)
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
                product_code INTEGER PRIMARY KEY AUTOINCREMENT,
                Category TEXT ,
                product_name TEXT NOT NULL,
                Quantitee TEXT,
                purchase_price REAL DEFAULT 0,
                selling_price REAL DEFAULT 0,
                minimum_limit INTEGER DEFAULT 10,
                date_added DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        # Inventory table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                movement TEXT,
                quantity INTEGER,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                reference TEXT,
                FOREIGN KEY (product_name) REFERENCES products(product_name)
            )
        ''')
        
        # Sales table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                invoice_number TEXT PRIMARY KEY,
                invoice_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                customer_code TEXT,
                invoice_total REAL DEFAULT 0,
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
        
        # Expenses table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                amount REAL,
                expense_date DATE DEFAULT CURRENT_DATE,
                notes TEXT
            )
        ''')
        
        self.conn.commit()
        
        # Add sample data if tables are empty
        self.add_sample_data()
    
    def add_sample_data(self):
        """Add sample data for testing"""
        try:
            # Check if customers exist
            self.cursor.execute("SELECT COUNT(*) FROM customers")
            if self.cursor.fetchone()[0] == 0:
                # Add sample customers
                customers = [
                    ('CUS-0001', 'Advanced Technology Company', '0123456789', 'Riyadh - Al Olaya', 'info@tech.com'),
                    ('CUS-0002', 'Success Trading Establishment', '0112233445', 'Jeddah - Al Sharafiya', 'sales@najah.com'),
                    ('CUS-0003', 'Al-Amani Stores', '0109876543', 'Dammam - Al Rakah', 'amani@store.com')
                ]
                self.cursor.executemany('''
                    INSERT INTO customers (customer_code, customer_name, phone, address, email)
                    VALUES (?, ?, ?, ?, ?)
                ''', customers)
                
                # Add sample products
                products = [
                    (1, 'pc', 'Dell Laptop', 'unit', 2500, 3200, 5),
                    (2, 'pc', 'HP Printer', 'unit', 800, 1200, 10),
                    (3, 'pc', 'Wireless Mouse', 'piece', 50, 80, 50),
                    (4, 'pc', 'Keyboard', 'piece', 70, 100, 30),
                    (5, 'pc', '24 Inch Monitor', 'unit', 900, 1400, 8)
                ]
                self.cursor.executemany('''
                    INSERT INTO products (product_code, Category, product_name, Quantitee, purchase_price, selling_price, minimum_limit)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', products)
                
                self.conn.commit()
                print("Sample data added successfully")
        except Exception as e:
            print(f"Error adding sample data: {e}")
    
    def setup_ui(self):
        """Create main user interface"""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import CSV", command=self.import_csv)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_command(label="Backup", command=self.backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Calculate Balance", command=self.calculate_balance)
        tools_menu.add_command(label="Inventory Count", command=self.inventory_count)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="About System", command=self.about_system)
        
        # Create Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_customers_tab()
        self.create_products_tab()
        self.create_sales_tab()
        self.create_inventory_tab()
        self.create_reports_tab()
        self.create_expenses_tab()
        
        # Update data first time
        self.update_dashboard()
        
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="📊 Dashboard")
        
        # Title frame
        title_frame = tk.Frame(self.dashboard_tab, bg=self.colors['primary'], height=60)
        title_frame.pack(fill='x', padx=10, pady=(10, 0))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="Main Dashboard", 
                              font=('Arial', 16, 'bold'), 
                              fg='white', bg=self.colors['primary'])
        title_label.pack(pady=20)
        
        # Metrics frame
        metrics_frame = tk.Frame(self.dashboard_tab, bg='white')
        metrics_frame.pack(fill='x', padx=10, pady=10)
        
        # Key performance indicators
        self.metrics_vars = {
            'total_sales': tk.StringVar(value="0.00"),
            'total_customers': tk.StringVar(value="0"),
            'total_products': tk.StringVar(value="0"),
            'inventory_value': tk.StringVar(value="0.00")
        }
        
        metrics = [
            ("Total Sales", self.metrics_vars['total_sales'], self.colors['success']),
            ("Customers", self.metrics_vars['total_customers'], self.colors['secondary']),
            ("Products", self.metrics_vars['total_products'], self.colors['warning']),
            ("Inventory Value", self.metrics_vars['inventory_value'], self.colors['primary'])
        ]
        
        for i, (label, var, color) in enumerate(metrics):
            metric_frame = tk.Frame(metrics_frame, bg=color, relief='raised', bd=2)
            metric_frame.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            
            tk.Label(metric_frame, text=label, font=('Arial', 10), 
                    bg=color, fg='white').pack(pady=(10, 5))
            tk.Label(metric_frame, textvariable=var, font=('Arial', 18, 'bold'),
                    bg=color, fg='white').pack(pady=(5, 10))
        
        metrics_frame.columnconfigure([0,1,2,3], weight=1)
        
        # Quick analysis frame
        analysis_frame = tk.LabelFrame(self.dashboard_tab, text="Quick Analysis", 
                                      font=('Arial', 12, 'bold'))
        analysis_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Analysis tree
        columns = ('Analysis Type', 'Value', 'Status')
        self.analysis_tree = ttk.Treeview(analysis_frame, columns=columns, 
                                         show='headings', height=10)
        
        for col in columns:
            self.analysis_tree.heading(col, text=col)
            self.analysis_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(analysis_frame, orient='vertical', 
                                 command=self.analysis_tree.yview)
        self.analysis_tree.configure(yscrollcommand=scrollbar.set)
        
        self.analysis_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons frame
        buttons_frame = tk.Frame(self.dashboard_tab, bg='white')
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(buttons_frame, text="Refresh Data", 
                 command=self.update_dashboard,
                 bg=self.colors['primary'], fg='white',
                 font=('Arial', 10, 'bold'), padx=20, pady=10).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Quick Report",
                 command=self.quick_report,
                 bg=self.colors['secondary'], fg='white',
                 font=('Arial', 10, 'bold'), padx=20, pady=10).pack(side='left', padx=5)
    
    def create_customers_tab(self):
        """Create customers management tab"""
        self.customers_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_tab, text="👥 Customers")
        
        # Title
        title_label = tk.Label(self.customers_tab, text="Customer Management",
                              font=('Arial', 14, 'bold'), bg=self.colors['primary'],
                              fg='white', pady=15)
        title_label.pack(fill='x')
        
        # Input form
        form_frame = tk.LabelFrame(self.customers_tab, text="Customer Information",
                                  font=('Arial', 11, 'bold'), padx=10, pady=10)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        # Form fields
        fields = [
            ("Customer Code:", "customer_code"),
            ("Customer Name:", "customer_name"),
            ("Phone:", "customer_phone"),
            ("Address:", "customer_address"),
            ("Email:", "customer_email")
        ]
        
        self.customer_vars = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, font=('Arial', 10)).grid(
                row=i//2, column=(i%2)*2, sticky='e', padx=5, pady=5)
            
            var = tk.StringVar()
            self.customer_vars[key] = var
            entry = tk.Entry(form_frame, textvariable=var, width=25, font=('Arial', 10))
            entry.grid(row=i//2, column=(i%2)*2+1, sticky='w', padx=5, pady=5)
        
        # Buttons
        buttons_frame = tk.Frame(form_frame)
        buttons_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        tk.Button(buttons_frame, text="Add", command=self.add_customer,
                 bg=self.colors['success'], fg='white', width=12).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Update", command=self.update_customer,
                 bg=self.colors['warning'], fg='white', width=12).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Delete", command=self.delete_customer,
                 bg=self.colors['danger'], fg='white', width=12).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Clear", command=self.clear_customer_form,
                 bg=self.colors['secondary'], fg='white', width=12).pack(side='left', padx=5)
        
        # Customers table
        table_frame = tk.LabelFrame(self.customers_tab, text="Registered Customers",
                                   font=('Arial', 11, 'bold'))
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('Code', 'Name', 'Phone', 'Address', 'Email', 'Registration Date')
        self.customers_tree = ttk.Treeview(table_frame, columns=columns, 
                                          show='headings', height=15)
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical',
                                 command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customers_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.customers_tree.bind('<<TreeviewSelect>>', self.on_customer_select)
        
        # Load customers
        self.load_customers()
    
    def create_products_tab(self):
        """Create products management tab"""
        self.products_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.products_tab, text="📦 Products")
        
        # Title
        title_label = tk.Label(self.products_tab, text="Products & Inventory Management",
                              font=('Arial', 14, 'bold'), bg=self.colors['primary'],
                              fg='white', pady=15)
        title_label.pack(fill='x')
        
        # Input form
        form_frame = tk.LabelFrame(self.products_tab, text="Product Information",
                                  font=('Arial', 11, 'bold'), padx=10, pady=10)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        # Form fields
        fields = [
            ("Category:", "Category"),
            ("Product Name:", "product_name"),
            ("Quantitee:", "Quantitee"),
            ("Purchase Price:", "purchase_price"),
            ("Selling Price:", "selling_price"),
            ("Minimum Limit:", "minimum_limit")
        ]
        
        self.product_vars = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, font=('Arial', 10)).grid(
                row=i//2, column=(i%2)*2, sticky='e', padx=5, pady=5)
            
            var = tk.StringVar()
            self.product_vars[key] = var
            entry = tk.Entry(form_frame, textvariable=var, width=25, font=('Arial', 10))
            entry.grid(row=i//2, column=(i%2)*2+1, sticky='w', padx=5, pady=5)
        
        # Buttons
        buttons_frame = tk.Frame(form_frame)
        buttons_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        tk.Button(buttons_frame, text="Add", command=self.add_product,
                 bg=self.colors['success'], fg='white', width=12).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Update", command=self.update_product,
                 bg=self.colors['warning'], fg='white', width=12).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Delete", command=self.delete_product,
                 bg=self.colors['danger'], fg='white', width=12).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Clear", command=self.clear_product_form,
                 bg=self.colors['secondary'], fg='white', width=12).pack(side='left', padx=5)
        
        # Products table
        table_frame = tk.LabelFrame(self.products_tab, text="Available Products",
                                   font=('Arial', 11, 'bold'))
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('product_code', 'Category', 'Name', 'Quantitee', 'Purchase Price', 'Selling Price', 
                  'Min. Limit', 'Date Added')
        self.products_tree = ttk.Treeview(table_frame, columns=columns,
                                         show='headings', height=12)
        
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical',
                                 command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        self.products_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.products_tree.bind('<<TreeviewSelect>>', self.on_product_select)
        
        # Load products
        self.load_products()
    
    def create_sales_tab(self):
        """Create sales management tab"""
        self.sales_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_tab, text="💰 Sales")
        
        # Title
        title_label = tk.Label(self.sales_tab, text="Sales Management",
                              font=('Arial', 14, 'bold'), bg=self.colors['primary'],
                              fg='white', pady=15)
        title_label.pack(fill='x')
        
        # Invoice header
        header_frame = tk.LabelFrame(self.sales_tab, text="Invoice Header",
                                    font=('Arial', 11, 'bold'), padx=10, pady=10)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        # Invoice information
        self.sale_vars = {
            'invoice_number': tk.StringVar(),
            'customer_code': tk.StringVar(),
            'discount': tk.StringVar(value="0")
        }
        
        tk.Label(header_frame, text="Invoice Number:", font=('Arial', 10)).grid(
            row=0, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(header_frame, textvariable=self.sale_vars['invoice_number'],
                width=20, font=('Arial', 10)).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        tk.Label(header_frame, text="Customer:", font=('Arial', 10)).grid(
            row=0, column=2, sticky='e', padx=5, pady=5)
        
        # Customer dropdown
        self.cursor.execute("SELECT customer_name FROM customers")
        customers = self.cursor.fetchall()
        customer_list = [name[0] for  name in customers]
        
        
        self.customer_combo = ttk.Combobox(header_frame, 
                                     textvariable=self.sale_vars['customer_code'],
                                     values=customer_list, width=30, font=('Arial', 10))
        self.customer_combo.grid(row=0, column=3, sticky='w', padx=5, pady=5)
        
        tk.Label(header_frame, text="Discount:", font=('Arial', 10)).grid(
            row=1, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(header_frame, textvariable=self.sale_vars['discount'],
                width=20, font=('Arial', 10)).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Invoice items
        items_frame = tk.LabelFrame(self.sales_tab, text="Invoice Items",
                                   font=('Arial', 11, 'bold'), padx=10, pady=10)
        items_frame.pack(fill='x', padx=10, pady=10)
        
        # Item selection
        self.item_vars = {
            'Category': tk.StringVar(),
            'quantity': tk.StringVar(value="1"),
            'price': tk.StringVar()
        }
        
        tk.Label(items_frame, text="Product:", font=('Arial', 10)).grid(
            row=0, column=0, sticky='e', padx=5, pady=5)
        
        self.cursor.execute("SELECT product_name FROM products")
        products = self.cursor.fetchall()
        product_list = [name[0] for name in products]
        
        self.sales_product_combo = ttk.Combobox(items_frame,
                                    textvariable=self.item_vars['Category'],
                                    values=product_list, width=30, font=('Arial', 10))
        self.sales_product_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.sales_product_combo.bind('<<ComboboxSelected>>', self.on_product_selected)
        
        tk.Label(items_frame, text="Quantity:", font=('Arial', 10)).grid(
            row=0, column=2, sticky='e', padx=5, pady=5)
        tk.Entry(items_frame, textvariable=self.item_vars['quantity'],
                width=10, font=('Arial', 10)).grid(row=0, column=3, sticky='w', padx=5, pady=5)
        
        tk.Label(items_frame, text="Price:", font=('Arial', 10)).grid(
            row=0, column=4, sticky='e', padx=5, pady=5)
        tk.Entry(items_frame, textvariable=self.item_vars['price'],
                width=10, font=('Arial', 10)).grid(row=0, column=5, sticky='w', padx=5, pady=5)
        
        tk.Button(items_frame, text="Add Item", command=self.add_sale_item,
                 bg=self.colors['success'], fg='white', width=12).grid(
            row=0, column=6, padx=10, pady=5)
        
        # Invoice items table
        table_frame = tk.LabelFrame(self.sales_tab, text="Invoice Items",
                                   font=('Arial', 11, 'bold'))
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('Product Name', 'Quantity', 'Price', 'Total')
        self.sale_items_tree = ttk.Treeview(table_frame, columns=columns,
                                           show='headings', height=8)
        
        for col in columns:
            self.sale_items_tree.heading(col, text=col)
            self.sale_items_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical',
                                 command=self.sale_items_tree.yview)
        self.sale_items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sale_items_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Invoice totals
        totals_frame = tk.Frame(self.sales_tab)
        totals_frame.pack(fill='x', padx=10, pady=10)
        
        self.sale_totals = {
            'subtotal': tk.StringVar(value="0.00"),
            'discount_amount': tk.StringVar(value="0.00"),
            'net_total': tk.StringVar(value="0.00")
        }
        
        tk.Label(totals_frame, text="Subtotal:", font=('Arial', 11, 'bold')).pack(side='left', padx=10)
        tk.Label(totals_frame, textvariable=self.sale_totals['subtotal'],
                font=('Arial', 11)).pack(side='left', padx=10)
        
        tk.Label(totals_frame, text="Discount:", font=('Arial', 11, 'bold')).pack(side='left', padx=10)
        tk.Label(totals_frame, textvariable=self.sale_totals['discount_amount'],
                font=('Arial', 11)).pack(side='left', padx=10)
        
        tk.Label(totals_frame, text="Net Total:", font=('Arial', 12, 'bold'),
                fg=self.colors['success']).pack(side='left', padx=10)
        tk.Label(totals_frame, textvariable=self.sale_totals['net_total'],
                font=('Arial', 12, 'bold'), fg=self.colors['success']).pack(side='left', padx=10)
        
        # Buttons
        buttons_frame = tk.Frame(self.sales_tab)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(buttons_frame, text="Save Invoice", command=self.save_invoice,
                 bg=self.colors['success'], fg='white', font=('Arial', 11, 'bold'),
                 width=15, pady=10).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="New Invoice", command=self.new_invoice,
                 bg=self.colors['secondary'], fg='white', font=('Arial', 11, 'bold'),
                 width=15, pady=10).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Remove Item", command=self.remove_sale_item,
                 bg=self.colors['danger'], fg='white', font=('Arial', 11, 'bold'),
                 width=15, pady=10).pack(side='left', padx=5)
        
        # Generate first invoice number
        self.generate_invoice_number()
    
    def create_inventory_tab(self):
        """Create inventory management tab"""
        self.inventory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_tab, text="📊 Inventory")
        
        # Title
        title_label = tk.Label(self.inventory_tab, text="Inventory Management",
                              font=('Arial', 14, 'bold'), bg=self.colors['primary'],
                              fg='white', pady=15)
        title_label.pack(fill='x')
        
        # Inventory movement form
        form_frame = tk.LabelFrame(self.inventory_tab, text="Inventory Movement",
                                  font=('Arial', 11, 'bold'), padx=10, pady=10)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        self.inventory_vars = {
            'product_name': tk.StringVar(),
            'movement': tk.StringVar(value='in'),
            'quantity': tk.StringVar(),
            'reference': tk.StringVar()
        }
        
        tk.Label(form_frame, text="Product:", font=('Arial', 10)).grid(
            row=0, column=0, sticky='e', padx=5, pady=5)
        
        self.cursor.execute("SELECT product_name FROM products")
        products = self.cursor.fetchall()
        product_list = [ name for name in products]
        
        self.inventory_product_combo = ttk.Combobox(form_frame,
                                    textvariable=self.inventory_vars['product_name'],
                                    values=product_list, width=30, font=('Arial', 10))
        self.inventory_product_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        tk.Label(form_frame, text="Movement Type:", font=('Arial', 10)).grid(
            row=0, column=2, sticky='e', padx=5, pady=5)
        
        movement_frame = tk.Frame(form_frame)
        movement_frame.grid(row=0, column=3, sticky='w', padx=5, pady=5)
        
        tk.Radiobutton(movement_frame, text="In", variable=self.inventory_vars['movement'],
                      value='in', font=('Arial', 10)).pack(side='left', padx=5)
        tk.Radiobutton(movement_frame, text="Out", variable=self.inventory_vars['movement'],
                      value='out', font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Label(form_frame, text="Quantity:", font=('Arial', 10)).grid(
            row=1, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.inventory_vars['quantity'],
                width=15, font=('Arial', 10)).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        tk.Label(form_frame, text="Reference:", font=('Arial', 10)).grid(
            row=1, column=2, sticky='e', padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.inventory_vars['reference'],
                width=30, font=('Arial', 10)).grid(row=1, column=3, sticky='w', padx=5, pady=5)
        
        # Buttons
        buttons_frame = tk.Frame(form_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        tk.Button(buttons_frame, text="Add Movement", command=self.add_inventory_movement,
                 bg=self.colors['success'], fg='white', width=15).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Clear", command=self.clear_inventory_form,
                 bg=self.colors['secondary'], fg='white', width=15).pack(side='left', padx=5)
        
        # Inventory movements table
        table_frame = tk.LabelFrame(self.inventory_tab, text="Inventory Movements",
                                   font=('Arial', 11, 'bold'))
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('ID', 'product_name', 'Movement', 'Quantity', 'Date', 'Reference')
        self.inventory_tree = ttk.Treeview(table_frame, columns=columns,
                                          show='headings', height=15)
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical',
                                 command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        self.inventory_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load inventory movements
        self.load_inventory()
    
    def create_reports_tab(self):
        """Create reports tab"""
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="📈 Reports")
        
        # Title
        title_label = tk.Label(self.reports_tab, text="Reports and Analytics",
                              font=('Arial', 14, 'bold'), bg=self.colors['primary'],
                              fg='white', pady=15)
        title_label.pack(fill='x')
        
        # Report selection
        selection_frame = tk.LabelFrame(self.reports_tab, text="Report Selection",
                                       font=('Arial', 11, 'bold'), padx=10, pady=10)
        selection_frame.pack(fill='x', padx=10, pady=10)
        
        self.report_type = tk.StringVar(value='sales')
        
        reports = [
            ('sales', 'Sales Report'),
            ('inventory', 'Inventory Report'),
            ('customers', 'Customers Report'),
            ('products', 'Products Report')
        ]
        
        for i, (value, text) in enumerate(reports):
            tk.Radiobutton(selection_frame, text=text, variable=self.report_type,
                          value=value, font=('Arial', 10)).grid(
                row=0, column=i, padx=10, pady=5)
        
        # Date range
        date_frame = tk.Frame(selection_frame)
        date_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        tk.Label(date_frame, text="From:", font=('Arial', 10)).pack(side='left', padx=5)
        self.from_date = tk.StringVar(value=dt.now().strftime('%Y-%m-%d'))
        tk.Entry(date_frame, textvariable=self.from_date, width=15,
                font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Label(date_frame, text="To:", font=('Arial', 10)).pack(side='left', padx=5)
        self.to_date = tk.StringVar(value=dt.now().strftime('%Y-%m-%d'))
        tk.Entry(date_frame, textvariable=self.to_date, width=15,
                font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Button(date_frame, text="Generate Report", command=self.generate_report,
                 bg=self.colors['success'], fg='white', width=15).pack(side='left', padx=10)
        tk.Button(date_frame, text="Export to Excel", command=self.export_report,
                 bg=self.colors['secondary'], fg='white', width=15).pack(side='left', padx=5)
        
        # Report display
        display_frame = tk.LabelFrame(self.reports_tab, text="Report Results",
                                     font=('Arial', 11, 'bold'))
        display_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Report treeview
        self.report_tree = ttk.Treeview(display_frame, show='headings', height=20)
        
        scrollbar_y = ttk.Scrollbar(display_frame, orient='vertical',
                                   command=self.report_tree.yview)
        scrollbar_x = ttk.Scrollbar(display_frame, orient='horizontal',
                                   command=self.report_tree.xview)
        
        self.report_tree.configure(yscrollcommand=scrollbar_y.set,
                                  xscrollcommand=scrollbar_x.set)
        
        self.report_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)
        
        
    def create_expenses_tab(self):
                """Create expenses tab"""
                self.expenses_tab = ttk.Frame(self.notebook)
                self.notebook.add(self.expenses_tab, text="💸 Expenses")

                # العنوان
                title_label = tk.Label(
                    self.expenses_tab,
                    text="Expenses Management",
                    font=('Arial', 14, 'bold'),
                    bg=self.colors['primary'],
                    fg='white',
                    pady=15
                )
                title_label.pack(fill='x')

                # نموذج الإدخال
                form_frame = tk.LabelFrame(
                    self.expenses_tab,
                    text="Add New Expense",
                    font=('Arial', 11, 'bold'),
                    padx=10,
                    pady=10
                )
                form_frame.pack(fill='x', padx=10, pady=10)

                self.expense_vars = {
                    'title': tk.StringVar(),
                    'amount': tk.StringVar()
                }

                # اسم المصروف
                tk.Label(form_frame, text="Expense Name:", font=('Arial', 10)).grid(
                    row=0, column=0, sticky='e', padx=5, pady=5
                )
                tk.Entry(form_frame, textvariable=self.expense_vars['title'],
                        width=30, font=('Arial', 10)).grid(
                    row=0, column=1, padx=5, pady=5
                )

                # المبلغ
                tk.Label(form_frame, text="Amount:", font=('Arial', 10)).grid(
                    row=1, column=0, sticky='e', padx=5, pady=5
                )
                tk.Entry(form_frame, textvariable=self.expense_vars['amount'],
                        width=30, font=('Arial', 10)).grid(
                    row=1, column=1, padx=5, pady=5
                )

                # زر الحفظ
                tk.Button(
                    form_frame,
                    text="Save Expense",
                    command=self.save_expense,
                    bg=self.colors['success'],
                    fg='white',
                    width=15
                ).grid(row=2, column=0, columnspan=2, pady=10)
                
    
    # ===== Customer Functions =====
    
    def load_customers(self):
        """Load customers from database"""
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        self.cursor.execute("SELECT * FROM customers ORDER BY customer_code")
        for row in self.cursor.fetchall():
            self.customers_tree.insert('', 'end', values=row)
        
        # Refresh customer combo boxes in sales tab
        self.refresh_customer_combos()
    
    def add_customer(self):
        """Add new customer"""
        try:
            code = self.customer_vars['customer_code'].get().strip()
            name = self.customer_vars['customer_name'].get().strip()
            
            if not code or not name:
                messagebox.showwarning("Warning", "Please enter customer code and name")
                return
            
            self.cursor.execute('''
                INSERT INTO customers (customer_code, customer_name, phone, address, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                code,
                name,
                self.customer_vars['customer_phone'].get(),
                self.customer_vars['customer_address'].get(),
                self.customer_vars['customer_email'].get()
            ))
            
            self.conn.commit()
            self.load_customers()
            self.clear_customer_form()
            messagebox.showinfo("Success", "Customer added successfully")
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Customer code already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding customer: {str(e)}")
    
    def update_customer(self):
        """Update existing customer"""
        try:
            code = self.customer_vars['customer_code'].get().strip()
            
            if not code:
                messagebox.showwarning("Warning", "Please select a customer to update")
                return
            
            self.cursor.execute('''
                UPDATE customers 
                SET customer_name=?, phone=?, address=?, email=?
                WHERE customer_code=?
            ''', (
                self.customer_vars['customer_name'].get(),
                self.customer_vars['customer_phone'].get(),
                self.customer_vars['customer_address'].get(),
                self.customer_vars['customer_email'].get(),
                code
            ))
            
            self.conn.commit()
            self.load_customers()
            self.clear_customer_form()
            messagebox.showinfo("Success", "Customer updated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating customer: {str(e)}")
    
    def delete_customer(self):
        """Delete customer"""
        try:
            code = self.customer_vars['customer_code'].get().strip()
            
            if not code:
                messagebox.showwarning("Warning", "Please select a customer to delete")
                return
            
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this customer?"):
                self.cursor.execute("DELETE FROM customers WHERE customer_code=?", (code,))
                self.conn.commit()
                self.load_customers()
                self.clear_customer_form()
                messagebox.showinfo("Success", "Customer deleted successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting customer: {str(e)}")
    
    def clear_customer_form(self):
        """Clear customer form"""
        for var in self.customer_vars.values():
            var.set('')
    
    def on_customer_select(self, event):
        """Handle customer selection"""
        selection = self.customers_tree.selection()
        if selection:
            item = self.customers_tree.item(selection[0])
            values = item['values']
            
            self.customer_vars['customer_code'].set(values[0])
            self.customer_vars['customer_name'].set(values[1])
            self.customer_vars['customer_phone'].set(values[2])
            self.customer_vars['customer_address'].set(values[3])
            self.customer_vars['customer_email'].set(values[4])
    
    # ===== Product Functions =====
    
    def load_products(self):
        """Load products from database"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        self.cursor.execute("SELECT * FROM products ORDER BY product_code")
        for row in self.cursor.fetchall():
            self.products_tree.insert('', 'end', values=row)
        
        # Refresh product combo boxes in other tabs
        self.refresh_product_combos()
    
    def add_product(self):
        """Add new product"""
        try:
            code = self.product_vars['Category'].get().strip()
            name = self.product_vars['product_name'].get().strip()
            
            if not code or not name:
                messagebox.showwarning("Warning", "Please enter product code and name")
                return
            
            self.cursor.execute('''
                INSERT INTO products (Category, product_name, Quantitee, 
                                    purchase_price, selling_price, minimum_limit)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                code,
                name,
                self.product_vars['Quantitee'].get(),
                float(self.product_vars['purchase_price'].get() or 0),
                float(self.product_vars['selling_price'].get() or 0),
                int(self.product_vars['minimum_limit'].get() or 10)
            ))
            
            self.conn.commit()
            self.load_products()
            self.clear_product_form()
            messagebox.showinfo("Success", "Product added successfully")
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Product code already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding product: {str(e)}")
    
    def update_product(self):
        """Update existing product"""
        try:
            code = self.product_vars['product_name'].get().strip()
            
            if not code:
                messagebox.showwarning("Warning", "Please select a product to update")
                return
            
            self.cursor.execute('''
                UPDATE products 
                SET Category=?, product_name=?, Quantitee=?, purchase_price=?, 
                    selling_price=?, minimum_limit=?
                WHERE product_name=?
            ''', (
                self.product_vars['Category'].get(),
                self.product_vars['product_name'].get(),
                self.product_vars['Quantitee'].get(),
                float(self.product_vars['purchase_price'].get() or 0),
                float(self.product_vars['selling_price'].get() or 0),
                int(self.product_vars['minimum_limit'].get() or 10),
                code
            ))
            
            self.conn.commit()
            self.load_products()
            self.clear_product_form()
            messagebox.showinfo("Success", "Product updated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating product: {str(e)}")
    
    def delete_product(self):
        """Delete product"""
        try:
            code = self.product_vars['product_code'].get().strip()
            
            if not code:
                messagebox.showwarning("Warning", "Please select a product to delete")
                return
            
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
                self.cursor.execute("DELETE FROM products WHERE product_code=?", (code,))
                self.conn.commit()
                self.load_products()
                self.clear_product_form()
                messagebox.showinfo("Success", "Product deleted successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting product: {str(e)}")
    
    def clear_product_form(self):
        """Clear product form"""
        for var in self.product_vars.values():
            var.set('')
    
    def on_product_select(self, event):
            """Handle product selection"""
            selection = self.products_tree.selection()
            if selection:
                item = self.products_tree.item(selection[0])
                values = item['values']
                
                # product_code est à l'index 0, Category à l'index 1
                # Mais vous avez besoin de product_code pour les autres fonctions
                product_code = values[0]  # Ajouté
                self.product_vars['Category'].set(values[1])
                self.product_vars['product_name'].set(values[2])
                self.product_vars['Quantitee'].set(values[3])
                self.product_vars['purchase_price'].set(values[4])
                self.product_vars['selling_price'].set(values[5])
                self.product_vars['minimum_limit'].set(values[6])
                
                # Stocker product_code pour référence
                if not hasattr(self, 'selected_product_code'):
                    self.selected_product_code = tk.StringVar()
                self.selected_product_code.set(product_code)
    
    def refresh_product_combos(self):
       
            """Refresh product combo boxes in sales and inventory tabs"""
            try:
                # Get updated product list
                self.cursor.execute("SELECT product_code, product_name FROM products")  # Changé product_code -> Category
                products = self.cursor.fetchall()
                product_list = [f"{code} - {name}" for code, name in products]
                
                # Update sales tab product combo
                if hasattr(self, 'sales_product_combo'):
                    current_value = self.item_vars['Category'].get()  # Changé 'Category' -> 'product_code'
                    self.sales_product_combo['values'] = product_list
                    self.item_vars['Category'].set(current_value)  # Changé 'Category' -> 'product_code'
                
                # Update inventory tab product combo
                if hasattr(self, 'inventory_product_combo'):
                    current_value = self.inventory_vars['Category'].get()
                    self.inventory_product_combo['values'] = product_list
                    self.inventory_vars['Category'].set(current_value)
                    
            except Exception as e:
                print(f"Error refreshing product combos: {e}")
    
    def refresh_customer_combos(self):
        """Refresh customer combo boxes in sales tab"""
        try:
            # Get updated customer list
            self.cursor.execute("SELECT customer_code, customer_name FROM customers")
            customers = self.cursor.fetchall()
            customer_list = [f"{code} - {name}" for code, name in customers]
            
            # Update sales tab customer combo
            if hasattr(self, 'customer_combo'):
                current_value = self.sale_vars['customer_code'].get()
                self.customer_combo['values'] = customer_list
                self.sale_vars['customer_code'].set(current_value)
                
        except Exception as e:
            print(f"Error refreshing customer combos: {e}")
    
    # ===== Sales Functions =====
    
    def generate_invoice_number(self):
        """Generate next invoice number"""
        try:
            self.cursor.execute("SELECT MAX(invoice_number) FROM sales")
            last_invoice = self.cursor.fetchone()[0]
            
            if last_invoice:
                num = int(last_invoice.split('-')[1]) + 1
            else:
                num = 1
            
            invoice_number = f"INV-{num:05d}"
            self.sale_vars['invoice_number'].set(invoice_number)
            
        except Exception as e:
            print(f"Error generating invoice number: {e}")
            self.sale_vars['invoice_number'].set("INV-00001")
    
    def on_product_selected(self, event):
        """Update price when product is selected"""
        try:
            product_info = self.item_vars['product_code'].get()  # Changé 'Category' -> 'product_code'
           
            if product_info:
                # La nouvelle format est "Category - product_name"
                product_code = product_info.split(' - ')[0]
                
                self.cursor.execute("SELECT selling_price FROM products WHERE product_code=?",  # Changé product_code -> Category
                                )
                result = self.cursor.fetchone()
                
                if result:
                    self.item_vars['price'].set(str(result[0]))
        except Exception as e:
            print(f"Error loading product price: {e}")
    
    def add_sale_item(self):
        """Add item to invoice"""
        try:
            product_info = self.item_vars['product_name'].get()
            if not product_info:
                messagebox.showwarning("Warning", "Please select a product")
                return
            
            product_code = product_info.split(' - ')[0]
            product_name = product_info.split(' - ')[1]
            quantity = int(self.item_vars['quantity'].get())
            price = float(self.item_vars['price'].get())
            total = quantity * price
            
            # Store product code in item tags for later retrieval
            item_id = self.sale_items_tree.insert('', 'end', 
                                       values=(product_name, quantity, price, total),
                                       tags=(product_code,))
            
            self.calculate_invoice_totals()
            
            # Clear item fields
            self.item_vars['product_code'].set('')
            self.item_vars['quantity'].set('1')
            self.item_vars['price'].set('')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error adding item: {str(e)}")
    
    def remove_sale_item(self):
        """Remove selected item from invoice"""
        selection = self.sale_items_tree.selection()
        if selection:
            self.sale_items_tree.delete(selection[0])
            self.calculate_invoice_totals()
        else:
            messagebox.showwarning("Warning", "Please select an item to remove")
    
    def calculate_invoice_totals(self):
        """Calculate invoice totals"""
        try:
            subtotal = 0
            for item in self.sale_items_tree.get_children():
                values = self.sale_items_tree.item(item)['values']
                subtotal += float(values[3])  # Total is now at index 3 instead of 4
            
            discount = float(self.sale_vars['discount'].get() or 0)
            discount_amount = subtotal * (discount / 100)
            net_total = subtotal - discount_amount
            
            self.sale_totals['subtotal'].set(f"{subtotal:.2f}")
            self.sale_totals['discount_amount'].set(f"{discount_amount:.2f}")
            self.sale_totals['net_total'].set(f"{net_total:.2f}")
            
        except Exception as e:
            print(f"Error calculating totals: {e}")
    
    def save_invoice(self):
        """Save invoice to database"""
        try:
            invoice_number = self.sale_vars['invoice_number'].get()
            customer_info = self.sale_vars['customer_code'].get()
            
            if not customer_info:
                messagebox.showwarning("Warning", "Please select a customer")
                return
            
            if not self.sale_items_tree.get_children():
                messagebox.showwarning("Warning", "Please add items to the invoice")
                return
            
            customer_code = customer_info.split(' - ')[0]
            customer_name = customer_info.split(' - ')[1] if ' - ' in customer_info else ''
            
            # Save invoice header
            self.cursor.execute('''
                INSERT INTO sales (invoice_number, customer_code, invoice_total, 
                                 discount, net_invoice, invoice_status)
                VALUES (?, ?, ?, ?, ?, 'closed')
            ''', (
                invoice_number,
                customer_code,
                float(self.sale_totals['subtotal'].get()),
                float(self.sale_vars['discount'].get() or 0),
                float(self.sale_totals['net_total'].get())
            ))
            
            # Prepare data for CSV export
            csv_data = []
            
            # Save invoice items and update inventory
            for item in self.sale_items_tree.get_children():
                values = self.sale_items_tree.item(item)['values']
                tags = self.sale_items_tree.item(item)['tags']
                
                # Get product code from tags
                product_code = tags[0] if tags else None
                if not product_code:
                    continue
                
                product_name = values[0]   # Product name at index 0
                quantity = int(values[1])  # Quantity at index 1
                price = float(values[2])   # Price at index 2
                total = float(values[3])   # Total at index 3
                
                # Save item
                self.cursor.execute('''
                    INSERT INTO sales_details (invoice_number, product_code, 
                                              quantity, price, total)
                    VALUES (?, ?, ?, ?, ?)
                ''', (invoice_number, product_code, quantity, price, total))
                
                # Update inventory (outgoing movement)
                self.cursor.execute('''
                    INSERT INTO inventory (product_code, movement, quantity, reference)
                    VALUES (?, 'out', ?, ?)
                ''', (product_code, quantity, f"Invoice {invoice_number}"))
                
                # Add to CSV data
                csv_data.append({
                    'Invoice Number': invoice_number,
                    'Date': dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Customer Code': customer_code,
                    'Customer Name': customer_name,
                    'Product Code': product_code,
                    'Product Name': product_name,
                    'Quantity': quantity,
                    'Price': price,
                    'Total': total,
                    'Discount': float(self.sale_vars['discount'].get() or 0),
                    'Net Total': float(self.sale_totals['net_total'].get())
                })
            
            self.conn.commit()
            
            # === Save invoice to CSV automatically ===
            try:
                csv_file = "invoices.csv"

                # Prepare invoice data
                data = []
                for item in self.sale_items_tree.get_children():
                    values = self.sale_items_tree.item(item)['values']
                    product_name = values[0]
                    quantity = values[1]
                    price = values[2]
                    total = values[3]

                    data.append([
                        invoice_number,
                        customer_code,
                        product_name,
                        quantity,
                        price,
                        total,
                        self.sale_totals['net_total'].get()
                    ])

                df = pd.DataFrame(data, columns=[
                    "Invoice Number",
                    "Customer Code",
                    "Product Name",
                    "Quantity",
                    "Price",
                    "Total",
                    "Net Invoice"
                ])

                # Append to CSV if exists
                if os.path.exists(csv_file):
                    df.to_csv(csv_file, mode="a", index=False, header=False)
                else:
                    df.to_csv(csv_file, index=False)

            except Exception as e:
                print("CSV save error:", e)

            
            # Save to CSV file
            self.save_invoice_to_csv(csv_data)
            
            messagebox.showinfo("Success", f"Invoice {invoice_number} saved successfully\nand exported to CSV file")
            
            self.new_invoice()
            self.update_dashboard()
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error saving invoice: {str(e)}")
    
    def save_invoice_to_csv(self, invoice_data):
        """Save invoice data to CSV file"""
        try:
            # Create invoices directory if it doesn't exist
            if not os.path.exists('invoices'):
                os.makedirs('invoices')
            
            # CSV file path
            csv_file = 'invoices/invoices_log.csv'
            
            # Check if file exists to determine if we need to write headers
            file_exists = os.path.isfile(csv_file)
            
            # Convert to DataFrame
            df = pd.DataFrame(invoice_data)
            
            # Append to CSV file
            df.to_csv(csv_file, mode='a', header=not file_exists, index=False, encoding='utf-8')
            
            print(f"Invoice saved to {csv_file}")
            
        except Exception as e:
            print(f"Error saving invoice to CSV: {e}")
    
    def new_invoice(self):
        """Start new invoice"""
        # Clear invoice items
        for item in self.sale_items_tree.get_children():
            self.sale_items_tree.delete(item)
        
        # Reset values
        self.sale_vars['customer_code'].set('')
        self.sale_vars['discount'].set('0')
        self.sale_totals['subtotal'].set('0.00')
        self.sale_totals['discount_amount'].set('0.00')
        self.sale_totals['net_total'].set('0.00')
        
        # Generate new invoice number
        self.generate_invoice_number()
    
    # ===== Inventory Functions =====
    
    def load_inventory(self):
        """Load inventory movements"""
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        self.cursor.execute('''
            SELECT * FROM inventory 
            ORDER BY date DESC 
            LIMIT 100
        ''')
        
        for row in self.cursor.fetchall():
            self.inventory_tree.insert('', 'end', values=row)
    
    def add_inventory_movement(self):
        """Add inventory movement"""
        try:
            product_info = self.inventory_vars['product_name'].get()
            if not product_info:
                messagebox.showwarning("Warning", "Please select a product")
                return
            
            product_code = product_info.split(' - ')[0]
            movement = self.inventory_vars['movement'].get()
            quantity = int(self.inventory_vars['quantity'].get())
            reference = self.inventory_vars['reference'].get()
            
            self.cursor.execute('''
                INSERT INTO inventory (product_name, movement, quantity, reference)
                VALUES (?, ?, ?, ?)
            ''', (product_code, movement, quantity, reference))
            
            code = self.product_vars['product_name'].get().strip()
            
            self.cursor.execute('''
                UPDATE products 
                SET Category=?, product_name=?, Quantitee=?, purchase_price=?, 
                    selling_price=?, minimum_limit=?
                WHERE product_name=?
            ''', (
                #self.product_vars['Category'].get(),
                self.product_vars['product_name'].get(),
                self.product_vars['Quantitee'].get(),
                #float(self.product_vars['purchase_price'].get() or 0),
                #float(self.product_vars['selling_price'].get() or 0),
                #int(self.product_vars['minimum_limit'].get() or 10),
                code
            ))
            
            self.conn.commit()
            self.load_inventory()
            self.clear_inventory_form()
            
            messagebox.showinfo("Success", "Inventory movement added successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error adding inventory movement: {str(e)}")
    
    def clear_inventory_form(self):
        """Clear inventory form"""
        self.inventory_vars['product_name'].set('')
        self.inventory_vars['movement'].set('in')
        self.inventory_vars['quantity'].set('')
        self.inventory_vars['reference'].set('')
    
    # ===== Report Functions =====
    
    def generate_report(self):
        """Generate selected report"""
        try:
            report_type = self.report_type.get()
            
            # Clear previous report
            self.report_tree.delete(*self.report_tree.get_children())
            
            if report_type == 'sales':
                self.generate_sales_report()
            elif report_type == 'inventory':
                self.generate_inventory_report()
            elif report_type == 'customers':
                self.generate_customers_report()
            elif report_type == 'products':
                self.generate_products_report()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {str(e)}")
    
    def generate_sales_report(self):
        """Generate sales report"""
        columns = ('Invoice #', 'Date', 'Customer', 'Total', 'Discount', 'Net', 'Status')
        self.report_tree['columns'] = columns
        
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=100)
        
        self.cursor.execute('''
            SELECT s.invoice_number, s.invoice_date, c.customer_name,
                   s.invoice_total, s.discount, s.net_invoice, s.invoice_status
            FROM sales s
            LEFT JOIN customers c ON s.customer_code = c.customer_code
            WHERE DATE(s.invoice_date) BETWEEN ? AND ?
            ORDER BY s.invoice_date DESC
        ''', (self.from_date.get(), self.to_date.get()))
        
        for row in self.cursor.fetchall():
            self.report_tree.insert('', 'end', values=row)
    
    def generate_inventory_report(self):
        """Generate inventory report"""
        columns = ('Product Name', 'In', 'Out', 'Balance')
        self.report_tree['columns'] = columns
        
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=120)
        
        self.cursor.execute('''
            SELECT 
                p.product_name,
                COALESCE((SELECT SUM(quantity) FROM inventory 
                         WHERE product_code = p.product_code AND movement = 'in'), 0) as total_in,
                COALESCE((SELECT SUM(quantity) FROM inventory 
                         WHERE product_code = p.product_code AND movement = 'out'), 0) as total_out,
                COALESCE((SELECT SUM(quantity) FROM inventory 
                         WHERE product_code = p.product_code AND movement = 'in'), 0) -
                COALESCE((SELECT SUM(quantity) FROM inventory 
                         WHERE product_code = p.product_code AND movement = 'out'), 0) as balance
            FROM products p
            ORDER BY p.product_name
        ''')
        
        for row in self.cursor.fetchall():
            self.report_tree.insert('', 'end', values=row)
    
    def generate_customers_report(self):
        """Generate customers report"""
        columns = ('Code', 'Name', 'Phone', 'Email', 'Total Purchases')
        self.report_tree['columns'] = columns
        
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=120)
        
        self.cursor.execute('''
            SELECT 
                c.customer_code,
                c.customer_name,
                c.phone,
                c.email,
                COALESCE(SUM(s.net_invoice), 0) as total_purchases
            FROM customers c
            LEFT JOIN sales s ON c.customer_code = s.customer_code
            GROUP BY c.customer_code
            ORDER BY total_purchases DESC
        ''')
        
        for row in self.cursor.fetchall():
            self.report_tree.insert('', 'end', values=row)
    
    def generate_products_report(self):
        """Generate products report"""
        columns = ('Product Name', 'Unit', 'Purchase Price', 'Selling Price', 'Stock')
        self.report_tree['columns'] = columns
        
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=100)
        
        self.cursor.execute('''
            SELECT 
                p.product_name,
                p.unit_of_measure,
                p.purchase_price,
                p.selling_price,
                COALESCE((SELECT SUM(quantity) FROM inventory 
                         WHERE product_code = p.product_code AND movement = 'in'), 0) -
                COALESCE((SELECT SUM(quantity) FROM inventory 
                         WHERE product_code = p.product_code AND movement = 'out'), 0) as stock
            FROM products p
            ORDER BY p.product_name
        ''')
        
        for row in self.cursor.fetchall():
            self.report_tree.insert('', 'end', values=row)
    
    def export_report(self):
        """Export report to Excel"""
        try:
            if not self.report_tree.get_children():
                messagebox.showwarning("Warning", "Please generate a report first")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Get column headers
            columns = self.report_tree['columns']
            
            # Get data
            data = []
            for item in self.report_tree.get_children():
                data.append(self.report_tree.item(item)['values'])
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # Export to Excel
            df.to_excel(file_path, index=False, sheet_name='Report')
            
            messagebox.showinfo("Success", f"Report exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting report: {str(e)}")
    
    # ===== Dashboard Functions =====
    
    def update_dashboard(self):
        """Update dashboard"""
        try:
            # Total sales
            self.cursor.execute("SELECT SUM(net_invoice) FROM sales WHERE DATE(invoice_date) = DATE('now')")
            total_sales = self.cursor.fetchone()[0] or 0
            self.metrics_vars['total_sales'].set(f"{total_sales:.2f}")
            
            # Total customers
            self.cursor.execute("SELECT COUNT(*) FROM customers")
            total_customers = self.cursor.fetchone()[0] or 0
            self.metrics_vars['total_customers'].set(total_customers)
            
            # Total products
            self.cursor.execute("SELECT COUNT(*) FROM products")
            total_products = self.cursor.fetchone()[0] or 0
            self.metrics_vars['total_products'].set(total_products)
            
            # Inventory value
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
            inventory_value = self.cursor.fetchone()[0] or 0
            self.metrics_vars['inventory_value'].set(f"{inventory_value:.2f}")
            
            # Update quick analysis
            for item in self.analysis_tree.get_children():
                self.analysis_tree.delete(item)
            
            # Add analyses
            analyses = [
                ("Today's Sales", f"{total_sales:.2f} $", "Higher than yesterday" if total_sales > 0 else "No sales"),
                ("New Customers", "0", "No new customers registered today"),
                ("Low Stock Items", "2", "Need reorder"),
                ("Today's Invoices", "3", "All invoices processed")
            ]
            
            for analysis in analyses:
                self.analysis_tree.insert('', 'end', values=analysis)
                
        except Exception as e:
            print(f"Error updating dashboard: {e}")
    
    def quick_report(self):
        """Create quick report"""
        self.notebook.select(self.reports_tab)
        self.generate_report()
    
    # ===== Helper Functions =====
    
    def import_csv(self):
        """Import data from CSV file"""
        try:
            # Ask user which type of data to import
            import_window = tk.Toplevel(self.root)
            import_window.title("Import CSV File")
            import_window.geometry("400x300")
            import_window.transient(self.root)
            import_window.grab_set()
            
            # Center the window
            import_window.update_idletasks()
            x = (import_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (import_window.winfo_screenheight() // 2) - (300 // 2)
            import_window.geometry(f"400x300+{x}+{y}")
            
            # Title
            title_label = tk.Label(import_window, text="Select Data Type to Import",
                                  font=('Arial', 14, 'bold'), bg=self.colors['primary'],
                                  fg='white', pady=15)
            title_label.pack(fill='x')
            
            # Instructions
            instructions = tk.Label(import_window, 
                                   text="Select the type of data in your CSV file:",
                                   font=('Arial', 10), pady=10)
            instructions.pack()
            
            # Data type selection
            data_type_var = tk.StringVar(value='customers')
            
            options_frame = tk.Frame(import_window, pady=20)
            options_frame.pack()
            
            tk.Radiobutton(options_frame, text="Customers", 
                          variable=data_type_var, value='customers',
                          font=('Arial', 11)).pack(anchor='w', pady=5)
            tk.Radiobutton(options_frame, text="Products", 
                          variable=data_type_var, value='products',
                          font=('Arial', 11)).pack(anchor='w', pady=5)
            tk.Radiobutton(options_frame, text="Inventory Movements", 
                          variable=data_type_var, value='inventory',
                          font=('Arial', 11)).pack(anchor='w', pady=5)
            
            # Information label
            info_text = """
                    CSV Format Requirements:
                    • Use comma (,) as separator
                    • First row must contain column headers
                    • Encoding: UTF-8
            """
            info_label = tk.Label(import_window, text=info_text,
                                 font=('Arial', 9), justify='left',
                                 fg='gray')
            info_label.pack(pady=10)
            
            # Buttons
            buttons_frame = tk.Frame(import_window)
            buttons_frame.pack(pady=10)
            
            def select_and_import():
                data_type = data_type_var.get()
                import_window.destroy()
                self.process_csv_import(data_type)
            
            tk.Button(buttons_frame, text="Select CSV File", 
                     command=select_and_import,
                     bg=self.colors['success'], fg='white',
                     font=('Arial', 11, 'bold'), width=15, pady=5).pack(side='left', padx=5)
            
            tk.Button(buttons_frame, text="Cancel",
                     command=import_window.destroy,
                     bg=self.colors['secondary'], fg='white',
                     font=('Arial', 11, 'bold'), width=15, pady=5).pack(side='left', padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error opening import dialog: {str(e)}")
    
    def process_csv_import(self, data_type):
        """Process CSV file import based on data type"""
        try:
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title=f"Select CSV file for {data_type}",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Read CSV file
            df = pd.read_csv(file_path, encoding='utf-8')
            
            if df.empty:
                messagebox.showwarning("Warning", "The CSV file is empty")
                return
            
            # Import based on type
            if data_type == 'customers':
                self.import_customers_csv(df)
            elif data_type == 'products':
                self.import_products_csv(df)
            elif data_type == 'inventory':
                self.import_inventory_csv(df)
                
        except UnicodeDecodeError:
            try:
                # Try with different encoding
                df = pd.read_csv(file_path, encoding='latin-1')
                if data_type == 'customers':
                    self.import_customers_csv(df)
                elif data_type == 'products':
                    self.import_products_csv(df)
                elif data_type == 'inventory':
                    self.import_inventory_csv(df)
            except Exception as e:
                messagebox.showerror("Error", f"Error reading CSV file: {str(e)}\nPlease check the file encoding.")
        except Exception as e:
            messagebox.showerror("Error", f"Error importing CSV: {str(e)}")
    
    def import_customers_csv(self, df):
        """Import customers from CSV"""
        try:
            # Expected columns (flexible matching)
            column_mapping = {
                'customer_code': ['customer_code', 'code', 'customer_id', 'id'],
                'customer_name': ['customer_name', 'name', 'customer'],
                'phone': ['phone', 'telephone', 'tel', 'mobile'],
                'address': ['address', 'addr', 'location'],
                'email': ['email', 'e-mail', 'mail']
            }
            
            # Normalize column names
            df.columns = df.columns.str.lower().str.strip()
            
            # Map columns
            mapped_columns = {}
            for target_col, possible_names in column_mapping.items():
                for col in df.columns:
                    if col in possible_names:
                        mapped_columns[col] = target_col
                        break
            
            if 'customer_code' not in mapped_columns.values() or 'customer_name' not in mapped_columns.values():
                messagebox.showerror("Error", 
                    "CSV must contain at least 'customer_code' and 'customer_name' columns.\n\n" +
                    "Accepted column names:\n" +
                    "- customer_code, code, customer_id, id\n" +
                    "- customer_name, name, customer")
                return
            
            df = df.rename(columns=mapped_columns)
            
            # Import records
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    customer_code = str(row.get('customer_code', '')).strip()
                    customer_name = str(row.get('customer_name', '')).strip()
                    
                    if not customer_code or not customer_name:
                        error_count += 1
                        errors.append(f"Row {index + 2}: Missing customer code or name")
                        continue
                    
                    # Check if customer exists
                    self.cursor.execute("SELECT customer_code FROM customers WHERE customer_code = ?", 
                                       (customer_code,))
                    exists = self.cursor.fetchone()
                    
                    if exists:
                        # Update existing customer
                        self.cursor.execute('''
                            UPDATE customers 
                            SET customer_name=?, phone=?, address=?, email=?
                            WHERE customer_code=?
                        ''', (
                            customer_name,
                            str(row.get('phone', '')),
                            str(row.get('address', '')),
                            str(row.get('email', '')),
                            customer_code
                        ))
                    else:
                        # Insert new customer
                        self.cursor.execute('''
                            INSERT INTO customers (customer_code, customer_name, phone, address, email)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            customer_code,
                            customer_name,
                            str(row.get('phone', '')),
                            str(row.get('address', '')),
                            str(row.get('email', ''))
                        ))
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {index + 2}: {str(e)}")
            
            self.conn.commit()
            self.load_customers()
            
            # Show results
            result_message = f"Import completed!\n\n"
            result_message += f"✓ Successfully imported: {success_count}\n"
            if error_count > 0:
                result_message += f"✗ Errors: {error_count}\n\n"
                if len(errors) <= 5:
                    result_message += "Errors:\n" + "\n".join(errors)
                else:
                    result_message += "First 5 errors:\n" + "\n".join(errors[:5])
                    result_message += f"\n... and {len(errors) - 5} more errors"
            
            messagebox.showinfo("Import Results", result_message)
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error importing customers: {str(e)}")
    
    def import_products_csv(self, df):
        """Import products from CSV"""
        try:
            # Expected columns
            column_mapping = {
                #'product_code': ['product_code', 'code', 'product_id', 'id', 'item_code'],

                'product_name': ['product_name', 'name', 'product', 'item_name', 'item'],
                'Quantitee': ['unit_of_measure', 'unit', 'uom', 'measure'],
                'purchase_price': ['purchase_price', 'cost', 'buy_price', 'purchase'],
                'selling_price': ['selling_price', 'price', 'sell_price', 'sale_price'],
                'minimum_limit': ['minimum_limit', 'min_limit', 'minimum', 'min', 'min_stock']
            }
            
            # Normalize column names
            df.columns = df.columns.str.lower().str.strip()
            
            # Map columns
            mapped_columns = {}
            for target_col, possible_names in column_mapping.items():
                for col in df.columns:
                    if col in possible_names:
                        mapped_columns[col] = target_col
                        break
            
            if 'product_code' not in mapped_columns.values() or 'product_name' not in mapped_columns.values():
                messagebox.showerror("Error", 
                    "CSV must contain at least 'product_code' and 'product_name' columns.")
                return
            
            df = df.rename(columns=mapped_columns)
            
            # Import records
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    product_code = str(row.get('product_code', '')).strip()
                    product_name = str(row.get('product_name', '')).strip()
                    
                    if not product_code or not product_name:
                        error_count += 1
                        errors.append(f"Row {index + 2}: Missing product code or name")
                        continue
                    
                    # Convert numeric values
                    purchase_price = float(row.get('purchase_price', 0) or 0)
                    selling_price = float(row.get('selling_price', 0) or 0)
                    minimum_limit = int(row.get('minimum_limit', 10) or 10)
                    
                    # Check if product exists
                    self.cursor.execute("SELECT product_code FROM products WHERE product_code = ?", 
                                       (product_code,))
                    exists = self.cursor.fetchone()
                    
                    if exists:
                        # Update existing product
                        self.cursor.execute('''
                            UPDATE products 
                            SET product_name=?, unit_of_measure=?, purchase_price=?, 
                                selling_price=?, minimum_limit=?
                            WHERE product_code=?
                        ''', (
                            product_name,
                            str(row.get('Quantitee', '')),
                            purchase_price,
                            selling_price,
                            minimum_limit,
                            product_code
                        ))
                    else:
                        # Insert new product
                        self.cursor.execute('''
                            INSERT INTO products (product_code, Cattegory, product_name, Quantitee, 
                                                purchase_price, selling_price, minimum_limit)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            product_code,
                            product_name,
                            str(row.get('unit_of_measure', '')),
                            purchase_price,
                            selling_price,
                            minimum_limit
                        ))
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {index + 2}: {str(e)}")
            
            self.conn.commit()
            self.load_products()
            
            # Show results
            result_message = f"Import completed!\n\n"
            result_message += f"✓ Successfully imported: {success_count}\n"
            if error_count > 0:
                result_message += f"✗ Errors: {error_count}\n\n"
                if len(errors) <= 5:
                    result_message += "Errors:\n" + "\n".join(errors)
                else:
                    result_message += "First 5 errors:\n" + "\n".join(errors[:5])
                    result_message += f"\n... and {len(errors) - 5} more errors"
            
            messagebox.showinfo("Import Results", result_message)
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error importing products: {str(e)}")
    
    def import_inventory_csv(self, df):
        """Import inventory movements from CSV"""
        try:
            # Expected columns
            column_mapping = {
                'product_code': ['product_code', 'code', 'product_id', 'item_code'],
                'movement': ['movement', 'type', 'movement_type', 'direction'],
                'quantity': ['quantity', 'qty', 'amount'],
                'reference': ['reference', 'ref', 'note', 'remarks']
            }
            
            # Normalize column names
            df.columns = df.columns.str.lower().str.strip()
            
            # Map columns
            mapped_columns = {}
            for target_col, possible_names in column_mapping.items():
                for col in df.columns:
                    if col in possible_names:
                        mapped_columns[col] = target_col
                        break
            
            if 'product_code' not in mapped_columns.values() or 'quantity' not in mapped_columns.values():
                messagebox.showerror("Error", 
                    "CSV must contain at least 'product_code' and 'quantity' columns.")
                return
            
            df = df.rename(columns=mapped_columns)
            
            # Import records
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    product_code = str(row.get('product_code', '')).strip()
                    quantity = int(row.get('quantity', 0) or 0)
                    movement = str(row.get('movement', 'in')).strip().lower()
                    
                    # Normalize movement type
                    if movement in ['in', 'entry', 'receive', 'purchase', 'incoming', 'input']:
                        movement = 'in'
                    elif movement in ['out', 'exit', 'issue', 'sale', 'outgoing', 'output']:
                        movement = 'out'
                    else:
                        movement = 'in'  # Default to 'in'
                    
                    if not product_code or quantity <= 0:
                        error_count += 1
                        errors.append(f"Row {index + 2}: Invalid product code or quantity")
                        continue
                    
                    # Check if product exists
                    self.cursor.execute("SELECT product_code FROM products WHERE product_code = ?", 
                                       (product_code,))
                    if not self.cursor.fetchone():
                        error_count += 1
                        errors.append(f"Row {index + 2}: Product {product_code} not found")
                        continue
                    
                    # Insert inventory movement
                    self.cursor.execute('''
                        INSERT INTO inventory (product_code, movement, quantity, reference)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        product_code,
                        movement,
                        quantity,
                        str(row.get('reference', 'CSV Import'))
                    ))
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {index + 2}: {str(e)}")
            
            self.conn.commit()
            self.load_inventory()
            
            # Show results
            result_message = f"Import completed!\n\n"
            result_message += f"✓ Successfully imported: {success_count}\n"
            if error_count > 0:
                result_message += f"✗ Errors: {error_count}\n\n"
                if len(errors) <= 5:
                    result_message += "Errors:\n" + "\n".join(errors)
                else:
                    result_message += "First 5 errors:\n" + "\n".join(errors[:5])
                    result_message += f"\n... and {len(errors) - 5} more errors"
            
            messagebox.showinfo("Import Results", result_message)
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error importing inventory: {str(e)}")
    
    def export_data(self):
        """Export all data to Excel"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Create Excel file
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                tables = {
                    'Customers': "SELECT * FROM customers",
                    'Products': "SELECT * FROM products",
                    'Sales': "SELECT * FROM sales",
                    'Sales_Details': "SELECT * FROM sales_details",
                    'Inventory': "SELECT * FROM inventory"
                }
                
                for sheet_name, query in tables.items():
                    try:
                        df = pd.read_sql_query(query, self.conn)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    except Exception as e:
                        print(f"Error exporting {sheet_name}: {e}")
            
            messagebox.showinfo("Success", f"Data exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during export: {str(e)}")
    
    def backup_database(self):
        """Create database backup"""
        try:
            backup_file = f"erp_backup_{dt.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            # Copy database
            import shutil
            shutil.copy2('erp_system.db', backup_file)
            
            messagebox.showinfo("Success", f"Backup created: {backup_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during backup: {str(e)}")
    
    def calculate_balance(self):
        """Calculate inventory balance"""
        try:
            self.cursor.execute('''
                SELECT 
                    p.product_name,
                    COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'in'
                    ), 0) -
                    COALESCE((
                        SELECT SUM(quantity) FROM inventory WHERE product_code = p.product_code AND movement = 'out'
                    ), 0) as balance
                FROM products p
                ORDER BY p.product_name
            ''')
            
            balances = self.cursor.fetchall()
            
            result = "Inventory Balances:\n"
            result += "="*30 + "\n"
            
            for item in balances:
                result += f"{item[0]}: {item[1]}\n"
            
            messagebox.showinfo("Inventory Balance", result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating balance: {str(e)}")
    
    def inventory_count(self):
        """Inventory count"""
        messagebox.showinfo("Inventory Count", "This feature will be developed in future versions")
        
        
    def calculate_profit_loss(self):
            try:
                # Total sales
                self.cursor.execute("SELECT SUM(net_total) FROM sales")
                total_sales = self.cursor.fetchone()[0] or 0

                # Cost of goods (from purchases)
                self.cursor.execute("SELECT SUM(total_cost) FROM purchases")
                total_cost = self.cursor.fetchone()[0] or 0

                # Expenses
                self.cursor.execute("SELECT SUM(amount) FROM expenses")
                total_expenses = self.cursor.fetchone()[0] or 0

                profit = total_sales - total_cost - total_expenses

                return total_sales, total_cost, total_expenses, profit

            except:
                return 0, 0, 0, 0    
            
            
    def show_profit_report(self):
            sales, cost, expenses, profit = self.calculate_profit_loss()

            messagebox.showinfo(
                "Profit & Loss",
                f"Total Sales: {sales}\n"
                f"Cost of Goods: {cost}\n"
                f"Expenses: {expenses}\n\n"
                f"Net Profit: {profit}"
            )
    
    def save_expense(self):
            """Save expense to database"""
            title = self.expense_vars['title'].get().strip()
            amount = self.expense_vars['amount'].get().strip()

            if not title or not amount:
                messagebox.showwarning("Warning", "Please enter expense name and amount")
                return

            try:
                amount = float(amount)

                self.cursor.execute(
                    "INSERT INTO expenses (title, amount) VALUES (?, ?)",
                    (title, amount)
                )
                self.conn.commit()

                messagebox.showinfo("Success", "Expense saved successfully")

                # تفريغ الحقول
                self.expense_vars['title'].set("")
                self.expense_vars['amount'].set("")

            except ValueError:
                messagebox.showerror("Error", "Amount must be a number")
            
    
    def show_help(self):
        """Show user guide"""
        help_text = """
        ERP System User Guide:
        
        1. Dashboard:
           - View key metrics
           - Update data
        
        2. Customer Management:
           - Add new customers
           - Edit customer data
           - Delete customers
        
        3. Product Management:
           - Add new products
           - Set prices and limits
           - Manage inventory
        
        4. Sales Management:
           - Create sales invoices
           - Select customers and products
           - Apply discounts
        
        5. Inventory Management:
           - Record in/out movements
           - Track inventory levels
        
        6. Reports:
           - Generate various reports
           - Export reports
        
        For additional help, contact technical support.
        """
        
        messagebox.showinfo("User Guide", help_text)
    
    def about_system(self):
        """Show about system information"""
        about_text = """
        Integrated ERP System
        
        Version: 1.0.0
        Developer: Programming Team
        
        System Features:
        - Customer and supplier management
        - Inventory and product management
        - Sales and purchases management
        - Advanced reports and analytics
        - User-friendly interface
        
        © 2024 All Rights Reserved
        """
        
        messagebox.showinfo("About System", about_text)
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main function to run the system"""
    root = tk.Tk()
    app = ERPSystem(root)
    
    # Add icon (optional)
    try:
        root.iconbitmap(default='erp_icon.ico')
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()