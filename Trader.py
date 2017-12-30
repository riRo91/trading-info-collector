import datetime
import csv

from time import sleep
from bittrex import Bittrex, SELL_ORDERBOOK, BUY_ORDERBOOK

RESULT = u'result'
SUCCESS = u'success'
AVAILABLE = u'Available'
QUANTITY = u'Quantity'
RATE = u'Rate'
UUID = u'uuid'
CLOSED = u'Closed'
IS_OPEN = u'IsOpen'
FALSE_STATE = {SUCCESS: False}
BTC = 'BTC'
MARKET_NAME = u'MarketName'

class Trader(object):
    def __init__(self, apikey, apisecret):
        self.api = Bittrex(apikey, apisecret)
        self._btc_balance = FALSE_STATE
        self.available_btc_balance = 0



    def force_update_btc_balance(self):
        self._btc_balance = FALSE_STATE
        while not self._btc_balance[SUCCESS]:
            self._btc_balance = self.api.get_balance(BTC)
            self.available_btc_balance = self._btc_balance[RESULT][AVAILABLE]

    def get_minimum_wanted_price(self, amount, orderbook_result):
        '''
        :param amount: amount of BTC to spend
        :param orderbook_result: current orderbook of sold coins
        :return: the minimum price to buy wanted ammount
        '''
        i = 0
        while amount > 0:
            amount -= (orderbook_result[i][QUANTITY] * orderbook_result[i][RATE])
            i += 1
        return orderbook_result[i - 1][RATE]

    def is_order_done(self, uuid):
        '''
        :param uuid: order uuid string
        :return: true if the order is no longer open
        '''
        order = FALSE_STATE
        while not order[SUCCESS]:
            order = self.api.get_order(uuid)
        if order[RESULT][IS_OPEN]:
            return False
        return True


    def buy_and_sell_with_profit(self, market, amount, percent_above_asked, percent_profit):
        """
        :param market: (the coin you want to pay with)-(the coin you want to buy).
                        i.e. 'BTC-ETH' will buy ethereum using bitcoin

        :param amount: Number of BitCoins (float) you want to spend on the coin

        :param percent_above_asked: will take the lowest asked price and offer by this percent much more in %.
                                    (minimum is zero)

        :param percent_profit: perform immediate sell on the price bought + this amount in %.

        :return: success status of the order
        """
        if percent_above_asked < 0:
            return
        if percent_profit < 0:
            return

        self.force_update_btc_balance()

        current_sell_orderbook = FALSE_STATE
        while not current_sell_orderbook[SUCCESS]:
            current_sell_orderbook = self.api.get_orderbook(market, SELL_ORDERBOOK, 100)

        minimun_wanted_price = self.get_minimum_wanted_price(amount, current_sell_orderbook[RESULT])
        wanted_price_with_percents = minimun_wanted_price * (1 + (float(percent_above_asked) / 100))
        altcoins_amount = float(amount) / wanted_price_with_percents

        buy_result = FALSE_STATE
        #TODO: consider making sure the oreder recived using the order section or the available BTC balance
        while not buy_result[SUCCESS]:
            buy_result = self.api.buy_limit(market, altcoins_amount, wanted_price_with_percents)
        print 'Placed buy order at: ' + str(datetime.datetime.now()) + '\n'
        order_id = buy_result[RESULT][UUID]

        while not self.is_order_done(order_id):
            sleep(1)
        print 'Performed buy order at: ' + self.api.get_order(order_id)[RESULT][CLOSED]

        sell_result = FALSE_STATE
        #TODO: consider making sure the oreder recived using the order section or the available altcoins balance
        while not sell_result[SUCCESS]:
            sell_result = self.api.sell_limit(market, altcoins_amount,
                                              wanted_price_with_percents * (1 + (float(percent_profit) / 100)))
        print 'Placed sell order at: ' + str(datetime.datetime.now()) + '\n'

    def _get_all_markets(self):
        list_of_all_markets = [market[MARKET_NAME] for market in self.api.get_markets['result']]

    def update_csv_files(self):
        

'''
list_of_all_markets = [market[MARKET_NAME] for market in api.get_markets['result']]
for market in list_of_all_markets:
.....

time handling library:
yyyy-mm-ddThh:mm:ss.zzz format


'''
