import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import os


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker Dashboard")

        self.file_name = "expenses.csv"
        self.load_expenses()

        # Expense Input Section
        self.input_frame = ttk.LabelFrame(root, text="Add Expense")
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        self.category_label = ttk.Label(self.input_frame, text="Category:")
        self.category_label.grid(row=0, column=0, padx=5, pady=5)

        self.category = ttk.Combobox(self.input_frame,
                                     values=["Food", "Transport", "Entertainment", "Utilities", "Other"])
        self.category.grid(row=0, column=1, padx=5, pady=5)

        self.amount_label = ttk.Label(self.input_frame, text="Amount:")
        self.amount_label.grid(row=1, column=0, padx=5, pady=5)

        self.amount_entry = ttk.Entry(self.input_frame)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        self.comment_label = ttk.Label(self.input_frame, text="Comment:")
        self.comment_label.grid(row=2, column=0, padx=5, pady=5)

        self.comment_entry = ttk.Entry(self.input_frame)
        self.comment_entry.grid(row=2, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(self.input_frame, text="Add Expense", command=self.add_expense)
        self.add_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        # Filter Section
        self.filter_frame = ttk.LabelFrame(root, text="Filter Expenses")
        self.filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        self.filters = {}
        for col, index in zip(self.expenses.columns, range(len(self.expenses.columns))):
            label = ttk.Label(self.filter_frame, text=col)
            label.grid(row=0, column=index, padx=5, pady=5)

            if col == "Date":
                filter_widget = ttk.Entry(self.filter_frame)
                filter_widget.grid(row=1, column=index, padx=5, pady=5)
            else:
                filter_values = self.expenses[col].dropna().unique().tolist()
                filter_widget = ttk.Combobox(self.filter_frame, values=filter_values)
                filter_widget.grid(row=1, column=index, padx=5, pady=5)

            self.filters[col] = filter_widget

        filter_button = ttk.Button(self.filter_frame, text="Apply Filters", command=self.apply_filters)
        filter_button.grid(row=2, column=0, columnspan=len(self.expenses.columns), padx=5, pady=5, sticky='ew')

        clear_button = ttk.Button(self.filter_frame, text="Clear Filters", command=self.clear_filters)
        clear_button.grid(row=3, column=0, columnspan=len(self.expenses.columns), padx=5, pady=5, sticky='ew')

        # Summary Section
        self.summary_frame = ttk.LabelFrame(root, text="Expense Summary")
        self.summary_frame.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

        self.summary_tree = None
        self.show_expenses(self.summary_frame, self.expenses)

        # Make the summary section expand to fill the available space
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def load_expenses(self):
        if os.path.exists(self.file_name):
            self.expenses = pd.read_csv(self.file_name, parse_dates=["Date"])
        else:
            self.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Comment"])

    def save_expenses(self):
        self.expenses.to_csv(self.file_name, index=False)

    def add_expense(self):
        category = self.category.get()
        amount = self.amount_entry.get()
        comment = self.comment_entry.get()

        if category and amount:
            try:
                amount = float(amount)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid amount.")
                return

            date = datetime.now().strftime("%Y-%m-%d")
            new_expense = {"Date": date, "Category": category, "Amount": amount, "Comment": comment}
            self.expenses = pd.concat([self.expenses, pd.DataFrame([new_expense])], ignore_index=True)
            self.save_expenses()
            messagebox.showinfo("Success", "Expense added successfully.")
            self.category.set("")
            self.amount_entry.delete(0, tk.END)
            self.comment_entry.delete(0, tk.END)
            self.show_expenses(self.summary_frame, self.expenses)  # Update the summary after adding an expense
        else:
            messagebox.showerror("Missing Information", "Please fill out all fields.")

    def apply_filters(self):
        filtered_expenses = self.expenses.copy()
        for col, widget in self.filters.items():
            value = widget.get()
            if value:
                if col == "Date":
                    try:
                        value = pd.to_datetime(value).date()
                        filtered_expenses = filtered_expenses[filtered_expenses[col].dt.date == value]
                    except ValueError:
                        messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
                        return
                else:
                    filtered_expenses = filtered_expenses[filtered_expenses[col] == value]

        self.show_expenses(self.summary_frame, filtered_expenses)

    def clear_filters(self):
        for col, widget in self.filters.items():
            if isinstance(widget, ttk.Combobox):
                widget.set('')
            elif isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)

        self.show_expenses(self.summary_frame, self.expenses)

    def show_expenses(self, window, data):
        if self.summary_tree:
            self.summary_tree.destroy()

        cols = list(data.columns)
        tree = ttk.Treeview(window, columns=cols, show='headings')
        tree.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for index, row in data.iterrows():
            tree.insert("", "end", values=list(row))

        scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        tree.configure(yscrollcommand=scrollbar.set)

        self.summary_tree = tree


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
