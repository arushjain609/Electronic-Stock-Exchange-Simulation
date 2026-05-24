from OMS import OMS

class Trader:
    def __init__(self, ID, balance, exchange):
        self.ID = ID
        self.bank_account_balance = balance
        self.exchange = exchange
        self.OMS = OMS(exchange=self.exchange, trader_ID=self.ID, balance=(self.bank_account_balance)/2)
    
    def create_order(self, security_ID, price, quantity, direction):
        order = {}
        order["trader_ID"] = self.ID
        order["security_ID"] = security_ID
        order["price"] = price
        order["quantity"] = quantity
        order["direction"] = direction
        order["status"] = "PENDING"
        order["remaining"] = quantity
        order["timestamp"] = self.exchange.get_timestamp()
        order["validation"] = 0
        order["ID"] = str(order["timestamp"]) + "_" + str(order["trader_ID"]) + "_" + str(order["security_ID"]) + "_" + str(self.OMS.get_next_order_id())

        if order["timestamp"] <= self.exchange.time_limit:
            self.OMS.place_order(order)

    def add_amount_to_OMS(self,amount):
        if amount <= self.bank_account_balance:
            self.OMS.add_amount(amount)
            self.bank_account_balance -= amount
        else:
            print("Insufficient Balance")
    
    def withdraw_amount_from_OMS(self,amount):
        if self.OMS.withdraw_amount(amount):
            self.bank_account_balance += amount
        else:
            print("Insufficient Balance")

    def check_account_status(self):
        if self.OMS.trading_account_balance < 50000 and self.bank_account_balance > 0:
            amount = (self.bank_account_balance)/2 if self.bank_account_balance > 100000 else self.bank_account_balance
            self.add_amount_to_OMS(amount)
            print(self.ID,"required",amount,"money from bank account")