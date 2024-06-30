
import requests
import pandas as pd
import math
import time
from datetime import datetime, timedelta

#########################
#### BEGIN VARIABLES ####
#########################
tkr = "NVDA"
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKX38EM432GQ49SYV8SA",
    "APCA-API-SECRET-KEY": "lXwrv1l82QIQvvwakv6hWQ8s6JYSmEEW9MAu7vX8"
}

url = "https://paper-api.alpaca.markets/v2"
#########################
##### END VARIABLES #####
#########################

def trades_active():
    response = requests.get(url+"/positions", headers=headers)
    if (response.status_code == 200):
      positions = response.json()
      for position in positions:
         if (len(position['symbol']) > 4):
            return True
      return False
    else:
       time.sleep(60)
       trades_active()

def puts_cycle(tkr):
   response = requests.get(url+"/positions", headers=headers)
   if (response.status_code == 200):
      positions = response.json()
      for position in positions:
         if (position['symbol']==tkr):
            if(position['qty'] >= "100"):
               return True
      return False 
   else:
      time.sleep(60)
      puts_cycle(tkr) 


def get_current_price(tkr):
    price_url = url+f"/stocks/bars/latest?symbols={tkr}"
    price_data = requests.get(price_url, headers=headers).json()
    return float(price_data['bars'][f"{tkr}"]['c'])

def get_exp_date():
    dt = datetime.now()
    td = timedelta(days=7)
    # your calculated date
    next_exp = dt + td
    return next_exp.strftime("%Y")+"-"+next_exp.strftime("%m")+"-"+next_exp.strftime("%d")

def sell_puts(tkr):
    date = get_exp_date() # ONE WEEK INTO FURUTRE YYYY-MM-DD # exp_date = get_exp_date
    curr_price = get_current_price(tkr) # USE AS UPPER BOUND
    strike_price = math.floor(curr_price - (math.ceil(curr_price * .01))) # USE AS LOWER BOUND

    puts_url = url+f"/options/contracts?underlying_symbol={tkr}&expiration_date={date}&type=put&strike_price_gte={strike_price}&strike_price_lte={curr_price}&limit=20"
    puts_resp = requests.get(puts_url, headers=headers)
    if (puts_resp.status_code == 200): #add successful request check (if response 200 and len >= 1 continue, else wait and call function)
       #submit order
       puts_data = puts_resp.json()['option_contracts']
       if (len(puts_data) >= 1 ):
        sell_puts_payload = {
            "symbol": puts_data[len(puts_data)-1]['symbol'], # EX OF id: "AAPL231201P00175000"
            "qty": "1",
            "side": "sell",
            "type": "market",
            "time_in_force": "day"
            }
        response = requests.post(url+"/orders", json=sell_puts_payload, headers=headers)
       else:
          time.sleep(300)
          sell_puts(tkr)
    else:
       time.sleep(300)
       sell_puts(tkr)

def sell_calls(tkr):
    date = get_exp_date() # ONE WEEK INTO FURUTRE YYYY-MM-DD # exp_date = get_exp_date
    strike_price = math.ceil(get_current_price())
    calls_url = url+f"/options/contracts?underlying_symbol={tkr}&expiration_date={date}&strike_price_gte={strike_price}&strike_price_lte={strike_price+1}&limit=20"
    calls_response = requests.get(calls_url, headers=headers)
    if (calls_response.status_code == 200): #add successful request check (if response 200 and len >= 1 continue, else wait and call function)
       calls_data = calls_response.json()['option_contracts']
       if (len(calls_data) >=1):
        sell_calls_payload = {
        "symbol": calls_data[len(calls_data)-1]['symbol'], # EX OF id: "AAPL231201P00175000"
        "qty": "1",
        "side": "sell",
        "type": "market",
        "time_in_force": "day"
        }
        response = requests.post(url+"/orders", json=sell_calls_payload, headers=headers)
       else:
          time.sleep(300)
          sell_calls(tkr)
    else:
       time.sleep(300)
       sell_calls(tkr)
