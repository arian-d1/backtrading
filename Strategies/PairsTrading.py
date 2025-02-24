import backtrader as bt


class PairsTrading(bt.Strategy):
    params = (('lookback', 20), ('entry_threshold', 1), ('exit_threshold', 0.5))


    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Get price series for the two assets
        self.data0_close = self.datas[0].close # AAPL
        self.data1_close = self.datas[1].close # MSFT
        
        # Spread Calculation: price difference
        self.spread = self.data0_close - self.data1_close
        
        # Rolling Mean and Standard Deviation for Z-score calculation
        self.spread_mean = bt.indicators.SimpleMovingAverage(self.spread, period=self.params.lookback)
        self.spread_std = bt.indicators.StandardDeviation(self.spread, period=self.params.lookback)
        
        # Z-score of the spread
        self.z_score = (self.spread - self.spread_mean) / self.spread_std

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

    
    # Notify Strategy upon a change to order
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else: 
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None # No longer have an order in the queue

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))



    def next(self):

        # Check if an order is pending. If true, cannot place another order.
        if self.order:
            return
        
        z = self.z_score[0]
        
        # Entry logic
        if z > self.params.entry_threshold:
            self.sell(data=self.datas[0])  # Short first asset
            self.buy(data=self.datas[1])   # Long second asset
        elif z < -self.params.entry_threshold:
            self.buy(data=self.datas[0])   # Long first asset
            self.sell(data=self.datas[1])  # Short second asset
        # Exit logic (mean reversion)
        elif abs(z) < self.params.exit_threshold:
            self.close(self.datas[0])
            self.close(self.datas[1])