import Wheel_Controller as wc
import time

tkr = "NVDA"
while(True):
  if (wc.trades_active()): #If trade active wait
    time.sleep(3600)
  elif(wc.puts_cycle(tkr)): #If  own 100 stocks
    wc.sell_puts(tkr)
  else:
    wc.sell_calls(tkr)
