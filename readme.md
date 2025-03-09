# 🚀 Finance Manager CLI

A simple yet powerful **Command Line Interface (CLI)** application to track and manage your financial transactions across multiple **banks and accounts**. The program allows users to add, edit, and refund transactions with an **interactive menu**.

---

## 📌 Features

✅ **Transaction Management**

- Add, Edit, Refund, and View Transactions (by bank/account or all).
- Support for **deposits, withdrawals, and refunds** with descriptions.

✅ **Bank & Account Management**

- Add, Rename, and Delete Banks & Accounts.
- Each bank can have multiple accounts with **trackable balances**.

✅ **User Experience & Navigation**

- **Arrow Key Navigation** using `questionary` for smooth selection.
- **Automatic Screen Clearing** after every action for a clean UI.

✅ **Data Persistence**

- Saves all data in **setup.json** for easy storage and retrieval.

✅ **Cross-Platform Compatibility**

- Works on **Linux, Mac, and Windows** without additional setup.

✅ **Setup Process**

- First-time users are automatically guided through the **initial setup** to create banks and accounts.

✅ **View Transactions**

- View transactions per **bank, account**, or **all transactions together**.

---

## 📥 Installation

### **1️⃣ Clone the Repository**

```sh
git clone https://github.com/lokeshsandhu/Finance-manager-cli.git
cd Finance-manager-cli
```

### **2️⃣ Install Dependencies**

```sh
pip install -r requirements.txt
```

### **3️⃣ Run the Application**

```sh
python3 finance_manager.py
```

---

## 🎮 Usage Guide

Once you run `python3 main.py`, the following **interactive menu** appears:

```
🔹 Finance Manager CLI
🏦 Main Menu:
1️⃣ Add Transaction
2️⃣ Edit Transaction
3️⃣ Refund Transaction
4️⃣ View Transactions
5️⃣ Edit Setup
6️⃣ Exit
```

### **➤ Adding a Transaction**

1. Select **"Add Transaction"**
2. Choose **Bank → Account → Amount → Transaction Type (Deposit/Withdraw) → Description**
3. The **balance updates automatically**

### **➤ Viewing Transactions**

- Choose **a specific account, bank, or all transactions**
- The app displays **transaction amount, type, and description**

### **➤ Editing a Transaction**

1. Select **"Edit Transaction"**
2. Choose the **bank, account, and transaction to edit**
3. Modify **amount, type, or description**

### **➤ Refunding a Transaction**

1. Select **"Refund Transaction"**
2. Choose **Bank → Account → Transaction to refund**
3. Enter the **refund amount**
4. The refund **is recorded as a new transaction**

### **➤ Editing Setup (Banks & Accounts)**

1. Select **"Edit Setup"**
2. Choose **Add, Rename, or Delete Banks & Accounts**

---

## 💡 License

This project is licensed under the **MIT License** – feel free to use, modify, and distribute it.

---

🚀 **Developed by ****[Lokesh Sandhu](https://github.com/lokeshsandhu)** | [GitHub Repo](https://github.com/lokeshsandhu/Finance-manager-cli)

