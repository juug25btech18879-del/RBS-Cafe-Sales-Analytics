"""
RBS Cafe - Retail Sales Management & Analytics Dashboard
Second-year B.Tech CSE mini project

Technologies: Tkinter, Pandas, NumPy, CSV, Matplotlib
Run: python app.py
"""

import os
import csv
import uuid
from datetime import datetime, date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


APP_TITLE = "RBS Cafe | Retail Sales & Analytics"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")
MENU_FILE = os.path.join(DATA_DIR, "menu.csv")

# Coffee-house palette
BG = "#F5EFE6"
PANEL = "#FFFDF9"
DARK = "#2B1D16"
DARK_2 = "#3B2920"
COFFEE = "#7B4B2A"
LATTE = "#D8B894"
ACCENT = "#C87941"
TEXT = "#33251E"
MUTED = "#8B7A6D"
GREEN = "#527A55"
RED = "#B84A3A"
BORDER = "#E8DDD0"

MENU_COLUMNS = ["item_id", "item_name", "category", "price", "available"]
SALES_COLUMNS = [
    "order_id", "date", "time", "customer", "item_name", "category",
    "quantity", "unit_price", "line_total", "payment_method", "subtotal",
    "discount", "grand_total"
]

DEFAULT_MENU = [
    ("I001", "Veg Sandwich", "Snacks", 60, True),
    ("I002", "Cheese Sandwich", "Snacks", 80, True),
    ("I003", "Veg Burger", "Snacks", 70, True),
    ("I004", "French Fries", "Snacks", 60, True),
    ("I005", "Samosa", "Snacks", 20, True),
    ("I006", "Veg Puff", "Snacks", 25, True),
    ("I007", "Maggi", "Quick Bites", 50, True),
    ("I008", "Masala Dosa", "South Indian", 70, True),
    ("I009", "Cold Coffee", "Beverages", 60, True),
    ("I010", "Tea", "Beverages", 15, True),
    ("I011", "Cappuccino", "Beverages", 80, True),
    ("I012", "Fresh Lime Soda", "Beverages", 40, True),
]

def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(MENU_FILE):
        pd.DataFrame(DEFAULT_MENU, columns=MENU_COLUMNS).to_csv(MENU_FILE, index=False)
    if not os.path.exists(SALES_FILE):
        # A small set of realistic sample transactions for first launch.
        sample = []
        today = date.today()
        examples = [
            ("Aarav", "Veg Sandwich", "Snacks", 2, 60, "UPI", 0),
            ("Diya", "Cold Coffee", "Beverages", 1, 60, "Cash", 0),
            ("Rohan", "French Fries", "Snacks", 1, 60, "Card", 5),
            ("Ananya", "Cappuccino", "Beverages", 2, 80, "UPI", 0),
            ("Kabir", "Samosa", "Snacks", 3, 20, "Cash", 0),
            ("Meera", "Maggi", "Quick Bites", 1, 50, "UPI", 0),
            ("Ishaan", "Veg Burger", "Snacks", 2, 70, "Card", 10),
            ("Sara", "Tea", "Beverages", 2, 15, "Cash", 0),
        ]
        for idx, (customer, item, category, qty, price, payment, discount) in enumerate(examples):
            d = today - timedelta(days=(7 - idx))
            subtotal = qty * price
            grand = max(0, subtotal - discount)
            sample.append({
                "order_id": f"RBS-SAMPLE-{idx+1:03d}",
                "date": d.strftime("%Y-%m-%d"),
                "time": "10:30",
                "customer": customer,
                "item_name": item,
                "category": category,
                "quantity": qty,
                "unit_price": price,
                "line_total": subtotal,
                "payment_method": payment,
                "subtotal": subtotal,
                "discount": discount,
                "grand_total": grand,
            })
        pd.DataFrame(sample, columns=SALES_COLUMNS).to_csv(SALES_FILE, index=False)


class CafeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        ensure_data_files()
        self.title(APP_TITLE)
        self.geometry("1280x790")
        self.minsize(1080, 680)
        self.configure(bg=BG)

        self.menu_df = self.load_menu()
        self.sales_df = self.load_sales()
        self.cart = []
        self.current_page = None
        self.nav_buttons = {}

        self.setup_style()
        self.build_shell()
        self.show_page("Dashboard")

    def setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=TEXT, rowheight=29, borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#EDE1D3",
                        foreground=DARK, font=("Segoe UI", 10, "bold"),
                        relief="flat", padding=8)
        style.map("Treeview", background=[("selected", "#E9D4BE")],
                  foreground=[("selected", DARK)])
        style.configure("TCombobox", padding=6, fieldbackground=PANEL)
        style.configure("TEntry", padding=7)

    def load_menu(self):
        df = pd.read_csv(MENU_FILE)
        if df.empty:
            return pd.DataFrame(columns=MENU_COLUMNS)
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
        df["available"] = df["available"].astype(str).str.lower().isin(["true", "1", "yes"])
        return df

    def load_sales(self):
        df = pd.read_csv(SALES_FILE)
        if df.empty:
            return pd.DataFrame(columns=SALES_COLUMNS)
        for col in ["quantity", "unit_price", "line_total", "subtotal", "discount", "grand_total"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        return df

    def save_menu(self):
        self.menu_df.to_csv(MENU_FILE, index=False)

    def save_sales(self):
        self.sales_df.to_csv(SALES_FILE, index=False)

    def build_shell(self):
        sidebar = tk.Frame(self, bg=DARK, width=225)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=DARK)
        brand.pack(fill="x", padx=20, pady=(25, 30))
        tk.Label(brand, text="☕", bg=DARK, fg="#F4D7B5",
                 font=("Segoe UI Emoji", 25)).pack(anchor="w")
        tk.Label(brand, text="RBS CAFE", bg=DARK, fg="#FFF8EF",
                 font=("Segoe UI", 19, "bold")).pack(anchor="w", pady=(5, 0))
        tk.Label(brand, text="RETAIL SALES STUDIO", bg=DARK, fg="#C9AE97",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(2, 0))

        tk.Frame(sidebar, bg="#604535", height=1).pack(fill="x", padx=18, pady=(0, 18))
        for name, symbol in [
            ("Dashboard", "▦"), ("New Billing", "＋"), ("Sales Records", "▤"),
            ("Analytics", "◒"), ("Menu Management", "☷"), ("Reports", "⇩")
        ]:
            btn = tk.Button(sidebar, text=f"  {symbol}    {name}", anchor="w",
                            command=lambda n=name: self.show_page(n),
                            bg=DARK, fg="#EADCCF", activebackground=COFFEE,
                            activeforeground="white", relief="flat", bd=0,
                            font=("Segoe UI", 10, "bold"), padx=18, pady=13,
                            cursor="hand2")
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[name] = btn

        bottom = tk.Frame(sidebar, bg=DARK)
        bottom.pack(side="bottom", fill="x", padx=20, pady=20)
        tk.Label(bottom, text="LOCAL-FIRST • CSV STORAGE", bg=DARK,
                 fg="#B69A82", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(bottom, text="RBS Cafe  |  v1.0", bg=DARK,
                 fg="#8F7866", font=("Segoe UI", 8)).pack(anchor="w", pady=(5, 0))

        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)
        self.header = tk.Frame(self.main, bg=BG)
        self.header.pack(fill="x", padx=30, pady=(24, 12))
        self.page_title = tk.Label(self.header, text="", bg=BG, fg=DARK,
                                   font=("Segoe UI", 22, "bold"))
        self.page_title.pack(side="left")
        self.header_right = tk.Label(self.header, text="", bg=BG, fg=MUTED,
                                     font=("Segoe UI", 10))
        self.header_right.pack(side="right", pady=8)
        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=(5, 25))

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_page(self, page):
        self.current_page = page
        for name, btn in self.nav_buttons.items():
            btn.configure(bg=COFFEE if name == page else DARK,
                          fg="white" if name == page else "#EADCCF")
        self.page_title.configure(text=page)
        self.header_right.configure(text=datetime.now().strftime("%A, %d %b %Y"))
        self.clear_content()
        self.menu_df = self.load_menu()
        self.sales_df = self.load_sales()
        if page == "Dashboard":
            self.page_dashboard()
        elif page == "New Billing":
            self.page_billing()
        elif page == "Sales Records":
            self.page_records()
        elif page == "Analytics":
            self.page_analytics()
        elif page == "Menu Management":
            self.page_menu()
        elif page == "Reports":
            self.page_reports()

    def card(self, parent, title, value, note, accent=COFFEE):
        box = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER,
                       highlightthickness=1, padx=17, pady=14)
        tk.Label(box, text=title.upper(), bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(box, text=value, bg=PANEL, fg=DARK,
                 font=("Segoe UI", 21, "bold")).pack(anchor="w", pady=(7, 1))
        tk.Label(box, text=note, bg=PANEL, fg=accent,
                 font=("Segoe UI", 9)).pack(anchor="w")
        return box

    def section_label(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=DARK,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(8, 10))

    def make_tree(self, parent, columns, headings, widths=None, height=10):
        wrap = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        tree = ttk.Treeview(wrap, columns=columns, show="headings", height=height)
        for i, col in enumerate(columns):
            tree.heading(col, text=headings[i])
            width = widths[i] if widths else 120
            tree.column(col, width=width, anchor="center")
        yscroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscroll.set)
        tree.pack(side="left", fill="both", expand=True, padx=(7, 0), pady=7)
        yscroll.pack(side="right", fill="y", padx=(0, 5), pady=7)
        return wrap, tree

    def button(self, parent, text, command, primary=True):
        return tk.Button(parent, text=text, command=command,
                         bg=COFFEE if primary else "#EDE1D3",
                         fg="white" if primary else DARK,
                         activebackground=ACCENT, activeforeground="white",
                         relief="flat", bd=0, padx=15, pady=9,
                         font=("Segoe UI", 9, "bold"), cursor="hand2")

    def page_dashboard(self):
        df = self.sales_df.copy()
        today = date.today().strftime("%Y-%m-%d")
        today_df = df[df["date"].astype(str) == today] if not df.empty else df
        revenue = float(today_df["grand_total"].sum()) if not today_df.empty else 0
        orders = int(today_df["order_id"].nunique()) if not today_df.empty else 0
        items = int(today_df["quantity"].sum()) if not today_df.empty else 0
        avg = revenue / orders if orders else 0

        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill="x")
        stats = [
            ("Today's Revenue", f"₹{revenue:,.2f}", "Sales collected today", COFFEE),
            ("Today's Orders", str(orders), "Unique bills generated", GREEN),
            ("Items Sold", str(items), "Total quantity today", ACCENT),
            ("Average Bill", f"₹{avg:,.2f}", "Revenue per order", COFFEE),
        ]
        for i, data in enumerate(stats):
            c = self.card(cards, *data)
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))
            cards.grid_columnconfigure(i, weight=1)

        lower = tk.Frame(self.content, bg=BG)
        lower.pack(fill="both", expand=True, pady=(22, 0))
        left = tk.Frame(lower, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = tk.Frame(lower, bg=PANEL, highlightbackground=BORDER, highlightthickness=1, width=300)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(left, text="Revenue snapshot", bg=PANEL, fg=DARK,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=17, pady=(14, 0))
        fig = Figure(figsize=(6.2, 3.3), dpi=100, facecolor=PANEL)
        ax = fig.add_subplot(111)
        if not df.empty:
            temp = df.copy()
            temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
            daily = temp.groupby(temp["date"].dt.date)["grand_total"].sum().tail(7)
            if len(daily):
                ax.plot([str(x)[5:] for x in daily.index], daily.values,
                        marker="o", linewidth=2.5, color=COFFEE)
                ax.fill_between(range(len(daily)), daily.values, alpha=.12, color=LATTE)
        ax.set_ylabel("Revenue (₹)", color=MUTED)
        ax.grid(axis="y", alpha=.2)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_facecolor(PANEL)
        ax.tick_params(colors=MUTED)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=left)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

        tk.Label(right, text="Quick overview", bg=PANEL, fg=DARK,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=17, pady=(15, 13))
        total_revenue = float(df["grand_total"].sum()) if not df.empty else 0
        total_orders = int(df["order_id"].nunique()) if not df.empty else 0
        menu_count = int(self.menu_df["available"].sum()) if not self.menu_df.empty else 0
        for label, value in [
            ("All-time revenue", f"₹{total_revenue:,.2f}"),
            ("All-time orders", str(total_orders)),
            ("Available menu items", str(menu_count)),
        ]:
            row = tk.Frame(right, bg=PANEL)
            row.pack(fill="x", padx=17, pady=8)
            tk.Label(row, text=label, bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 9)).pack(side="left")
            tk.Label(row, text=value, bg=PANEL, fg=DARK,
                     font=("Segoe UI", 10, "bold")).pack(side="right")
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", padx=17, pady=12)
        self.button(right, "＋  Create New Bill",
                    lambda: self.show_page("New Billing")).pack(fill="x", padx=17, pady=5)
        tk.Label(right, text="Tip: Use Analytics to explore\nsales trends and bestsellers.",
                 bg=PANEL, fg=MUTED, justify="left",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=17, pady=13)

    def page_billing(self):
        outer = tk.Frame(self.content, bg=BG)
        outer.pack(fill="both", expand=True)
        left = tk.Frame(outer, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = tk.Frame(outer, bg=PANEL, highlightbackground=BORDER, highlightthickness=1, width=360)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(left, text="Create a new order", bg=PANEL, fg=DARK,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=17, pady=(15, 10))
        form = tk.Frame(left, bg=PANEL)
        form.pack(fill="x", padx=17)
        tk.Label(form, text="Customer name", bg=PANEL, fg=MUTED).grid(row=0, column=0, sticky="w")
        self.customer_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.customer_var, width=25).grid(row=1, column=0, sticky="ew", pady=(4, 10), padx=(0, 10))
        tk.Label(form, text="Menu item", bg=PANEL, fg=MUTED).grid(row=0, column=1, sticky="w")
        available = self.menu_df[self.menu_df["available"] == True]
        self.item_var = tk.StringVar()
        names = available["item_name"].tolist()
        item_combo = ttk.Combobox(form, textvariable=self.item_var, values=names, state="readonly", width=24)
        item_combo.grid(row=1, column=1, sticky="ew", pady=(4, 10), padx=(0, 10))
        if names:
            item_combo.current(0)
        tk.Label(form, text="Quantity", bg=PANEL, fg=MUTED).grid(row=0, column=2, sticky="w")
        self.qty_var = tk.StringVar(value="1")
        ttk.Entry(form, textvariable=self.qty_var, width=8).grid(row=1, column=2, sticky="ew", pady=(4, 10))
        self.button(form, "Add item", self.add_to_cart).grid(row=1, column=3, padx=(10, 0), sticky="ew")
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        tk.Label(left, text="Order items", bg=PANEL, fg=DARK,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=17, pady=(5, 8))
        tree_wrap, self.cart_tree = self.make_tree(left,
            ("item", "qty", "price", "total"),
            ("ITEM", "QTY", "UNIT PRICE", "TOTAL"),
            (210, 60, 100, 110), 11)
        tree_wrap.pack(fill="both", expand=True, padx=17, pady=(0, 12))
        self.button(left, "Remove selected item", self.remove_cart_item, primary=False).pack(anchor="w", padx=17, pady=(0, 14))

        tk.Label(right, text="Bill summary", bg=PANEL, fg=DARK,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18, pady=(16, 14))
        self.subtotal_var = tk.StringVar(value="₹0.00")
        self.discount_var = tk.StringVar(value="0")
        self.total_var = tk.StringVar(value="₹0.00")
        self.payment_var = tk.StringVar(value="UPI")
        for label, variable in [("Subtotal", self.subtotal_var)]:
            row = tk.Frame(right, bg=PANEL); row.pack(fill="x", padx=18, pady=6)
            tk.Label(row, text=label, bg=PANEL, fg=MUTED).pack(side="left")
            tk.Label(row, textvariable=variable, bg=PANEL, fg=DARK, font=("Segoe UI", 10, "bold")).pack(side="right")
        tk.Label(right, text="Discount (₹)", bg=PANEL, fg=MUTED).pack(anchor="w", padx=18, pady=(14, 4))
        discount_entry = ttk.Entry(right, textvariable=self.discount_var)
        discount_entry.pack(fill="x", padx=18)
        discount_entry.bind("<KeyRelease>", lambda e: self.update_bill_totals())
        tk.Label(right, text="Payment method", bg=PANEL, fg=MUTED).pack(anchor="w", padx=18, pady=(13, 4))
        ttk.Combobox(right, textvariable=self.payment_var,
                     values=["UPI", "Cash", "Card"], state="readonly").pack(fill="x", padx=18)
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", padx=18, pady=16)
        row = tk.Frame(right, bg=PANEL); row.pack(fill="x", padx=18, pady=4)
        tk.Label(row, text="GRAND TOTAL", bg=PANEL, fg=DARK,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(row, textvariable=self.total_var, bg=PANEL, fg=COFFEE,
                 font=("Segoe UI", 19, "bold")).pack(side="right")
        self.button(right, "Complete sale  ✓", self.complete_sale).pack(fill="x", padx=18, pady=(20, 8))
        self.button(right, "Clear current bill", self.clear_cart, primary=False).pack(fill="x", padx=18)
        tk.Label(right, text="A unique order ID is generated\nwhen the sale is completed.",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 8), justify="left").pack(anchor="w", padx=18, pady=15)

    def add_to_cart(self):
        name = self.item_var.get()
        if not name:
            messagebox.showwarning("Select item", "Please select a menu item.")
            return
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid quantity", "Enter a whole number greater than zero.")
            return
        item = self.menu_df[self.menu_df["item_name"] == name].iloc[0]
        existing = next((x for x in self.cart if x["item_name"] == name), None)
        if existing:
            existing["quantity"] += qty
        else:
            self.cart.append({"item_name": name, "category": item["category"],
                              "quantity": qty, "unit_price": float(item["price"])})
        self.refresh_cart()
        self.qty_var.set("1")

    def refresh_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        for item in self.cart:
            total = item["quantity"] * item["unit_price"]
            self.cart_tree.insert("", "end", values=(
                item["item_name"], item["quantity"], f"₹{item['unit_price']:.2f}", f"₹{total:.2f}"
            ))
        self.update_bill_totals()

    def update_bill_totals(self):
        subtotal = sum(x["quantity"] * x["unit_price"] for x in self.cart)
        try:
            discount = max(0, float(self.discount_var.get() or 0))
        except ValueError:
            discount = 0
        discount = min(discount, subtotal)
        self.subtotal_var.set(f"₹{subtotal:,.2f}")
        self.total_var.set(f"₹{subtotal-discount:,.2f}")

    def remove_cart_item(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showinfo("Select item", "Select an item in the bill to remove it.")
            return
        index = self.cart_tree.index(selected[0])
        self.cart.pop(index)
        self.refresh_cart()

    def clear_cart(self):
        self.cart = []
        self.refresh_cart()
        self.discount_var.set("0")
        self.customer_var.set("")

    def complete_sale(self):
        if not self.cart:
            messagebox.showwarning("Empty bill", "Add at least one item before completing the sale.")
            return
        try:
            discount = max(0, float(self.discount_var.get() or 0))
        except ValueError:
            messagebox.showerror("Invalid discount", "Enter a valid discount amount.")
            return
        subtotal = sum(x["quantity"] * x["unit_price"] for x in self.cart)
        if discount > subtotal:
            messagebox.showerror("Invalid discount", "Discount cannot exceed the subtotal.")
            return
        order_id = "RBS-" + datetime.now().strftime("%y%m%d") + "-" + uuid.uuid4().hex[:5].upper()
        now = datetime.now()
        customer = self.customer_var.get().strip() or "Walk-in Customer"
        rows = []
        for item in self.cart:
            line_total = item["quantity"] * item["unit_price"]
            rows.append({
                "order_id": order_id, "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"), "customer": customer,
                "item_name": item["item_name"], "category": item["category"],
                "quantity": item["quantity"], "unit_price": item["unit_price"],
                "line_total": line_total, "payment_method": self.payment_var.get(),
                "subtotal": subtotal, "discount": discount,
                "grand_total": subtotal - discount
            })
        self.sales_df = pd.concat([self.sales_df, pd.DataFrame(rows)], ignore_index=True)
        self.save_sales()
        messagebox.showinfo("Sale completed",
            f"Payment recorded successfully!\n\nOrder ID: {order_id}\nCustomer: {customer}\nTotal: ₹{subtotal-discount:,.2f}")
        self.cart = []
        self.show_page("New Billing")

    def page_records(self):
        top = tk.Frame(self.content, bg=BG)
        top.pack(fill="x", pady=(0, 12))
        tk.Label(top, text="Search", bg=BG, fg=MUTED).pack(side="left")
        self.record_search = tk.StringVar()
        search = ttk.Entry(top, textvariable=self.record_search, width=28)
        search.pack(side="left", padx=8)
        tk.Label(top, text="Date (YYYY-MM-DD)", bg=BG, fg=MUTED).pack(side="left", padx=(15, 4))
        self.record_date = tk.StringVar()
        date_entry = ttk.Entry(top, textvariable=self.record_date, width=15)
        date_entry.pack(side="left", padx=5)
        self.button(top, "Apply filters", self.refresh_records).pack(side="left", padx=8)
        self.button(top, "Reset", lambda: (self.record_search.set(""), self.record_date.set(""), self.refresh_records()), primary=False).pack(side="left")
        self.records_count = tk.Label(top, text="", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self.records_count.pack(side="right")

        wrap, self.records_tree = self.make_tree(self.content,
            ("order", "date", "time", "customer", "items", "qty", "payment", "total"),
            ("ORDER ID", "DATE", "TIME", "CUSTOMER", "ITEM", "QTY", "PAYMENT", "BILL TOTAL"),
            (165, 95, 85, 130, 145, 55, 85, 105), 18)
        wrap.pack(fill="both", expand=True)
        self.refresh_records()

    def refresh_records(self):
        if not hasattr(self, "records_tree") or not self.records_tree.winfo_exists():
            return
        for row in self.records_tree.get_children():
            self.records_tree.delete(row)
        df = self.sales_df.copy()
        if not df.empty:
            query = self.record_search.get().strip().lower()
            day = self.record_date.get().strip()
            if query:
                mask = df.astype(str).apply(lambda col: col.str.lower().str.contains(query, na=False)).any(axis=1)
                df = df[mask]
            if day:
                df = df[df["date"].astype(str).str.contains(day, na=False)]
            # One row per item, with full order amount shown on each item line.
            for _, r in df.sort_values(["date", "time"], ascending=False).iterrows():
                self.records_tree.insert("", "end", values=(
                    r["order_id"], r["date"], r["time"], r["customer"], r["item_name"],
                    int(r["quantity"]), r["payment_method"], f"₹{float(r['grand_total']):,.2f}"
                ))
        self.records_count.configure(text=f"{len(df)} item record(s)")

    def page_analytics(self):
        df = self.sales_df.copy()
        if df.empty:
            tk.Label(self.content, text="No sales data available yet. Complete a bill to see analytics.",
                     bg=BG, fg=MUTED, font=("Segoe UI", 12)).pack(pady=40)
            return
        df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")
        revenue = df.groupby("date_dt")["grand_total"].max().sort_index()
        item_sales = df.groupby("item_name")["quantity"].sum().sort_values(ascending=False).head(7)
        category_sales = df.groupby("category")["line_total"].sum().sort_values(ascending=False)

        # NumPy is used for summary statistics and trend calculations.
        values = revenue.to_numpy(dtype=float)
        avg_daily = float(np.mean(values)) if len(values) else 0
        std_daily = float(np.std(values)) if len(values) else 0
        summary = tk.Frame(self.content, bg=BG)
        summary.pack(fill="x", pady=(0, 12))
        for i, (label, val) in enumerate([
            ("Average daily revenue", f"₹{avg_daily:,.2f}"),
            ("Revenue standard deviation", f"₹{std_daily:,.2f}"),
            ("Best-selling item", str(item_sales.index[0]) if len(item_sales) else "—"),
        ]):
            c = self.card(summary, label, val, "Calculated from saved CSV data")
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))
            summary.grid_columnconfigure(i, weight=1)

        charts = tk.Frame(self.content, bg=BG)
        charts.pack(fill="both", expand=True)
        charts.grid_columnconfigure(0, weight=1)
        charts.grid_columnconfigure(1, weight=1)
        charts.grid_rowconfigure(0, weight=1)
        charts.grid_rowconfigure(1, weight=1)

        fig1 = Figure(figsize=(5.4, 2.5), dpi=100, facecolor=PANEL)
        ax1 = fig1.add_subplot(111)
        ax1.bar([d.strftime("%d %b") for d in revenue.index], revenue.values, color=COFFEE)
        ax1.set_title("Daily revenue", color=DARK, fontsize=11, fontweight="bold")
        ax1.set_ylabel("₹")
        ax1.tick_params(axis="x", rotation=25, labelsize=8)
        ax1.grid(axis="y", alpha=.2)
        ax1.spines[["top", "right"]].set_visible(False)
        fig1.tight_layout()
        self.embed_chart(charts, fig1, 0, 0)

        fig2 = Figure(figsize=(5.4, 2.5), dpi=100, facecolor=PANEL)
        ax2 = fig2.add_subplot(111)
        if len(item_sales):
            ax2.barh(item_sales.index[::-1], item_sales.values[::-1], color=ACCENT)
        ax2.set_title("Top-selling items (quantity)", color=DARK, fontsize=11, fontweight="bold")
        ax2.grid(axis="x", alpha=.2)
        ax2.spines[["top", "right", "left"]].set_visible(False)
        fig2.tight_layout()
        self.embed_chart(charts, fig2, 0, 1)

        fig3 = Figure(figsize=(5.4, 2.5), dpi=100, facecolor=PANEL)
        ax3 = fig3.add_subplot(111)
        if len(category_sales):
            ax3.pie(category_sales.values, labels=category_sales.index, autopct="%1.0f%%",
                    startangle=90, textprops={"fontsize": 8},
                    colors=["#7B4B2A", "#C87941", "#D8B894", "#527A55", "#A77B5A"])
        ax3.set_title("Revenue by category", color=DARK, fontsize=11, fontweight="bold")
        fig3.tight_layout()
        self.embed_chart(charts, fig3, 1, 0)

        fig4 = Figure(figsize=(5.4, 2.5), dpi=100, facecolor=PANEL)
        ax4 = fig4.add_subplot(111)
        payment = df.groupby("payment_method")["grand_total"].max()
        ax4.bar(payment.index, payment.values, color=GREEN)
        ax4.set_title("Revenue by payment method", color=DARK, fontsize=11, fontweight="bold")
        ax4.set_ylabel("₹")
        ax4.grid(axis="y", alpha=.2)
        ax4.spines[["top", "right"]].set_visible(False)
        fig4.tight_layout()
        self.embed_chart(charts, fig4, 1, 1)

    def embed_chart(self, parent, fig, row, col):
        holder = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        holder.grid(row=row, column=col, sticky="nsew", padx=(0, 10), pady=(0, 10))
        canvas = FigureCanvasTkAgg(fig, master=holder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def page_menu(self):
        top = tk.Frame(self.content, bg=BG)
        top.pack(fill="x", pady=(0, 12))
        self.button(top, "＋ Add menu item", self.add_menu_item).pack(side="left")
        self.button(top, "Edit selected", self.edit_menu_item, primary=False).pack(side="left", padx=8)
        self.button(top, "Delete selected", self.delete_menu_item, primary=False).pack(side="left")
        self.button(top, "Toggle availability", self.toggle_menu_item, primary=False).pack(side="left", padx=8)
        wrap, self.menu_tree = self.make_tree(self.content,
            ("id", "name", "category", "price", "availability"),
            ("ITEM ID", "ITEM NAME", "CATEGORY", "PRICE", "STATUS"),
            (100, 250, 180, 110, 120), 18)
        wrap.pack(fill="both", expand=True)
        self.refresh_menu()

    def refresh_menu(self):
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)
        for _, r in self.menu_df.iterrows():
            self.menu_tree.insert("", "end", values=(
                r["item_id"], r["item_name"], r["category"],
                f"₹{float(r['price']):.2f}", "Available" if r["available"] else "Unavailable"
            ))

    def menu_dialog(self, title, initial=None):
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        fields = {}
        labels = ["Item name", "Category", "Price (₹)"]
        defaults = initial or {}
        for i, label in enumerate(labels):
            tk.Label(win, text=label, bg=BG, fg=DARK,
                     font=("Segoe UI", 9, "bold")).grid(row=i, column=0, sticky="w", padx=18, pady=(15 if i == 0 else 8, 3))
            var = tk.StringVar(value=str(defaults.get(["item_name", "category", "price"][i], "")))
            entry = ttk.Entry(win, textvariable=var, width=30)
            entry.grid(row=i, column=1, padx=18, pady=(15 if i == 0 else 8, 3))
            fields[label] = var
        result = {}
        def save():
            try:
                name = fields["Item name"].get().strip()
                category = fields["Category"].get().strip()
                price = float(fields["Price (₹)"].get())
                if not name or not category or price <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid details", "Enter a name, category and price greater than zero.", parent=win)
                return
            result.update({"item_name": name, "category": category, "price": price})
            win.destroy()
        self.button(win, "Save item", save).grid(row=3, column=0, columnspan=2, pady=18)
        self.wait_window(win)
        return result or None

    def add_menu_item(self):
        data = self.menu_dialog("Add menu item")
        if data:
            new_id = "I" + uuid.uuid4().hex[:5].upper()
            row = pd.DataFrame([{"item_id": new_id, **data, "available": True}])
            self.menu_df = pd.concat([self.menu_df, row], ignore_index=True)
            self.save_menu()
            self.refresh_menu()
            messagebox.showinfo("Menu updated", "New item added successfully.")

    def selected_menu_index(self):
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showinfo("Select item", "Please select a menu item first.")
            return None
        item_id = self.menu_tree.item(selected[0], "values")[0]
        matches = self.menu_df.index[self.menu_df["item_id"].astype(str) == str(item_id)]
        return int(matches[0]) if len(matches) else None

    def edit_menu_item(self):
        idx = self.selected_menu_index()
        if idx is None:
            return
        initial = self.menu_df.loc[idx].to_dict()
        data = self.menu_dialog("Edit menu item", initial)
        if data:
            for key, value in data.items():
                self.menu_df.at[idx, key] = value
            self.save_menu()
            self.refresh_menu()

    def delete_menu_item(self):
        idx = self.selected_menu_index()
        if idx is None:
            return
        if messagebox.askyesno("Delete menu item", "Delete this item from the menu?"):
            self.menu_df = self.menu_df.drop(index=idx).reset_index(drop=True)
            self.save_menu()
            self.refresh_menu()

    def toggle_menu_item(self):
        idx = self.selected_menu_index()
        if idx is None:
            return
        self.menu_df.at[idx, "available"] = not bool(self.menu_df.at[idx, "available"])
        self.save_menu()
        self.refresh_menu()

    def page_reports(self):
        tk.Label(self.content, text="Export your café data for submission, backup or further analysis.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 18))
        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill="x")
        options = [
            ("Sales report", "Export all transaction line-items to a CSV file.",
             self.export_sales),
            ("Menu report", "Export the current café menu and availability.",
             self.export_menu),
            ("Daily summary", "Export revenue and order totals grouped by date.",
             self.export_daily_summary),
        ]
        for title, desc, command in options:
            box = tk.Frame(cards, bg=PANEL, highlightbackground=BORDER,
                           highlightthickness=1, padx=20, pady=20)
            box.pack(fill="x", pady=8)
            tk.Label(box, text="⇩", bg=PANEL, fg=ACCENT,
                     font=("Segoe UI", 22, "bold")).pack(side="left", padx=(0, 18))
            info = tk.Frame(box, bg=PANEL)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=title, bg=PANEL, fg=DARK,
                     font=("Segoe UI", 12, "bold")).pack(anchor="w")
            tk.Label(info, text=desc, bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))
            self.button(box, "Export CSV", command).pack(side="right")

        tk.Frame(self.content, bg=PANEL, highlightbackground=BORDER,
                 highlightthickness=1, padx=18, pady=15).pack(fill="x", pady=(18, 0))
        tk.Label(self.content.winfo_children()[-1],
                 text=f"Data folder: {DATA_DIR}\nSales file: sales.csv  •  Menu file: menu.csv",
                 bg=PANEL, fg=MUTED, justify="left",
                 font=("Segoe UI", 9)).pack(anchor="w")

    def export_dataframe(self, df, default_name):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile=default_name,
            filetypes=[("CSV files", "*.csv")])
        if path:
            df.to_csv(path, index=False)
            messagebox.showinfo("Export complete", f"Report saved successfully:\n{path}")

    def export_sales(self):
        self.export_dataframe(self.load_sales(), "RBS_Cafe_Sales_Report.csv")

    def export_menu(self):
        self.export_dataframe(self.load_menu(), "RBS_Cafe_Menu_Report.csv")

    def export_daily_summary(self):
        df = self.load_sales()
        if df.empty:
            messagebox.showinfo("No data", "There are no sales to summarise yet.")
            return
        summary = df.groupby("date").agg(
            orders=("order_id", "nunique"),
            items_sold=("quantity", "sum"),
            revenue=("grand_total", "max")
        ).reset_index()
        self.export_dataframe(summary, "RBS_Cafe_Daily_Summary.csv")


if __name__ == "__main__":
    app = CafeApp()
    app.mainloop()
