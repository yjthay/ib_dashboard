from py_vollib.black_scholes.greeks.analytical import *
from py_vollib.black_scholes import black_scholes
import datetime
import pandas as pd

tday = datetime.date.today()
expiry = datetime.date(2020, 9, 18)
output = []
multiplier = 1000
for t in range(1, (expiry - tday).days):
    for S in range(200, 351):
        delta_calc = delta("c", S, 280, t / 365, 0.05, 0.3) * multiplier
        gamma_calc = gamma("c", S, 280, t / 365, 0.05, 0.3) * multiplier
        theta_calc = theta("c", S, 280, t / 365, 0.05, 0.3) * multiplier
        vega_calc = vega("c", S, 280, t / 365, 0.05, 0.3) * multiplier
        value = black_scholes("c", S, 280, t / 365, 0.05, 0.3) * multiplier
        output.append((delta_calc, gamma_calc, theta_calc, vega_calc,value, expiry - datetime.timedelta(days=t), S))

output = pd.DataFrame(output, columns=['delta', 'gamma', 'theta', 'vega','value', 't', 'spot'])
output.index = [output['t'], output['spot']]
output = output.stack().reset_index()
output.columns = ['date','spot','plot_type', 'value']
output.to_csv("spx_test.csv")
