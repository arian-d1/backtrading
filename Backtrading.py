import backtrader as bt
import pandas as pd
import matplotlib

import sys

from Strategies.MACDCrossover import MACDCrossover
from Strategies.PairsTrading import PairsTrading
from Data.TickerData import getTickerData


def runMACD(ticker, cerebro):

    file = getTickerData(ticker, 365)
    df = pd.read_csv(file, parse_dates=['Date'], index_col='Date')
    data = bt.feeds.PandasData(dataname = df)

    cerebro.adddata(data) 
    cerebro.addstrategy(MACDCrossover)

    results = cerebro.run()

    getMetrics(results, cerebro)

def runPairs(ticker1, ticker2, cerebro):

    file1 = getTickerData(ticker1, 365)
    df1 = pd.read_csv(file1, parse_dates=['Date'], index_col='Date')
    data1 = bt.feeds.PandasData(dataname = df1)

    file2 =  getTickerData(ticker2, 365)
    df2 = pd.read_csv(file2, parse_dates=['Date'], index_col='Date')
    data2 = bt.feeds.PandasData(dataname = df2)

    cerebro.adddata(data1) 
    cerebro.adddata(data2) 
    cerebro.addstrategy(PairsTrading)

    results = cerebro.run()

    getMetrics(results, cerebro)

def getMetrics(results, cerebro):
    sharpe = results[0].analyzers.sharperatio.get_analysis()['sharperatio']
    returns = results[0].analyzers.returns.get_analysis()['rnorm100']
    maxPercentDrawdown = results[0].analyzers.drawdown.get_analysis()['max']['drawdown']
    maxDollarDrawdown = results[0].analyzers.drawdown.get_analysis()['max']['moneydown']

    print("Sharpe Ratio: ", sharpe)
    print("Percent return: %.5f" % returns)
    print("Max drawdown in %%: %.5f" % maxPercentDrawdown)
    print("Max drawdown in $: %.2f" % maxDollarDrawdown)

    print('Final Cash Value: %.2f' % cerebro.broker.getcash())
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()

def main(arg, tickers):

    cerebro = bt.Cerebro()

    # Initialize start conditions
    STARTCASH = 1_000_000
    cerebro.broker.setcash(STARTCASH)
    cerebro.addsizer(bt.sizers.FixedSize, stake=500)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    if (arg == "MACD"):
        runMACD(tickers[0], cerebro)
    elif (arg == "Pairs"):
        try:
            runPairs(tickers[0], tickers[1], cerebro)
        except IndexError:
            print("User must specify only 2 tickers to use the pairs method")
    else:
        print("No matching strategy found")

if __name__ == "__main__":
    if len(sys.argv) == 3 or len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2::])
    else:
        print("Incorrent usage, try one of: ")
        print("\tpython .\\Backtrading.py MACD \"Ticker 1\" ")
        print("\tpython .\Backtrading.py Pairs \"Ticker 1\" \"Ticker 2\"")