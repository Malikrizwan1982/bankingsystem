"""
╔══════════════════════════════════════════════╗
║       PyBank – Interactive Banking System    ║
║         Built with OOP Concepts in Python    ║
╚══════════════════════════════════════════════╝

OOP Concepts used:
  Encapsulation  → _balance, _transactions are protected
  Inheritance    → SavingsAccount & CurrentAccount extend BankAccount
  Polymorphism   → withdraw() behaves differently per account type
  Abstraction    → Bank class hides internal storage details
  Magic Methods  → __str__ for clean printing
"""

import datetime
import os


# ══════════════════════════════════════════════
#  HELPER UTILITIES
# ══════════════════════════════════════════════

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def divider(char="─", width=52):
    print("  " + char * width)

def header(title):
    clear()
    print()
    divider("═")
    print(f"  {'PyBank':^52}")
    print(f"  {title:^52}")
    divider("═")
    print()

def pause():
    input("\n  Press Enter to continue...")

def get_float(prompt):
    """Get a valid positive float from user."""
    while True:
        try:
            val = float(input(prompt))
            if val <= 0:
                print("  ✗  Amount must be greater than zero.")
            else:
                return val
        except ValueError:
            print("  ✗  Please enter a valid number.")

def get_int(prompt):
    """Get a valid integer from user."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  ✗  Please enter a valid number.")


# ══════════════════════════════════════════════
#  BASE CLASS  –  BankAccount
# ══════════════════════════════════════════════

class BankAccount:
    """Base class: shared logic for all account types."""

    interest_rate = 0.03   # class variable – 3% per year

    def __init__(self, account_number, owner_name, balance=0):
        self.account_number  = account_number
        self.owner_name      = owner_name
        self._balance        = balance        # encapsulated
        self._transactions   = []             # encapsulated

    # ── Deposit ───────────────────────────────
    def deposit(self, amount):
        if amount <= 0:
            print("  ✗  Amount must be positive.")
            return False
        self._balance += amount
        self._log("Deposit  +", amount)
        print(f"  ✓  Deposited Rs {amount:>12,.2f}")
        print(f"     New Balance  Rs {self._balance:>12,.2f}")
        return True

    # ── Withdraw ──────────────────────────────
    def withdraw(self, amount):
        if amount <= 0:
            print("  ✗  Amount must be positive.")
            return False
        if amount > self._balance:
            print(f"  ✗  Insufficient funds.")
            print(f"     Available:  Rs {self._balance:>12,.2f}")
            return False
        self._balance -= amount
        self._log("Withdraw -", amount)
        print(f"  ✓  Withdrew   Rs {amount:>12,.2f}")
        print(f"     New Balance  Rs {self._balance:>12,.2f}")
        return True

    # ── Transfer ──────────────────────────────
    def transfer(self, target, amount):
        print(f"\n  Sending Rs {amount:,.2f} → {target.owner_name} ({target.account_number})")
        if self.withdraw(amount):
            target._balance += amount
            target._log("Transfer +", amount)
            print(f"  ✓  Transfer complete!")
            return True
        return False

    # ── Balance Sheet ─────────────────────────
    def balance_sheet(self):
        print()
        divider()
        print(f"  {'BALANCE SHEET':^52}")
        divider()
        print(f"  Owner        : {self.owner_name}")
        print(f"  Account No   : {self.account_number}")
        print(f"  Account Type : {type(self).__name__}")
        print(f"  Date         : {datetime.date.today()}")
        divider()

        if not self._transactions:
            print("  No transactions on record.")
        else:
            print(f"  {'DATE':<12}  {'DESCRIPTION':<14}  {'AMOUNT':>12}")
            divider("·")
            running = 0
            for t in self._transactions:
                # Work out +/- for running balance
                if "+" in t["type"]:
                    running += t["amount"]
                else:
                    running -= t["amount"]
                sign = "+" if "+" in t["type"] else "-"
                label = t["type"].replace(" +","").replace(" -","").strip()
                print(f"  {t['date']:<12}  {label:<14}  {sign}Rs {t['amount']:>9,.2f}")
            divider("·")

        divider()
        print(f"  {'CURRENT BALANCE':}  Rs {self._balance:>12,.2f}")
        divider()
        print()

    # ── Internal log ──────────────────────────
    def _log(self, t_type, amount):
        self._transactions.append({
            "date"  : datetime.date.today().strftime("%Y-%m-%d"),
            "type"  : t_type,
            "amount": amount
        })

    def __str__(self):
        return (f"  Acc# {self.account_number}  |  {self.owner_name:<20}"
                f"  |  {type(self).__name__:<15}"
                f"  |  Rs {self._balance:>10,.2f}")


# ══════════════════════════════════════════════
#  SAVINGS ACCOUNT  (Inheritance)
# ══════════════════════════════════════════════

class SavingsAccount(BankAccount):
    """Savings account with interest feature."""

    def __init__(self, account_number, owner_name, balance=0):
        super().__init__(account_number, owner_name, balance)

    def apply_interest(self):
        interest = round(self._balance * BankAccount.interest_rate, 2)
        self._balance += interest
        self._log("Interest +", interest)
        print(f"  ✓  Interest credited: Rs {interest:,.2f}")
        print(f"     New Balance      : Rs {self._balance:,.2f}")


# ══════════════════════════════════════════════
#  CURRENT ACCOUNT  (Inheritance + Polymorphism)
# ══════════════════════════════════════════════

class CurrentAccount(BankAccount):
    """Current account with overdraft facility."""

    def __init__(self, account_number, owner_name, balance=0, overdraft=5000):
        super().__init__(account_number, owner_name, balance)
        self.overdraft = overdraft

    # Polymorphism: overrides parent withdraw()
    def withdraw(self, amount):
        if amount <= 0:
            print("  ✗  Amount must be positive.")
            return False
        limit = self._balance + self.overdraft
        if amount > limit:
            print(f"  ✗  Exceeds overdraft limit.")
            print(f"     Max withdrawable: Rs {limit:,.2f}")
            return False
        self._balance -= amount
        self._log("Withdraw -", amount)
        print(f"  ✓  Withdrew   Rs {amount:>12,.2f}")
        print(f"     New Balance  Rs {self._balance:>12,.2f}")
        if self._balance < 0:
            print(f"  ⚠  Overdraft active: Rs {abs(self._balance):,.2f} owed")
        return True


# ══════════════════════════════════════════════
#  BANK CLASS  (Abstraction / Manager)
# ══════════════════════════════════════════════

class Bank:
    """Manages all accounts. Hides storage internals from the user."""

    def __init__(self, name):
        self.name       = name
        self._accounts  = {}      # { acc_no: BankAccount }
        self._next_no   = 1001

    def create_account(self, owner, acc_type, initial):
        acc_no = str(self._next_no)
        self._next_no += 1
        if acc_type == "1":
            acc = SavingsAccount(acc_no, owner, initial)
        else:
            acc = CurrentAccount(acc_no, owner, initial)
        self._accounts[acc_no] = acc
        return acc

    def get(self, acc_no):
        return self._accounts.get(str(acc_no))

    def all_accounts(self):
        return list(self._accounts.values())

    def count(self):
        return len(self._accounts)


# ══════════════════════════════════════════════
#  INTERACTIVE MENUS
# ══════════════════════════════════════════════

def menu_main(bank):
    """Main menu – shown before logging into an account."""
    while True:
        header("MAIN MENU")
        print("  [1]  Create New Account")
        print("  [2]  Login to Account")
        print("  [3]  View All Accounts")
        print("  [0]  Exit")
        print()
        choice = input("  → ").strip()

        if choice == "1":
            menu_create(bank)
        elif choice == "2":
            menu_login(bank)
        elif choice == "3":
            menu_all_accounts(bank)
        elif choice == "0":
            header("GOODBYE")
            print(f"  Thank you for banking with {bank.name}!")
            print(f"  See you next time.\n")
            break
        else:
            print("  ✗  Invalid choice.")
            pause()


def menu_create(bank):
    """Create a new account."""
    header("CREATE ACCOUNT")
    name = input("  Full Name       : ").strip()
    if not name:
        print("  ✗  Name cannot be empty.")
        pause()
        return

    print()
    print("  Account Type:")
    print("  [1]  Savings Account  (earns interest)")
    print("  [2]  Current Account  (overdraft allowed)")
    print()
    acc_type = input("  → ").strip()
    if acc_type not in ("1", "2"):
        print("  ✗  Invalid choice.")
        pause()
        return

    print()
    initial = get_float("  Initial Deposit (Rs): ")

    acc = bank.create_account(name, acc_type, initial)

    print()
    divider()
    print(f"  ✓  Account created successfully!")
    divider("·")
    print(f"  Account Number : {acc.account_number}")
    print(f"  Owner          : {acc.owner_name}")
    print(f"  Type           : {type(acc).__name__}")
    print(f"  Balance        : Rs {acc._balance:,.2f}")
    divider()
    pause()


def menu_login(bank):
    """Login to an existing account."""
    if bank.count() == 0:
        header("LOGIN")
        print("  No accounts exist yet. Please create one first.")
        pause()
        return

    header("LOGIN")
    acc_no = input("  Enter Account Number: ").strip()
    acc = bank.get(acc_no)
    if not acc:
        print(f"  ✗  Account '{acc_no}' not found.")
        pause()
        return

    menu_account(bank, acc)


def menu_account(bank, acc):
    """Per-account menu after login."""
    while True:
        header(f"ACCOUNT  #{acc.account_number}")
        print(f"  Welcome, {acc.owner_name}!")
        print(f"  Type    : {type(acc).__name__}")
        print(f"  Balance : Rs {acc._balance:,.2f}")
        print()
        divider("·")
        print("  [1]  Deposit")
        print("  [2]  Withdraw")
        print("  [3]  Transfer")
        print("  [4]  Balance Sheet")
        if isinstance(acc, SavingsAccount):
            print("  [5]  Apply Interest")
        print("  [0]  Logout")
        print()
        choice = input("  → ").strip()

        if choice == "1":
            header("DEPOSIT")
            amount = get_float("  Amount to deposit (Rs): ")
            print()
            acc.deposit(amount)
            pause()

        elif choice == "2":
            header("WITHDRAW")
            amount = get_float("  Amount to withdraw (Rs): ")
            print()
            acc.withdraw(amount)
            pause()

        elif choice == "3":
            header("TRANSFER")
            if bank.count() < 2:
                print("  ✗  No other accounts to transfer to.")
                pause()
                continue
            # show available accounts
            print("  Available Accounts:")
            divider("·")
            for a in bank.all_accounts():
                if a.account_number != acc.account_number:
                    print(f"  Acc# {a.account_number}  –  {a.owner_name}")
            divider("·")
            target_no = input("\n  Enter target account number: ").strip()
            target = bank.get(target_no)
            if not target:
                print(f"  ✗  Account '{target_no}' not found.")
                pause()
                continue
            if target.account_number == acc.account_number:
                print("  ✗  Cannot transfer to your own account.")
                pause()
                continue
            amount = get_float("  Amount to transfer (Rs): ")
            print()
            acc.transfer(target, amount)
            pause()

        elif choice == "4":
            header("BALANCE SHEET")
            acc.balance_sheet()
            pause()

        elif choice == "5" and isinstance(acc, SavingsAccount):
            header("APPLY INTEREST")
            print(f"  Interest Rate : {BankAccount.interest_rate*100:.1f}%")
            print(f"  Current Balance: Rs {acc._balance:,.2f}")
            print()
            acc.apply_interest()
            pause()

        elif choice == "0":
            break

        else:
            print("  ✗  Invalid option.")
            pause()


def menu_all_accounts(bank):
    """View all accounts in the bank."""
    header("ALL ACCOUNTS")
    if bank.count() == 0:
        print("  No accounts found. Create one first.")
    else:
        print(f"  {'ACC#':<6}  {'OWNER':<22}  {'TYPE':<16}  {'BALANCE':>12}")
        divider("·")
        for a in bank.all_accounts():
            print(f"  {a.account_number:<6}  {a.owner_name:<22}"
                  f"  {type(a).__name__:<16}  Rs {a._balance:>9,.2f}")
        divider()
        print(f"  Total Accounts : {bank.count()}")
    pause()


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════

def main():
    bank = Bank("PyBank")
    clear()
    print()
    divider("═")
    print(f"  {'':>4}  Welcome to PyBank  {'':>4}")
    print(f"  {'Interactive Banking System':^52}")
    divider("═")
    print()
    input("  Press Enter to start...")
    menu_main(bank)


if __name__ == "__main__":
    main()