import backtrader as bt

class MACDCrossover(bt.Strategy):

    params = (('rsi_period', 14),
              ('MACD_entry', 0.05),
              ('MACD_exit', 0),
              ('RSI_entry_low', 30),
              ('RSI_entry_high', 50),
              ('RSI_exit', 70),
              ) 

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.MACD = bt.indicators.MACDHisto(self.datas[0])
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

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
        # Log the closing price of the series from the reference
        # self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending. If true, cannot place another order.
        if self.order:
            return
        
        # Check if there is already a position in play
        if not self.position:
            if self.rsi[0] <= self.params.RSI_entry_high and self.rsi[0] >= self.params.RSI_entry_low and self.MACD >= self.params.MACD_entry:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
                

        elif self.rsi[0] >= self.params.RSI_exit or  self.MACD < self.params.MACD_exit:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

