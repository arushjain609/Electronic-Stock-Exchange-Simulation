import numpy as np
import matplotlib.pyplot as plt

from StockExchange import StockExchange
from OMS import OMS
from Trader import Trader
from Security import Security

def simulation():
    TIME_LIMIT = 200
    BALANCE = 1000000

    exchange = StockExchange(TIME_LIMIT)
    print("EXCHANGE CREATED")
    securities = {}
    traders = {}
    for i in range(1,6):
        id = "S" + str(i)
        securities[id] = Security(id)
        print("SECURITY :",id," Created")
        securities[id].last_traded_price = np.random.randint(40,120)
        exchange.list_security(securities[id])

    for i in range(1,6):
        id = "T" + str(i)
        traders[id] = Trader(id, BALANCE, exchange)
        print("TRADER :",id," Created")
        quantity = [0,5000,7000]
        traders[id].OMS.portfolio = {}
        for key in securities.keys():
            traders[id].OMS.portfolio[key] = {}
            traders[id].OMS.portfolio[key]["quantity"] = np.random.choice(quantity)
            traders[id].OMS.portfolio[key]["avg_buy_price"] = securities[key].last_traded_price
            traders[id].OMS.portfolio[key]["realised_pnl"] = 0
            traders[id].OMS.portfolio[key]["unrealised_pnl"] = 0
            traders[id].OMS.portfolio[key]["sold_quantity"] = 0
            traders[id].OMS.portfolio[key]["value"] = traders[id].OMS.portfolio[key]["quantity"]*traders[id].OMS.portfolio[key]["avg_buy_price"]
        value = traders[id].OMS.get_portfolio_value()
        print("TRADER :",id," Initial Portfolio Value :",value)
        exchange.list_trader_OMS(traders[id].OMS)

    for time in range(TIME_LIMIT):
        exchange.increase_timestep()
        for trader_ID, trader in traders.items():
            for security_ID, security in securities.items():
                direction = np.random.choice(["buy","sell"])
                price = 0
                if(not (security.order_bids or security.order_asks)):
                    ltp = security.get_last_traded_price()
                    price = np.random.choice([int(ltp*1.05),int(ltp*0.95)])
                else:
                    best_bid, best_ask = security.get_best_bid_and_ask()
                    bid = 0.0
                    ask = 0.0
                    quantity = 0
                    if not best_bid:
                        ask = best_ask["price"]
                        bid = ask
                    elif not best_ask:
                        bid = best_bid["price"]
                        ask = bid
                    else:
                        ask = best_ask["price"]
                        bid = best_bid["price"]

                    if direction == "buy":
                        prob = np.random.rand()
                        if prob >= 0.2:
                            price = np.random.randint(bid-3,bid+1)
                        else:
                            price = np.random.randint(bid,ask+2)
                    else:
                        prob = np.random.rand()
                        if prob >= 0.2:
                            price = np.random.randint(ask,ask+4)
                        else:
                            price = np.random.randint(bid-1,ask+1)
                
                quantity = 1000

                trader.create_order(security_ID, price, quantity, direction)
                
        exchange.check_orders()

        exchange.matching_engine()

        if time%20 == 0:
            exchange.get_security_dashboard()
            exchange.get_active_orders()

        for trader_ID, trader in traders.items():
            trader.check_account_status()
            trader.OMS.check_order_status()
            if time%1 == 0:
                trader.OMS.get_portfolio_value()
            if time%20 == 0:
                trader.OMS.get_portfolio_dashboard()

    for trader_ID, trader in traders.items():
        plt.figure()   # create a new figure

        plt.plot(trader.OMS.portfolio_history)

        plt.title(f"Portfolio History - Trader {trader_ID}")
        plt.xlabel("Timesteps")
        plt.ylabel("Portfolio Value")

        plt.savefig(f"images/trader_{trader_ID}.png")

        plt.close() 
        
if __name__ == "__main__":
    simulation()