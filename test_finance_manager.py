import datetime
import questionary
import pytest

# Import the functions to test from your CLI code.
# (Make sure the finance_manager.py file is in the same directory or in your PYTHONPATH)
from finance_manager import (
    add_transaction,
    refund_transaction,
    edit_transaction,
    view_balance,
)

# A simple dummy prompter class that mimics questionary's .ask() behavior.
class DummyPrompter:
    def __init__(self, response):
        self.response = response

    def ask(self):
        return self.response

# A helper function to override questionary functions and input.
def set_monkeypatch_responses(monkeypatch, responses):
    it = iter(responses)
    monkeypatch.setattr(
        questionary,
        "select",
        lambda prompt, choices=None, **kwargs: DummyPrompter(next(it)),
    )
    monkeypatch.setattr(
        questionary,
        "text",
        lambda prompt, **kwargs: DummyPrompter(next(it)),
    )
    monkeypatch.setattr(
        questionary,
        "confirm",
        lambda prompt, **kwargs: DummyPrompter(next(it)),
    )
    # Bypass the built-in input (used for "Press Enter to return to menu...")
    monkeypatch.setattr("builtins.input", lambda prompt="": None)

    
def test_add_transaction(monkeypatch):
    # Set up a test bank with one account.
    setup_data = {
        "banks": [
            {
                "name": "Test Bank",
                "accounts": [{"name": "Checking", "balance": 100.0}],
            }
        ]
    }
    transactions = []

    test_bank = setup_data["banks"][0]
    test_account = test_bank["accounts"][0]
    
    # Responses (in order) for add_transaction:
    # 1. Bank selection: return the bank object.
    # 2. Account selection: return the account object.
    # 3. Transaction type: "Deposit"
    # 4. Amount: "50"
    # 5. Description: "Test deposit"
    responses = [test_bank, test_account, "Deposit", "50", "Test deposit"]
    set_monkeypatch_responses(monkeypatch, responses)

    add_transaction(setup_data, transactions)

    # Verify that a transaction was added.
    assert len(transactions) == 1
    tx = transactions[0]
    assert tx["bank"] == "Test Bank"
    assert tx["account"] == "Checking"
    assert tx["type"] == "deposit"
    assert tx["amount"] == 50.0
    assert tx["description"] == "Test deposit"
    # Verify that the account balance was updated (100 + 50 = 150)
    assert test_account["balance"] == 150.0

def test_refund_transaction(monkeypatch):
    # Set up a test bank with one account and one deposit transaction.
    setup_data = {
        "banks": [
            {
                "name": "Test Bank",
                "accounts": [{"name": "Checking", "balance": 150.0}],
            }
        ]
    }
    transactions = [
        {
            "id": "tx1",
            "bank": "Test Bank",
            "account": "Checking",
            "type": "deposit",
            "amount": 50.0,
            "description": "Test deposit",
            "date": datetime.datetime.now().isoformat(),
        }
    ]
    test_bank = setup_data["banks"][0]
    test_account = test_bank["accounts"][0]

    # Simulate refund selection with formatted transaction string
    transaction_string = f"{transactions[0]['date'][:19]} | {transactions[0]['bank']} - {transactions[0]['account']} | {transactions[0]['type'].capitalize()} ${transactions[0]['amount']} | {transactions[0]['description']}"

    # Responses for refund_transaction:
    # 1. Transaction selection: formatted transaction string.
    # 2. Refund amount: "20" (default is full amount if blank)
    responses = [transaction_string, "20"]
    set_monkeypatch_responses(monkeypatch, responses)

    refund_transaction(setup_data, transactions)

    # Now there should be two transactions.
    assert len(transactions) == 2
    refund_tx = transactions[-1]
    assert refund_tx["refunded_transaction_id"] == "tx1"
    assert refund_tx["amount"] == 20.0
    # Since the original was a deposit, the refund type becomes withdrawal.
    # Thus, the account balance should decrease by 20 (150 - 20 = 130).
    assert test_account["balance"] == 130.0

def test_edit_transaction(monkeypatch):
    # Set up a test bank with one account and one deposit transaction.
    setup_data = {
        "banks": [
            {
                "name": "Test Bank",
                "accounts": [{"name": "Checking", "balance": 150.0}],
            }
        ]
    }
    transactions = [
        {
            "id": "tx1",
            "bank": "Test Bank",
            "account": "Checking",
            "type": "deposit",
            "amount": 50.0,
            "description": "Test deposit",
            "date": datetime.datetime.now().isoformat(),
        }
    ]
    test_bank = setup_data["banks"][0]
    test_account = test_bank["accounts"][0]

    # Correctly formatted f-string (split across lines for readability)
    transaction_string = (
        f"{transactions[0]['date'][:19]} | "
        f"{transactions[0]['bank']} - {transactions[0]['account']} | "
        f"{transactions[0]['type'].capitalize()} ${transactions[0]['amount']} | "
        f"{transactions[0]['description']}"
    )

    # Simulate editing the transaction:
    # 1. Transaction selection: formatted transaction string.
    # 2. New transaction type: "Withdrawal"
    # 3. New amount: "30"
    # 4. New description: "Edited transaction"
    responses = [transaction_string, "Withdrawal", "30", "Edited transaction"]
    set_monkeypatch_responses(monkeypatch, responses)

    edit_transaction(setup_data, transactions)

    tx = transactions[0]
    assert tx["type"] == "withdrawal"
    assert tx["amount"] == 30.0
    assert tx["description"] == "Edited transaction"
    
    # Calculation:
    # - Reverse original deposit of 50: 150 - 50 = 100.
    # - Apply new withdrawal of 30: 100 - 30 = 70.
    assert test_account["balance"] == 70.0


def test_view_balance(capsys, monkeypatch):
    # Set up test data with two banks and multiple accounts.
    setup_data = {
        "banks": [
            {"name": "Bank A", "accounts": [{"name": "A1", "balance": 100.0}, {"name": "A2", "balance": 200.0}]},
            {"name": "Bank B", "accounts": [{"name": "B1", "balance": 300.0}]},
        ]
    }
    # Bypass the "Press Enter" input prompt.
    monkeypatch.setattr("builtins.input", lambda prompt="": None)

    # Call view_balance (it prints output).
    view_balance(setup_data)
    captured = capsys.readouterr().out

    # Verify that the output contains the expected balances.
    assert "Bank: Bank A (Total Balance: $300.00)" in captured
    assert "  - A1: $100.00" in captured
    assert "  - A2: $200.00" in captured
    assert "Bank: Bank B (Total Balance: $300.00)" in captured
    assert "  - B1: $300.00" in captured
