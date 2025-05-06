import bcrypt
from pymongo import MongoClient
import datetime
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar

# MongoDB setup
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['finance_manager']
    users_collection = db['users']
    transactions_collection = db['transactions']
    budgets_collection = db['budgets']  # For budgeting feature
except Exception as e:
    print(f"Could not connect to the database: {e}")

# Global variable to store logged-in username
logged_in_username = None

# Register User
def register_user():
    username = username_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()
    email = email_entry.get()
    phone = phone_entry.get()

    # Input validation
    if not username or not password:
        messagebox.showwarning("Input Error", "Username and password cannot be empty!")
        return

    if password != confirm_password:
        messagebox.showerror("Password Error", "Passwords do not match!")
        return

    # Check if the user already exists
    if users_collection.find_one({"username": username}):
        messagebox.showerror("Registration Error", "Username already exists!")
        return

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_data = {
        "username": username,
        "password": hashed_pw,
        "email": email,
        "phone": phone,
        "description": ""
    }
    users_collection.insert_one(user_data)
    messagebox.showinfo("Registration", f"User {username} registered successfully!")

# Login User
def login_user():
    global logged_in_username
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Input Error", "Username and password cannot be empty!")
        return

    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        logged_in_username = username  # Store logged-in username
        messagebox.showinfo("Login", "Login successful!")
        main_window()
    else:
        messagebox.showerror("Login", "Login failed!")

# Main Window
def main_window():
    clear_window()
    label = tk.Label(root, text="Welcome to the Finance Manager", font=("Arial", 16))
    label.pack(pady=10)

    add_button = tk.Button(root, text="Add Transaction", command=add_transaction_window)
    add_button.pack(pady=5)

    view_button = tk.Button(root, text="View Transactions", command=view_transactions)
    view_button.pack(pady=5)

    set_budget_button = tk.Button(root, text="Set Budget", command=set_budget_window)
    set_budget_button.pack(pady=5)

# Add Transaction Window
def add_transaction_window():
    clear_window()
    label = tk.Label(root, text="Add Transaction", font=("Arial", 16))
    label.pack(pady=10)

    amount_label = tk.Label(root, text="Amount:")
    amount_label.pack()
    amount_entry = tk.Entry(root)
    amount_entry.pack()

    category_label = tk.Label(root, text="Category:")
    category_label.pack()
    category_entry = tk.Entry(root)
    category_entry.pack()

    type_label = tk.Label(root, text="Transaction Type (income/expense):")
    type_label.pack()
    type_entry = tk.Entry(root)
    type_entry.pack()

    submit_button = tk.Button(root, text="Submit", command=lambda: submit_transaction(amount_entry.get(), category_entry.get(), type_entry.get()))
    submit_button.pack(pady=10)

    back_button = tk.Button(root, text="Back", command=main_window)
    back_button.pack(pady=5)

def submit_transaction(amount, category, transaction_type):
    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for the amount.")
        return

    if transaction_type not in ["income", "expense"]:
        messagebox.showerror("Invalid Input", "Transaction type must be 'income' or 'expense'.")
        return

    # Check budget before allowing transaction submission
    if transaction_type == "expense":
        budget = check_budget(category)
        total_expenses = sum(tx['amount'] for tx in transactions_collection.find({"username": logged_in_username, "transaction_type": "expense"}))

        if total_expenses + amount > budget:
            messagebox.showwarning("Budget Alert", "This transaction exceeds your budget for this category!")

    transaction_data = {
        "username": logged_in_username,  # Use the stored username
        "amount": amount,
        "category": category,
        "transaction_type": transaction_type,
        "date": datetime.datetime.now()
    }
    transactions_collection.insert_one(transaction_data)
    messagebox.showinfo("Transaction", "Transaction added successfully!")
    main_window()

# View Transactions
def view_transactions():
    clear_window()
    transactions = list(transactions_collection.find({"username": logged_in_username}))
    
    label = tk.Label(root, text="Your Transactions", font=("Arial", 16))
    label.pack(pady=10)

    # Create a Listbox to display transactions
    transaction_listbox = Listbox(root, width=50)
    transaction_listbox.pack(pady=10)

    total_income = 0.0
    total_expense = 0.0

    for transaction in transactions:
        transaction_listbox.insert(tk.END, f"Date: {transaction['date']}, Amount: {transaction['amount']}, "
                                             f"Category: {transaction['category']}, Type: {transaction['transaction_type']}")
        # Calculate total income and expenses
        if transaction['transaction_type'] == "income":
            total_income += transaction['amount']
        elif transaction['transaction_type'] == "expense":
            total_expense += transaction['amount']

    # Scrollbar for the Listbox
    scrollbar = Scrollbar(root)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    transaction_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=transaction_listbox.yview)

    delete_button = tk.Button(root, text="Delete Selected Transaction", command=lambda: delete_transaction(transaction_listbox.curselection()))
    delete_button.pack(pady=5)

    back_button = tk.Button(root, text="Back", command=main_window)
    back_button.pack(pady=5)

    # Show total income and expenses
    total_message = f"Total Income: ${total_income:.2f}\nTotal Expense: ${total_expense:.2f}"
    messagebox.showinfo("Totals", total_message)

def delete_transaction(selection):
    if selection:
        index = selection[0]
        transactions = list(transactions_collection.find({"username": logged_in_username}))
        transaction = transactions[index]
        transactions_collection.delete_one({"_id": transaction["_id"]})
        messagebox.showinfo("Delete Transaction", "Transaction deleted successfully!")
        view_transactions()
    else:
        messagebox.showwarning("Delete Transaction", "Please select a transaction to delete.")

# Budgeting Functions
def set_budget_window():
    clear_window()
    label = tk.Label(root, text="Set Budget", font=("Arial", 16))
    label.pack(pady=10)

    category_label = tk.Label(root, text="Category:")
    category_label.pack()
    category_entry = tk.Entry(root)
    category_entry.pack()

    amount_label = tk.Label(root, text="Budget Amount:")
    amount_label.pack()
    amount_entry = tk.Entry(root)
    amount_entry.pack()

    submit_button = tk.Button(root, text="Set Budget", command=lambda: set_budget(category_entry.get(), amount_entry.get()))
    submit_button.pack(pady=10)

    back_button = tk.Button(root, text="Back", command=main_window)
    back_button.pack(pady=5)

def set_budget(category, amount):
    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for the budget.")
        return

    budget_data = {
        "username": logged_in_username,
        "category": category,
        "amount": amount
    }
    budgets_collection.update_one(
        {"username": logged_in_username, "category": category},
        {"$set": budget_data},
        upsert=True
    )
    messagebox.showinfo("Budget", f"Budget for {category} set to ${amount:.2f}!")
    main_window()

def check_budget(category):
    budget = budgets_collection.find_one({"username": logged_in_username, "category": category})
    if budget:
        return budget['amount']
    return float('inf')  # No budget set, return infinity

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

# Tkinter setup
root = tk.Tk()
root.title("Personal Finance Manager")
root.geometry("500x500")

# User registration/login interface
label = tk.Label(root, text="Username:")
label.pack()
username_entry = tk.Entry(root)
username_entry.pack()

label = tk.Label(root, text="Password:")
label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

label = tk.Label(root, text="Confirm Password:")
label.pack()
confirm_password_entry = tk.Entry(root, show="*")
confirm_password_entry.pack()

label = tk.Label(root, text="Email:")
label.pack()
email_entry = tk.Entry(root)
email_entry.pack()

label = tk.Label(root, text="Phone:")
label.pack()
phone_entry = tk.Entry(root)
phone_entry.pack()

login_button = tk.Button(root, text="Login", command=login_user)
login_button.pack(pady=10)

register_button = tk.Button(root, text="Register", command=register_user)
register_button.pack(pady=10)

root.mainloop()
