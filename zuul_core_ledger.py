from datetime import datetime, timedelta
import os
import pika
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)
db = client.zuul_core_banking

# Define Account model
class Account:
    def __init__(self, account_id, customer_name, initial_balance=0.0, interest_rate=0.01):
        self.account_id = account_id
        self.customer_name = customer_name
        self.balance = initial_balance
        self.interest_rate = interest_rate
        self.loans = []
        self.transactions = []

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "customer_name": self.customer_name,
            "balance": self.balance,
            "interest_rate": self.interest_rate,
            "loans": self.loans,
            "transactions": self.transactions
        }

    @staticmethod
    def from_dict(data):
        account = Account(data["account_id"], data["customer_name"], data["balance"], data["interest_rate"])
        account.loans = data.get("loans", [])
        account.transactions = data.get("transactions", [])
        return account

class ZuulCoreLedger:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv("RABBITMQ_HOST", "localhost")))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='transfer_queue')

    def open_account(self, account_id, customer_name, initial_balance=0.0, interest_rate=0.01):
        account = Account(account_id, customer_name, initial_balance, interest_rate)
        db.accounts.insert_one(account.to_dict())
        logging.info(f"Account {account_id} created for {customer_name} with balance {initial_balance}")

    def get_account(self, account_id):
        data = db.accounts.find_one({"account_id": account_id})
        return Account.from_dict(data) if data else None

    def update_account(self, account):
        db.accounts.update_one({"account_id": account.account_id}, {"$set": account.to_dict()})

    def deposit(self, account_id, amount):
        account = self.get_account(account_id)
        if account and amount > 0:
            account.balance += amount
            account.transactions.append({"type": "deposit", "amount": amount, "date": datetime.now()})
            self.update_account(account)
            return f"Deposited {amount} to account {account_id}."
        return "Account not found or invalid deposit amount."

    def withdraw(self, account_id, amount):
        account = self.get_account(account_id)
        if account and 0 < amount <= account.balance:
            account.balance -= amount
            account.transactions.append({"type": "withdraw", "amount": amount, "date": datetime.now()})
            self.update_account(account)
            return f"Withdrew {amount} from account {account_id}."
        return "Account not found or insufficient funds."

    def transfer(self, from_account_id, to_account_id, amount):
        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)
        if from_account and to_account and 0 < amount <= from_account.balance:
            from_account.balance -= amount
            to_account.balance += amount
            from_account.transactions.append({"type": "transfer", "amount": -amount, "to": to_account_id, "date": datetime.now()})
            to_account.transactions.append({"type": "transfer", "amount": amount, "from": from_account_id, "date": datetime.now()})
            self.update_account(from_account)
            self.update_account(to_account)
            return f"Transferred {amount} from {from_account_id} to {to_account_id}."
        return "Transfer failed due to insufficient funds or account error."

    def calculate_interest(self, account_id):
        account = self.get_account(account_id)
        if account:
            interest = account.balance * account.interest_rate
            account.balance += interest
            account.transactions.append({"type": "interest", "amount": interest, "date": datetime.now()})
            self.update_account(account)
            return f"Interest of {interest} applied to account {account_id}."
        return "Account not found."

    def request_loan(self, account_id, amount, interest_rate=0.05, duration=12):
        account = self.get_account(account_id)
        if account and amount > 0:
            loan = {
                "amount": amount,
                "interest_rate": interest_rate,
                "duration": duration,
                "outstanding_balance": amount,
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(days=30 * duration)
            }
            account.loans.append(loan)
            account.balance += amount
            account.transactions.append({"type": "loan", "amount": amount, "date": datetime.now()})
            self.update_account(account)
            return f"Loan of {amount} granted to account {account_id}."
        return "Loan request failed."

    def repay_loan(self, account_id, loan_index, amount):
        account = self.get_account(account_id)
        if account and loan_index < len(account.loans):
            loan = account.loans[loan_index]
            if 0 < amount <= account.balance:
                account.balance -= amount
                loan["outstanding_balance"] -= amount
                account.transactions.append({"type": "loan repayment", "amount": -amount, "date": datetime.now()})
                if loan["outstanding_balance"] <= 0:
                    account.loans.pop(loan_index)  # Loan fully repaid
                self.update_account(account)
                return f"Repayment of {amount} applied to loan for account {account_id}."
        return "Repayment failed due to invalid loan index or insufficient funds."

    def get_transaction_history(self, account_id):
        account = self.get_account(account_id)
        if account:
            return account.transactions
        return "Account not found."
