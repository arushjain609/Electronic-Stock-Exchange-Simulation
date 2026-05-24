class StockExchange:
    def __init__(self, limit):
        self.time_limit = limit
        self.timesteps = 0
        self.securities = {}
        self.OMSs = {}
        self.order_life = 20
        self.orders = {}

    def get_timestamp(self):
        return self.timesteps
    
    def increase_timestep(self):
        self.timesteps += 1
        self.orders[self.timesteps] = {}
    
    def list_security(self, security):
        self.securities[security.ID] = security

    def list_trader_OMS(self, OMS):
        self.OMSs[OMS.ID] = OMS

    def get_last_traded_price(self, security_ID):
        return self.securities[security_ID].get_last_traded_price()
    
    def get_best_bid_and_ask(self, security_ID):
        return self.securities[security_ID].get_best_bid_and_ask()
    
    def get_top_5_bids_and_asks(self, security_ID):
        return self.securities[security_ID].get_top_5_bids_and_asks()
    
    def place_order(self, order):
        self.securities[order["security_ID"]].place_order(order)

        order_book = []
        status = ""
        if order["direction"] == "buy":
            order_book = self.securities[order["security_ID"]].order_bids
        else:
            order_book = self.securities[order["security_ID"]].order_asks

        idx = order_book.index(order)
        if idx > 4:
            status = "REJECTED"
            self.OMSs[order["trader_ID"]].orders[order["ID"]]["status"] = status
            order_book = order_book[:5]
        else:
            status = "ACCEPTED"
            order_book[idx]["status"] = status
            self.OMSs[order["trader_ID"]].orders[order["ID"]]["status"] = status
            order["status"] = "ACCEPTED"
            self.orders[self.timesteps][order["ID"]] = order
            if len(order_book) > 5:
                junk_order = order_book[-1]
                self.OMSs[junk_order["trader_ID"]].orders[junk_order["ID"]]["status"] = "REJECTED"
                self.orders[junk_order["timestamp"]][junk_order["ID"]]["status"] = "REJECTED"
                order_book = order_book[:5]

        if order["direction"] == "buy":
            self.securities[order["security_ID"]].order_bids = order_book
        else:
            self.securities[order["security_ID"]].order_asks = order_book

        return status
    
    def check_orders(self):
        for security_ID, security in self.securities.items():
            order_bids = []
            order_asks = []
            for order in security.order_bids:
                if order["timestamp"] + self.order_life >= self.timesteps:
                    order_bids.append(order)
                else:
                    self.OMSs[order["trader_ID"]].orders[order["ID"]]["status"] = "EXPIRED"
            security.order_bids = order_bids

            for order in security.order_asks:
                if order["timestamp"] + self.order_life >= self.timesteps:
                    order_asks.append(order)
                else:
                    self.OMSs[order["trader_ID"]].orders[order["ID"]]["status"] = "EXPIRED"
            security.order_asks = order_asks
        
    def matching_engine(self):
        if self.timesteps <= self.time_limit:
            for security_ID, security in self.securities.items():
                best_bid, best_ask = self.get_best_bid_and_ask(security_ID)
                while best_bid and best_ask and best_bid["price"] >= best_ask["price"]:
                    price = 0.0
                    if best_bid["timestamp"] < best_ask["timestamp"]:
                        price = best_bid["price"]
                    else:
                        price = best_ask["price"]

                    quantity = min(best_bid["remaining"],best_ask["remaining"])

                    amount = price*quantity

                    self.OMSs[best_bid["trader_ID"]].execute_trade(security_ID,price,quantity,"buy")
                    self.OMSs[best_ask["trader_ID"]].execute_trade(security_ID,price,quantity,"sell")
                    
                    security.last_traded_price = price

                    if quantity == best_bid["remaining"]:
                        security.order_bids = security.order_bids[1:]
                        self.OMSs[best_bid["trader_ID"]].orders[best_bid["ID"]]["status"] = "FILLED"
                        self.orders[best_bid["timestamp"]][best_bid["ID"]]["status"] = "FILLED"
                    else:
                        security.order_bids[0]["remaining"] -= quantity
                        self.OMSs[best_bid["trader_ID"]].orders[best_bid["ID"]]["remaining"] -= quantity
                        self.OMSs[best_bid["trader_ID"]].orders[best_bid["ID"]]["status"] = "PARTIALLY FILLED"
                        self.OMSs[best_bid["trader_ID"]].orders[best_bid["ID"]]["validation"] = 0
                        self.orders[best_bid["timestamp"]][best_bid["ID"]]["status"] = "PARTIALLY FILLED"

                    if quantity == best_ask["remaining"]:
                        security.order_asks = security.order_asks[1:]
                        self.OMSs[best_ask["trader_ID"]].orders[best_ask["ID"]]["status"] = "FILLED"
                        self.orders[best_ask["timestamp"]][best_ask["ID"]]["status"] = "FILLED"
                    else:
                        security.order_asks[0]["remaining"] -= quantity
                        self.OMSs[best_ask["trader_ID"]].orders[best_ask["ID"]]["remaining"] -= quantity
                        self.OMSs[best_ask["trader_ID"]].orders[best_ask["ID"]]["status"] = "PARTIALLY FILLED"
                        self.orders[best_ask["timestamp"]][best_ask["ID"]]["status"] = "PARTIALLY FILLED"
                        self.OMSs[best_ask["trader_ID"]].orders[best_ask["ID"]]["validation"] = 0

                    best_bid, best_ask = self.get_best_bid_and_ask(security_ID)
        else:
            for security_ID, security in self.securities.items():
                for order in self.securities[security_ID].order_bids:
                    self.OMSs[order["trader_ID"]].orders[order["ID"]]["status"] = "CANCELLED"

                for order in self.securities[security_ID].order_asks:
                    self.OMSs[order["trader_ID"]].orders[order["ID"]]["status"] = "CANCELLED"

                self.securities[security_ID].order_bids = []
                self.securities[security_ID].order_asks = []

    def get_security_dashboard(self):
        print("="*60)
        print("SECURITY"," "*3,"LTP"," "*3,"BID"," "*3,"ASK")
        for security_ID, security in self.securities.items():
            ltp,bid,ask = security.get_current_state()
            print(security_ID," "*6,f"{ltp:.2f}" if ltp else "-"," "*3,f"{bid:.2f}" if bid else "-"," "*3,f"{ask:.2f}" if ask else "-")

        print("="*60)

    def get_active_orders(self):
        print("="*60)
        print("ACTIVE ORDERS")
        for order in self.orders[self.timesteps].values():
            print(order["direction"].upper()," "*5,order["security_ID"]," "*5,order["quantity"],"@",round(order["price"],2)," "*5,order["status"])
        print("="*60)