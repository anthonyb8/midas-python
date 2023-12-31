class BacktestResult:
    def __init__(self):
        self.strategy_name = None
        self.parameters = {}
        self.summary_stats = []
        self.trade_data = []
        self.equity_data = []
        self.signal_data = []
        self.price_data = []

    def set_strategy_name(self, name):
        self.strategy_name = name

    def set_parameters(self, parameters):
        self.parameters = parameters

    def set_summary_stats(self, summary_stats):
        self.summary_stats = summary_stats

    def set_trade_data(self, trade_data):
        self.trade_data = trade_data

    def set_equity_data(self, equity_data):
        self.equity_data = equity_data

    def set_signals(self, signal_data):
        self.signal_data = signal_data

    def set_price_data(self, price_data):
        self.price_data = price_data
        

    def to_dict(self):
        return {
            "strategy_name": self.strategy_name,
            "parameters": self.parameters,
            "summary_stats": self.summary_stats,
            "trades": self.trade_data,
            "equity_data":self.equity_data,
            "signals": self.signal_data,
            "price_data": self.price_data,
        }
