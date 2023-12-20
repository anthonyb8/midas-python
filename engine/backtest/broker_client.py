import logging
from engine.base.events import ExecutionEvent
from engine.base.data import PositionsManager

class BrokerClient:
    """
    Simulates the broker, controls the execution of trades and the updating of 'account' data.
    """
    def __init__(self, logger: logging.Logger):
        self.position_manager = PositionsManager()
        self.capital = 10000  # Placeholder, replace with dynamic initialization if necessary
        self.logger = logger

    @property
    def positions(self):
        return self.position_manager.positions

    def on_execution(self, event: ExecutionEvent):
        contract = event.contract
        direction = event.order.action
        price = event.fill_price
        quantity = event.quantity
        timestamp = event.timestamp

        self._update_position(contract, direction, price, quantity)
        self._update_capital(direction, quantity, price)

    def _update_position(self, contract, direction, price, quantity):
        self.position_manager.update_or_add_position(contract, direction, price, quantity)
        self.logger.info(f"Updated Position: {contract}")

    def _update_capital(self, direction, quantity, price):
        multiplier = 0

        if direction == 'BUY':
            multiplier = 1
        elif direction == 'SELL':
            multiplier = -1
        else:
            raise ValueError(f"Direction: {direction} not in ['BUY','SELL']")

        self.capital += (multiplier * quantity) * price 
        self.logger.info(f"Updated Capital: {self.capital}")

    def liquidate_positions(self):
        """
        Handles the liquidation of positions, typically on the last marketdataevent, to get allow for full performance calculations.
        """
        liquidated_positions = {}

        for contract, position in self.positions.items():
            liquidated_positions[contract]  = {
                'quantity' :position.quantity * -1,
                'direction' : 'BUY' if position.direction =='SELL' else 'SELL',
            }
        return liquidated_positions
        