import logging
from queue import Queue
from datetime import datetime
from ibapi.contract import Contract
from ibapi.order import Order

from .dummy_broker import DummyBroker
from midas.portfolio import PortfolioServer
from midas.account_data import Position, Trade
from midas.events import ExecutionEvent, OrderEvent, TradeInstruction, Action

class BrokerClient:
    """
    Simulates the broker, controls the execution of trades and the updating of 'account' data.
    """
    def __init__(self,event_queue: Queue, logger: logging.Logger, portfolio_server: PortfolioServer, broker:DummyBroker):
        # Subscriptions
        self.portfolio_server = portfolio_server
        self.broker = broker
        self.logger = logger
        self.event_queue = event_queue

        self.update_account()
        
    def on_order(self, event: OrderEvent):
        """
        The Order Event listener, called when a new order event is intercepted in the queue.

        Args:
            OrderEvent (Object) : Event with all the data related to a specific order to be executed.

        """
        timestamp = event.timestamp
        trade_instructions = event.trade_instructions
        contract = event.contract
        order = event.order
        action= event.trade_instructions.action

        self.handle_order(timestamp, trade_instructions,action ,contract,order)

    def handle_order(self, timestamp, trade_instructions:TradeInstruction, action:Action, contract:Contract, order:Order):
        """
        Handles the the execution of the order, simulation the placing of order and creation of execution event.
        
        Args:
            contract (Object) : Class containing the specfics related to the symbol ex. ticker, exchange, currency
            order (Object) : Class that contains all the data related to a specific orde. ex OrderType(market, limit), and assocated data ex. limit price
            signal (Object) : Inititial signal object, used to pass signal data to trade client for updating the portfolio related fields.
            market_data (Object) : Initial MarketDataEvent, used to pass data not included in the signal or order to the trade client for portfolio updating.

        """

        self.broker.placeOrder(timestamp, trade_instructions, action ,contract, order)

    def on_execution(self, event:ExecutionEvent):
        self.update_positions()
        self.update_account()
        self.update_trades()
  
    def eod_update(self):
        self.broker.mark_to_market()
        self.broker.check_margin_call()
        self.update_account()
   
    def update_positions(self):
        positions = self.broker.return_positions()
        for contract, position_data in positions.items():
            # Convert the `PositionDetails` TypedDict into a `Position` data class instance.
            position_instance = Position(
                action=position_data['action'],
                avg_cost=position_data['avg_cost'],
                quantity=position_data['quantity'],
                contract_size=position_data['contract_size'],
                initial_margin=position_data['initial_margin'],
                total_cost=position_data.get('total_cost', 0)  # Provide a default value if not present
            )

            # Now, use `position_instance` as needed, for example, to update positions in the portfolio server.
            self.portfolio_server.update_positions(contract, position_instance)

    def update_trades(self):
        last_trades = self.broker.return_ExecutedTrade()
        for contract, trade in last_trades.items():
            # Convert the `ExecutiuonDetails` TypedDict into a `Trade` data class instance.
            trade_instance = Trade(
                trade_id= trade['trade_id'],
                leg_id= trade['leg_id'],
                timestamp= trade['timestamp'],
                symbol= trade['symbol'],
                quantity= trade['quantity'],
                price= trade['price'],
                cost= trade['cost'],
                action= trade['action'],
                fees= trade['fees']
            )

            self.portfolio_server.update_trades(trade_instance)

    def update_account(self):
        account = self.broker.return_account()
        self.portfolio_server.update_account_details(account)

    def update_EquityValue(self):
        self.broker.update_equity_value()
        equity = self.broker.return_EquityValue()
        self.portfolio_server.update_equity(equity)
        # self.portfolio_server.update_account_details({'EquityValue':{'timestamp': account['Timestamp'], 'equity_value':account['EquityValue']}})


    def liquidate_positions(self):
        """
        Handles the liquidation of positions, typically on the last marketdataevent, to get allow for full performance calculations.
        """
        self.update_positions()
        self.update_account()
        self.update_EquityValue()
        self.broker.liquidate_positions()
        self.update_trades()