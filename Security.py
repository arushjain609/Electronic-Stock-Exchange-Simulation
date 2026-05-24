class Security:
    def __init__(self, ID):
        self.ID = ID
        self.last_traded_price = 0.0
        self.order_bids = []
        self.order_asks = []

    def get_last_traded_price(self):
        return self.last_traded_price
        
    def get_best_bid_and_ask(self):
        best_bid = self.order_bids[0] if len(self.order_bids) > 0 else {}
        best_ask = self.order_asks[0] if len(self.order_asks) > 0 else {}

        return best_bid, best_ask
    
    def get_top_5_bids_and_asks(self):
        return self.order_bids, self.order_asks
    
    def place_order(self,order):
        if order["direction"] == "buy":
            self.order_bids.append(order)
            self.order_bids.sort(key=lambda x: (-1*x["price"],x["timestamp"]))
        else:
            self.order_asks.append(order)
            self.order_asks.sort(key=lambda x: (x["price"],x["timestamp"]))

    def get_current_state(self):
        best_bid, best_ask = self.get_best_bid_and_ask()
        ltp = self.get_last_traded_price()
        bid = 0.0
        ask = 0.0
        if best_bid:
            bid = best_bid["price"]
        
        if best_ask:
            ask = best_ask["price"]

        return ltp, bid, ask