import os
import json
import uuid
import datetime
import questionary

# File paths for persistent data
SETUP_FILE = "setup.json"
TRANSACTION_FILE = "transactions.json"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    print("=" * 60)
    print("      $$$  Money Maestro - Finance Manager CLI  $$$")
    print("=" * 60)
    print()


# --- Data Persistence Functions ---

def load_setup():
    if os.path.exists(SETUP_FILE):
        with open(SETUP_FILE, "r") as f:
            return json.load(f)
    else:
        return {"banks": []}


def save_setup(data):
    with open(SETUP_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_transactions():
    if os.path.exists(TRANSACTION_FILE):
        with open(TRANSACTION_FILE, "r") as f:
            return json.load(f)
    else:
        return []


def save_transactions(transactions):
    with open(TRANSACTION_FILE, "w") as f:
        json.dump(transactions, f, indent=4)


# --- Initial Setup Process ---

def setup_initial():
    clear_screen()
    print_header()
    print("Welcome to Finance Manager CLI Setup!")
    setup_data = {"banks": []}
    while True:
        bank_name = questionary.text("Enter bank name (or leave blank to finish):").ask()
        if not bank_name:
            break
        bank = {"name": bank_name, "accounts": []}
        while True:
            account_name = questionary.text(
                f"Enter account name for '{bank_name}' (or leave blank to finish):"
            ).ask()
            if not account_name:
                break
            initial_balance_str = questionary.text(
                f"Enter initial balance for account '{account_name}' (default 0):"
            ).ask()
            try:
                initial_balance = float(initial_balance_str) if initial_balance_str else 0.0
            except ValueError:
                initial_balance = 0.0
            bank["accounts"].append({"name": account_name, "balance": initial_balance})
        setup_data["banks"].append(bank)
    save_setup(setup_data)
    print("Setup complete! Restarting application...")
    input("Press Enter to continue...")


# --- Transaction & Financial Operations ---

def add_transaction(setup_data, transactions):
    clear_screen()
    print_header()
    if not setup_data["banks"]:
        print("No banks available. Please set up banks and accounts first.")
        input("Press Enter to return to menu...")
        return

    # Build bank choices with total balance displayed
    bank_choices = []
    for bank in setup_data["banks"]:
        total_balance = sum(account["balance"] for account in bank["accounts"])
        bank_choices.append(questionary.Choice(
            title=f"{bank['name']} (Total: ${total_balance:.2f})", value=bank
        ))
    selected_bank = questionary.select("Select bank for transaction:", choices=bank_choices).ask()
    if not selected_bank["accounts"]:
        print("No accounts available for this bank.")
        input("Press Enter to return to menu...")
        return

    # Build account choices with balance info
    account_choices = []
    for account in selected_bank["accounts"]:
        account_choices.append(questionary.Choice(
            title=f"{account['name']} (Balance: ${account['balance']:.2f})", value=account
        ))
    selected_account = questionary.select("Select account:", choices=account_choices).ask()

    transaction_type = questionary.select("Select transaction type:", choices=["Deposit", "Withdrawal"]).ask()
    amount_str = questionary.text("Enter amount:").ask()
    try:
        amount = float(amount_str)
    except ValueError:
        print("Invalid amount.")
        input("Press Enter to return to menu...")
        return
    description = questionary.text("Enter description:").ask()

    transaction = {
        "id": uuid.uuid4().hex,
        "bank": selected_bank["name"],
        "account": selected_account["name"],
        "type": transaction_type.lower(),
        "amount": amount,
        "description": description,
        "date": datetime.datetime.now().isoformat(),
    }

    # Update the account balance
    if transaction_type.lower() == "deposit":
        selected_account["balance"] += amount
    else:
        selected_account["balance"] -= amount

    transactions.append(transaction)
    save_transactions(transactions)
    save_setup(setup_data)
    print("Transaction added successfully!")
    input("Press Enter to return to menu...")


def edit_transaction(setup_data, transactions):
    clear_screen()
    print_header()
    if not transactions:
        print("No transactions to edit.")
        input("Press Enter to return to menu...")
        return

    # List transactions for selection
    choices = []
    for tx in transactions:
        choices.append(
            f"{tx['date'][:19]} | {tx['bank']} - {tx['account']} | {tx['type'].capitalize()} ${tx['amount']} | {tx['description']}"
        )
    tx_choice = questionary.select("Select transaction to edit:", choices=choices).ask()
    tx_index = choices.index(tx_choice)
    tx = transactions[tx_index]

    # Reverse original transaction effect
    bank = next((b for b in setup_data["banks"] if b["name"] == tx["bank"]), None)
    if bank:
        account = next((a for a in bank["accounts"] if a["name"] == tx["account"]), None)
        if account:
            if tx["type"] == "deposit":
                account["balance"] -= tx["amount"]
            else:
                account["balance"] += tx["amount"]

    # Get new details from user
    new_type = questionary.select(
        "Select new transaction type:", choices=["Deposit", "Withdrawal"], default=tx["type"].capitalize()
    ).ask()
    new_amount_str = questionary.text("Enter new amount:", default=str(tx["amount"])).ask()
    try:
        new_amount = float(new_amount_str)
    except ValueError:
        print("Invalid amount. Aborting edit.")
        input("Press Enter to return to menu...")
        return
    new_description = questionary.text("Enter new description:", default=tx["description"]).ask()

    tx["type"] = new_type.lower()
    tx["amount"] = new_amount
    tx["description"] = new_description
    tx["date"] = datetime.datetime.now().isoformat()

    # Re-apply new transaction effect
    if bank and account:
        if tx["type"] == "deposit":
            account["balance"] += new_amount
        else:
            account["balance"] -= new_amount

    save_transactions(transactions)
    save_setup(setup_data)
    print("Transaction edited successfully!")
    input("Press Enter to return to menu...")


def refund_transaction(setup_data, transactions):
    clear_screen()
    print_header()
    if not transactions:
        print("No transactions available for refund.")
        input("Press Enter to return to menu...")
        return

    # Let user select a transaction to refund
    choices = []
    for tx in transactions:
        choices.append(
            f"{tx['date'][:19]} | {tx['bank']} - {tx['account']} | {tx['type'].capitalize()} ${tx['amount']} | {tx['description']}"
        )
    tx_choice = questionary.select("Select transaction to refund:", choices=choices).ask()
    tx_index = choices.index(tx_choice)
    original_tx = transactions[tx_index]

    # Ask for refund amount with default as full amount
    refund_amount_str = questionary.text(
        "Enter refund amount (default full amount):", default=str(original_tx["amount"])
    ).ask()
    try:
        refund_amount = float(refund_amount_str) if refund_amount_str else original_tx["amount"]
    except ValueError:
        refund_amount = original_tx["amount"]
    if refund_amount > original_tx["amount"]:
        refund_amount = original_tx["amount"]

    # Determine refund type: flip deposit/withdrawal
    refund_type = "withdrawal" if original_tx["type"] == "deposit" else "deposit"
    refund_tx = {
        "id": uuid.uuid4().hex,
        "bank": original_tx["bank"],
        "account": original_tx["account"],
        "type": refund_type,
        "amount": refund_amount,
        "description": f"Refund for transaction {original_tx['id']}",
        "date": datetime.datetime.now().isoformat(),
        "refunded_transaction_id": original_tx["id"],
    }

    # Update account balance for the refund
    bank = next((b for b in setup_data["banks"] if b["name"] == original_tx["bank"]), None)
    if bank:
        account = next((a for a in bank["accounts"] if a["name"] == original_tx["account"]), None)
        if account:
            if refund_type == "deposit":
                account["balance"] += refund_amount
            else:
                account["balance"] -= refund_amount

    transactions.append(refund_tx)
    save_transactions(transactions)
    save_setup(setup_data)
    print("Refund transaction added successfully!")
    input("Press Enter to return to menu...")


def view_transactions(transactions):
    clear_screen()
    print_header()
    if not transactions:
        print("No transactions available.")
        input("Press Enter to return to menu...")
        return

    filter_choice = questionary.select(
        "View transactions:", choices=["All", "Filter by Bank", "Filter by Account"]
    ).ask()

    filtered = transactions
    if filter_choice == "Filter by Bank":
        banks = list(set(tx["bank"] for tx in transactions))
        bank_selected = questionary.select("Select bank:", choices=banks).ask()
        filtered = [tx for tx in transactions if tx["bank"] == bank_selected]
    elif filter_choice == "Filter by Account":
        banks = list(set(tx["bank"] for tx in transactions))
        bank_selected = questionary.select("Select bank:", choices=banks).ask()
        accounts = list(set(tx["account"] for tx in transactions if tx["bank"] == bank_selected))
        account_selected = questionary.select("Select account:", choices=accounts).ask()
        filtered = [tx for tx in transactions if tx["bank"] == bank_selected and tx["account"] == account_selected]

    print("Transactions:")
    for tx in filtered:
        print(f"ID: {tx['id']}")
        print(f"Date: {tx['date']}")
        print(f"Bank: {tx['bank']}, Account: {tx['account']}")
        print(f"Type: {tx['type'].capitalize()}, Amount: ${tx['amount']}")
        print(f"Description: {tx['description']}")
        print("-" * 40)
    input("Press Enter to return to menu...")


# --- Bank & Account Management ---

def add_bank(setup_data):
    clear_screen()
    print_header()
    bank_name = questionary.text("Enter new bank name:").ask()
    if any(b["name"] == bank_name for b in setup_data["banks"]):
        print("Bank already exists!")
        input("Press Enter to return to menu...")
        return
    new_bank = {"name": bank_name, "accounts": []}
    setup_data["banks"].append(new_bank)
    save_setup(setup_data)
    print("Bank added successfully!")
    input("Press Enter to return to menu...")


def rename_bank(setup_data, transactions):
    clear_screen()
    print_header()
    if not setup_data["banks"]:
        print("No banks available.")
        input("Press Enter to return to menu...")
        return
    bank_names = [bank["name"] for bank in setup_data["banks"]]
    bank_choice = questionary.select("Select bank to rename:", choices=bank_names).ask()
    new_name = questionary.text("Enter new name for the bank:").ask()
    for bank in setup_data["banks"]:
        if bank["name"] == bank_choice:
            bank["name"] = new_name
            break
    for tx in transactions:
        if tx["bank"] == bank_choice:
            tx["bank"] = new_name
    save_setup(setup_data)
    save_transactions(transactions)
    print("Bank renamed successfully!")
    input("Press Enter to return to menu...")


def delete_bank(setup_data, transactions):
    clear_screen()
    print_header()
    if not setup_data["banks"]:
        print("No banks available.")
        input("Press Enter to return to menu...")
        return
    bank_names = [bank["name"] for bank in setup_data["banks"]]
    bank_choice = questionary.select("Select bank to delete:", choices=bank_names).ask()
    confirm = questionary.confirm(
        f"Are you sure you want to delete bank '{bank_choice}' and all its accounts?"
    ).ask()
    if not confirm:
        return
    setup_data["banks"] = [bank for bank in setup_data["banks"] if bank["name"] != bank_choice]
    transactions[:] = [tx for tx in transactions if tx["bank"] != bank_choice]
    save_setup(setup_data)
    save_transactions(transactions)
    print("Bank deleted successfully!")
    input("Press Enter to return to menu...")


def add_account(setup_data):
    clear_screen()
    print_header()
    if not setup_data["banks"]:
        print("No banks available. Please add a bank first.")
        input("Press Enter to return to menu...")
        return
    bank_names = [bank["name"] for bank in setup_data["banks"]]
    bank_choice = questionary.select("Select bank to add account to:", choices=bank_names).ask()
    for bank in setup_data["banks"]:
        if bank["name"] == bank_choice:
            account_name = questionary.text("Enter new account name:").ask()
            if any(acc["name"] == account_name for acc in bank["accounts"]):
                print("Account already exists!")
                input("Press Enter to return to menu...")
                return
            initial_balance_str = questionary.text("Enter initial balance (default 0):").ask()
            try:
                initial_balance = float(initial_balance_str) if initial_balance_str else 0.0
            except ValueError:
                initial_balance = 0.0
            bank["accounts"].append({"name": account_name, "balance": initial_balance})
            break
    save_setup(setup_data)
    print("Account added successfully!")
    input("Press Enter to return to menu...")


def rename_account(setup_data, transactions):
    clear_screen()
    print_header()
    if not setup_data["banks"]:
        print("No banks available.")
        input("Press Enter to return to menu...")
        return
    bank_choices = []
    for bank in setup_data["banks"]:
        bank_choices.append(questionary.Choice(title=bank["name"], value=bank))
    selected_bank = questionary.select("Select bank:", choices=bank_choices).ask()
    if not selected_bank["accounts"]:
        print("No accounts available in this bank.")
        input("Press Enter to return to menu...")
        return
    account_choices = []
    for acc in selected_bank["accounts"]:
        account_choices.append(questionary.Choice(
            title=f"{acc['name']} (Balance: ${acc['balance']:.2f})", value=acc
        ))
    selected_account = questionary.select("Select account to rename:", choices=account_choices).ask()
    old_name = selected_account["name"]
    new_name = questionary.text("Enter new account name:", default=selected_account["name"]).ask()
    selected_account["name"] = new_name
    for tx in transactions:
        if tx["bank"] == selected_bank["name"] and tx["account"] == old_name:
            tx["account"] = new_name
    save_setup(setup_data)
    save_transactions(transactions)
    print("Account renamed successfully!")
    input("Press Enter to return to menu...")


def delete_account(setup_data, transactions):
    clear_screen()
    print_header()
    if not setup_data["banks"]:
        print("No banks available.")
        input("Press Enter to return to menu...")
        return
    bank_choices = []
    for bank in setup_data["banks"]:
        bank_choices.append(questionary.Choice(title=bank["name"], value=bank))
    selected_bank = questionary.select("Select bank:", choices=bank_choices).ask()
    if not selected_bank["accounts"]:
        print("No accounts available in this bank.")
        input("Press Enter to return to menu...")
        return
    account_choices = []
    for acc in selected_bank["accounts"]:
        account_choices.append(questionary.Choice(
            title=f"{acc['name']} (Balance: ${acc['balance']:.2f})", value=acc
        ))
    selected_account = questionary.select("Select account to delete:", choices=account_choices).ask()
    confirm = questionary.confirm(
        f"Are you sure you want to delete account '{selected_account['name']}'?"
    ).ask()
    if not confirm:
        return
    selected_bank["accounts"] = [acc for acc in selected_bank["accounts"] if acc["name"] != selected_account["name"]]
    transactions[:] = [
        tx for tx in transactions if not (tx["bank"] == selected_bank["name"] and tx["account"] == selected_account["name"])
    ]
    save_setup(setup_data)
    save_transactions(transactions)
    print("Account deleted successfully!")
    input("Press Enter to return to menu...")


def bank_account_management(setup_data, transactions):
    while True:
        clear_screen()
        print_header()
        choice = questionary.select("Bank & Account Management:", choices=[
            "Add Bank",
            "Rename Bank",
            "Delete Bank",
            "Add Account",
            "Rename Account",
            "Delete Account",
            "Back to Main Menu",
        ]).ask()
        if choice == "Add Bank":
            add_bank(setup_data)
        elif choice == "Rename Bank":
            rename_bank(setup_data, transactions)
        elif choice == "Delete Bank":
            delete_bank(setup_data, transactions)
        elif choice == "Add Account":
            add_account(setup_data)
        elif choice == "Rename Account":
            rename_account(setup_data, transactions)
        elif choice == "Delete Account":
            delete_account(setup_data, transactions)
        elif choice == "Back to Main Menu":
            break


# --- Financial Operations Menu (includes view balance) ---

def financial_operations(setup_data, transactions):
    while True:
        clear_screen()
        print_header()
        choice = questionary.select("Financial Operations:", choices=[
            "Add Transaction",
            "Edit Transaction",
            "Refund Transaction",
            "View Transactions",
            "View Balance",
            "Back to Main Menu",
        ]).ask()
        if choice == "Add Transaction":
            add_transaction(setup_data, transactions)
        elif choice == "Edit Transaction":
            edit_transaction(setup_data, transactions)
        elif choice == "Refund Transaction":
            refund_transaction(setup_data, transactions)
        elif choice == "View Transactions":
            view_transactions(transactions)
        elif choice == "View Balance":
            view_balance(setup_data)
        elif choice == "Back to Main Menu":
            break


# --- New Balance View Function ---

def view_balance(setup_data):
    clear_screen()
    print_header()
    if not setup_data["banks"]:
        print("No banks or accounts available.")
        input("Press Enter to return to menu...")
        return
    print("Account Balances:")
    for bank in setup_data["banks"]:
        total_balance = sum(account["balance"] for account in bank["accounts"])
        print(f"\nBank: {bank['name']} (Total Balance: ${total_balance:.2f})")
        if bank["accounts"]:
            for account in bank["accounts"]:
                print(f"  - {account['name']}: ${account['balance']:.2f}")
        else:
            print("  No accounts available.")
    print("\n" + "=" * 60)
    input("Press Enter to return to menu...")


# --- Main Menu ---

def main_menu():
    setup_data = load_setup()
    transactions = load_transactions()

    # Run initial setup if no banks exist.
    if not setup_data["banks"]:
        setup_initial()
        setup_data = load_setup()

    while True:
        clear_screen()
        print_header()
        choice = questionary.select("Main Menu", choices=[
            "Financial Operations",
            "Bank & Account Management",
            "Exit",
        ]).ask()

        if choice == "Financial Operations":
            financial_operations(setup_data, transactions)
        elif choice == "Bank & Account Management":
            bank_account_management(setup_data, transactions)
        elif choice == "Exit":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main_menu()
