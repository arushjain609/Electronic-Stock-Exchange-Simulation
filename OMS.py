class OMS:
    def __init__(self, exchange, trader_ID, balance):
        self.exchange = exchange
        self.ID = trader_ID
        self.trading_account_balance = balance
        self.pending_buy_balance = 0.0
        self.pending_sell_quantity = {}
        self.portfolio = {}
        self.portfolio_history = []
        self.orders = {}
        self.next_order_id = 0

        for security_ID in self.exchange.securities.keys():
            self.pending_sell_quantity[security_ID] = 0

    def get_trading_account_balance(self):
        return self.trading_account_balance
    
    def get_next_order_id(self):
        id = self.next_order_id
        self.next_order_id += 1
        return id
    
    def add_amount(self, amount):
        self.trading_account_balance += amount
        return 1
    
    def withdraw_amount(self, amount):
        if self.trading_account_balance >= amount:
            self.trading_account_balance -= amount
            return 1
        else:
            return 0
        
    def get_portfolio_value(self):
        value = 0.0
        for security_id, data in self.portfolio.items():
            data["value"] = self.exchange.get_last_traded_price(security_id)*data["quantity"]
            data["unrealised_pnl"] += (data["value"] - data["quantity"]*data["avg_buy_price"])
            value += data["value"]

        self.portfolio_history.append(value)

        return value
      
    def place_order(self,order):
        check = 0
        if order["direction"] == "buy":
            amount = order["quantity"]*order["price"]
            if self.pending_buy_balance + amount <= self.trading_account_balance:
                check = 1
        else:
            quantity = order["quantity"]
            if  quantity + self.pending_sell_quantity[order["security_ID"]] <= self.portfolio[order["security_ID"]]["quantity"]:
                check = 1

        if check:
            self.orders[order["ID"]] = order
            status = self.exchange.place_order(order)
            self.orders[order["ID"]]["status"] = status
            if status == "ACCEPTED":
                self.orders[order["ID"]]["validation"] = 1
                if order["direction"] == "buy":
                    amount = order["quantity"]*order["price"]
                    self.pending_buy_balance += amount
                    order["reservation"] = [amount, amount]
                else:
                    quantity = order["quantity"]
                    self.pending_sell_quantity[order["security_ID"]] += quantity
                    order["reservation"] = [quantity, quantity]
        else:
            order["status"] = "REJECTED"
            self.orders[order["ID"]] = order

    def check_order_status(self):
        del_idx = []
        for order_ID, order in self.orders.items():
            if (order["status"] in ["REJECTED", "CANCELLED", "EXPIRED", "FILLED"]):
                del_idx.append(order_ID)
                if order["validation"]:
                    order["validation"] = 0
                    if order["direction"] == "buy":
                        self.pending_buy_balance -= order["reservation"][1]
                    else:
                        self.pending_sell_quantity[order["security_ID"]] -= order["reservation"][1]
            elif order["status"] == "PARTIALLY FILLED" and not order["validation"]:
                order["validation"] = 1
                order["reservation"][0] = order["reservation"][1]
                current_quantity =  order["remaining"]
                if order["direction"] == "buy":
                    amount = current_quantity*order["price"]
                    order["reservation"][1] = amount
                    self.pending_buy_balance -= order["reservation"][0] - order["reservation"][1]
                else:
                    order["reservation"][1] = current_quantity
                    self.pending_sell_quantity[order["security_ID"]] -= order["reservation"][0] - order["reservation"][1]
                    

        for idx in del_idx:
            self.orders.pop(idx)

    def execute_trade(self, security_ID, price, quantity, direction):
        if direction == "buy":
            self.withdraw_amount(price*quantity)
            self.portfolio[security_ID]["quantity"] += quantity
            avg_buy_price = self.portfolio[security_ID]["avg_buy_price"]
            total_quantity = self.portfolio[security_ID]["quantity"]
            self.portfolio[security_ID]["avg_buy_price"] = ((avg_buy_price*(total_quantity-quantity)) + (price*quantity))/(total_quantity)
        else:
            self.add_amount(price*quantity)
            self.portfolio[security_ID]["quantity"] -= quantity
            self.portfolio[security_ID]["sold_quantity"] += quantity
            avg_buy_price = self.portfolio[security_ID]["avg_buy_price"]
            self.portfolio[security_ID]["realised_pnl"] += ((price - avg_buy_price)*quantity) 

    def get_portfolio_dashboard(self):
        print("="*60)
        print(self.ID," Available Cash:",round(self.trading_account_balance,2))
        print("PORTFOLIO:")
        print("SECURITY"," "*3,"Quantity"," "*3,"Avg Buy Price"," "*3,"LTP"," "*3,"Unrealised Return"," "*3,"Realised Return")
        for security_ID, data in self.portfolio.items():
            if data["quantity"]:
                unrealised_return = data["unrealised_pnl"]*100/(data["avg_buy_price"]*data["quantity"])
                realised_return = 0   
                if data["sold_quantity"]:
                    realised_return = data["realised_pnl"]*100/(data["avg_buy_price"]*data["sold_quantity"])
                print(security_ID," "*10,data["quantity"]," "*6,round(data["avg_buy_price"],2)," "*8,round(self.exchange.securities[security_ID].get_last_traded_price(),2)," "*8,f"{unrealised_return:.2f}%"," "*8,f"{realised_return:.2f}%")
        print("TOTAL EQUITY:", round(self.get_portfolio_value()+self.trading_account_balance,2))
        print("="*60)