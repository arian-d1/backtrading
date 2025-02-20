import backtrader as bt
import pandas as pd
import matplotlib

from Strategies.MACDCrossover import MACDCrossover


file = 'Data\SPY_data.csv'
df = pd.read_csv(file, parse_dates=['Date'], index_col='Date')

data = bt.feeds.PandasData(dataname = df)

cerebro = bt.Cerebro()

# Feed the data
cerebro.adddata(data)

# Initialize start conditions
STARTCASH = 1_000_000
# Risk 1% based on initial price of security
STAKE = int((STARTCASH / df['Close'].iloc[0]) * 0.01) 
cerebro.broker.setcash(STARTCASH)
cerebro.addsizer(bt.sizers.FixedSize, stake = STAKE)

# Strategies
cerebro.addstrategy(MACDCrossover)

# Analyzers
cerebro.addanalyzer(bt.analyzers.SharpeRatio)
cerebro.addanalyzer(bt.analyzers.Returns)
cerebro.addanalyzer(bt.analyzers.DrawDown)


print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
results = cerebro.run()

print('Final Cash Value: %.2f' % cerebro.broker.getcash())
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


sharpe = results[0].analyzers.sharperatio.get_analysis()['sharperatio']
returns = results[0].analyzers.returns.get_analysis()['rnorm100']
maxPercentDrawdown = results[0].analyzers.drawdown.get_analysis()['max']['drawdown']
maxDollarDrawdown = results[0].analyzers.drawdown.get_analysis()['max']['moneydown']


print("Sharpe Ratio: ", sharpe)
print("Percent return: %.5f" % returns)
print("Max drawdown in %%: %.5f" % maxPercentDrawdown)
print("Max drawdown in $: %.2f" % maxDollarDrawdown)

cerebro.plot()

