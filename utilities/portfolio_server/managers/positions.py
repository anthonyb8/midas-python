class Position:
    def __init__(self, symbol:str, direction:str, avg_price:float, quantity:int):
        quantity = self.check_direction(direction, quantity)

        self.symbol = symbol
        self.direction = direction
        self.avg_price = avg_price
        self.quantity = quantity
        self.mkt_value = self.avg_price*self.quantity # Delete after debug

    def update(self, direction:str, price:float, quantity:int):
        """Update the position's details based on a new execution event."""
        total_cost_before = self.avg_price * self.quantity
        total_cost_event = price * quantity
        
        # Update average price
        if self.quantity != 0:
            self.avg_price = (total_cost_before + total_cost_event) / self.quantity
        self.direction = direction

    def check_direction(self, direction, quantity):
        if direction =='BUY':
            return abs(quantity)
        elif direction == 'SELL':
            return quantity * -1
        else:
            raise ValueError(f"Direction: {direction} not in ['BUY', 'SELL'].")


class PositionsManager:
    def __init__(self):
        self.positions = {}

    def update(self, symbol:str, direction:str, price:float, quantity:int):
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol, direction, price, quantity)
        else:
            self.positions[symbol].update(direction, price, quantity)
            if self.positions[symbol].quantity == 0:
                del self.positions[symbol]

    # def value_at(self, current_price:float) -> float:
    #     if self.direction == 'LONG':
    #         return self.quantity * current_price
    #     elif self.direction == 'SHORT':
    #         return -self.quantity * current_price
    #     return 0

    # def total_value(self, price_data:dict) -> float:
    #     total = 0
    #     for symbol, position in self.positions.items():
    #         current_price = price_data[symbol]
    #         total += position.value_at(current_price)
    #     return total
