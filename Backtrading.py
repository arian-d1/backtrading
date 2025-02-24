import backtrader as bt
import pandas as pd
import matplotlib

import sys

from Strategies.MACDCrossover import MACDCrossover
from Strategies.PairsTrading import PairsTrading
from Data.TickerData import getTickerData


def runMACD(period, ticker, cerebro):

    file = getTickerData(ticker, period)
    df = pd.read_csv(file, parse_dates=['Date'], index_col='Date')
    data = bt.feeds.PandasData(dataname = df)

    cerebro.adddata(data) 
    cerebro.addstrategy(MACDCrossover)

    results = cerebro.run()

    getMetrics(results, cerebro)

def runPairs(period, ticker1, ticker2, cerebro):

    file1 = getTickerData(ticker1, period)
    df1 = pd.read_csv(file1, parse_dates=['Date'], index_col='Date')
    data1 = bt.feeds.PandasData(dataname = df1)

    file2 =  getTickerData(ticker2, period)
    df2 = pd.read_csv(file2, parse_dates=['Date'], index_col='Date')
    data2 = bt.feeds.PandasData(dataname = df2)

    cerebro.adddata(data1) 
    cerebro.adddata(data2) 
    cerebro.addstrategy(PairsTrading)

    results = cerebro.run()

    getMetrics(results, cerebro)

def getMetrics(results, cerebro):
    sharpe = results[0].analyzers.sharperatio.get_analysis()['sharperatio']
    annualizedReturns = results[0].analyzers.returns.get_analysis()['rnorm100']
    totalReturns = float(results[0].analyzers.returns.get_analysis()['rtot']) * 100
    maxPercentDrawdown = results[0].analyzers.drawdown.get_analysis()['max']['drawdown']
    maxDollarDrawdown = results[0].analyzers.drawdown.get_analysis()['max']['moneydown']

    print("Sharpe Ratio: ", sharpe)
    print("Annualized %% return: %.5f" % annualizedReturns)
    print("Total compounded %% return: %.5f" % totalReturns)
    print("Max %% drawdown: %.5f" % maxPercentDrawdown)
    print("Max $ drawdown: %.2f" % maxDollarDrawdown)

    print('Final Cash Value: %.2f' % cerebro.broker.getcash())
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()

def main(strategy, period, tickers):

    cerebro = bt.Cerebro()

    # Initialize start conditions
    STARTCASH = 1_000_000
    cerebro.broker.setcash(STARTCASH)
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    if (strategy == "MACD"):
        runMACD(period, tickers[0], cerebro)
    elif (strategy == "Pairs"):
        try:
            runPairs(period, tickers[0], tickers[1], cerebro)
        except IndexError:
            print("User must specify only 2 tickers to use the pairs method")
    else:
        print("No matching strategy found")
    
    print(f"Ran the {strategy} strategy over {period} days with {tickers}")

if __name__ == "__main__":
    if len(sys.argv) == 4 or len(sys.argv) == 5:
        main(sys.argv[1], int(sys.argv[2]), sys.argv[3::])
    else:
        print("Incorrent usage, try one of (period is the # of days as an integer): ")
        print("\tpython .\\Backtrading.py MACD Period \"Ticker 1\" ")
        print("\tpython .\\Backtrading.py Pairs Period \"Ticker 1\" \"Ticker 2\"")
        print("\tExample: python .\\Backtrading.py Pairs 365 AAPL MSFT")