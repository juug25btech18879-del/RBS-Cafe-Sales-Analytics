# RBS Cafe – Retail Sales Management & Analytics Dashboard

A desktop mini-project built with Python Tkinter, Pandas, NumPy, CSV and Matplotlib.

## Features
- Dashboard with today's revenue, order count, items sold and average bill.
- Billing screen with cart, quantity, discount and payment method.
- Automatic order IDs and persistent CSV storage.
- Searchable sales records with date filter.
- Analytics: daily revenue, top-selling products, category share and payment method charts.
- Menu management: add, edit, delete and toggle item availability.
- Export sales, menu and daily summary reports to CSV.
- Sample transactions are created automatically on first launch.

## Requirements
- Python 3.10 or newer
- pandas
- numpy
- matplotlib
- tkinter (included with most standard Windows Python installations)

## Setup (Windows / VS Code)
1. Extract the ZIP file.
2. Open the `RBS_Cafe_Project` folder in VS Code.
3. Open Terminal → New Terminal.
4. Install libraries:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Run the application:

   ```bash
   python app.py
   ```

The first run creates a `data` folder containing `menu.csv` and `sales.csv`.
Sales and menu changes are saved automatically. Do not delete the `data` folder if you want to retain your records.

## CSV structure
- `sales.csv`: one row per item in an order. Rows in the same order share an order ID and bill total.
- `menu.csv`: item ID, item name, category, price and availability.

## Suggested project explanation
"RBS Cafe is a Python-based retail sales dashboard. Tkinter is used to create the graphical interface. Pandas reads, filters and groups the CSV sales data, NumPy calculates summary statistics, and Matplotlib displays sales charts. The application supports billing, sales history, menu management and report export. CSV files provide lightweight local data storage."

## Important note for demonstration
The initial sample sales are dated relative to the day the app is first run, so charts and records have demonstration data. New bills are saved with the current date and remain available after restarting the app.
