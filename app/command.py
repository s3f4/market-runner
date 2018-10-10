import getopt
import sys

from exchange import Exchange
from util import Util
import json


class Command(object):

    def __init__(self):
        self.market_name = None
        self.market = None
        self.operation = None
        self.userId = None
        self.price = None
        self.code = None
        self.symbols = None
        self.symbol = None
        self.quote = None
        self.limit = None
        self.params = None
        self.since = None
        self.orderType = None
        self.id = None
        self.params = None
        self.timeframe = None
        self.side = None
        self.amount = None
        self.tag = None
        self.address = None

    def __get_command_args(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "m:o:u:p:c:", ["market", "operation", "userId", "price", "symbol"])
        except getopt.GetoptError as err:
            print(err)
            sys.exit(0)
        return opts, args

    def __set_params(self):
        opts = self.__get_command_args()
        for optTuple in opts:
            for opt, arg in optTuple:
                if opt == "-m":
                    self.market_name = arg
                if opt == "-o":
                    self.operation = arg
                if opt == "-u":
                    self.userId = arg
                if opt == "-p":
                    self.price = arg
                if opt == "-c":
                    self.symbol = arg
                if opt == "-q":
                    self.quote = arg
                if opt == "-i":
                    self.id = arg

    def execute(self):
        """

        :rtype: object
        """
        keys = Util.get_api_params()
        self.__set_params()

        self.market = Exchange(self.market_name,
                               keys[self.market_name]["apiKey"],
                               keys[self.market_name]["apiSecret"])
        print(self.__call_market_function())

    def __call_market_function(self):
        '''
        Call proper market functions.
        :return:
        '''
        if self.params is not None:
            self.params = json.loads(self.params)
        else:
            self.params = {}

        if self.symbols is not None:
            self.symbols = json.loads(self.symbols)

        if self.operation == "fetch_markets":
            result = getattr(self.market, self.operation)()
        elif self.operation in ["fetch_balance", "fetch_currencies"]:
            result = getattr(self.market, self.operation)(self.params)
        elif self.operation == "fetch_tickers":
            result = getattr(self.market, self.operation)(self.symbols, self.params)
        elif self.operation == "fetch_order_book":
            result = getattr(self.market, self.operation)(self.symbol, self.limit, self.params)
        elif self.operation in ["fetch_trades", "fetch_open_orders", "fetch_closed_orders"]:
            result = getattr(self.market, self.operation)(
                self.symbol,
                self.since,
                self.limit,
                self.params
            )
        elif self.operation == "fetch_ticker":
            result = getattr(self.market, self.operation)(self.symbol, self.params)
        elif self.operation == "fetch_ohlcv":
            result = getattr(self.market, self.operation)(
                self.symbol,
                self.timeframe,
                self.since,
                self.limit,
                self.params
            )
        elif self.operation == "create_order":
            result = getattr(self.market, self.operation)(
                self.symbol,
                self.orderType,
                self.side,
                self.amount,
                self.price,
                self.params
            )
        elif self.operation in ["create_order", "fetch_order"]:
            result = getattr(self.market, self.operation)(
                self.id,
                self.symbol,
                self.params
            )
        elif self.operation == "fetch_deposit_address":
            result = getattr(self.market, self.operation)(self.code, self.params)
        elif self.operation == "withdraw":
            result = getattr(self.market, self.operation)(
                self.code,
                self.amount,
                self.address,
                self.tag,
                self.params
            )
        return result

    def __price_control(self, price=None):
        if price is not None:
            if not Util.isfloat(price):
                print("price is not float")
                sys.exit(0)


if __name__ == '__main__':
    command = Command()
    command.execute()
