class ActiveOrder:
    def __init__(self, contract:dict, direction:str, avg_price:float, quantity:int):
        quantity = self.check_direction(direction, quantity)

        self.contract = contract
        self.direction = direction # LONG/SHORT
        self.avg_price = avg_price
        self.quantity = quantity
        self.mkt_value = self.avg_price*self.quantity # Delete after debug

    def to_dict(self):
        return {
            'trade_id': self.trade_id,
            'leg_id': self.leg_id,
            'timestamp': self.timestamp,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'price': self.price,
            'cost': self.cost,
            'direction': self.direction
        }
    

class OrderManager:
    def __init__(self):
        self.active_orders = {}

    def update_active_orders(self, data):
        # If the status is 'Cancelled' and the order is present in the dict, remove it
        if data['status'] == 'Cancelled' or data['status'] == 'Filled' and data['permId'] in self.active_orders:
            del self.active_orders[data['permId']]
        # If not cancelled, either update the existing order or add a new one
        elif data['status'] != 'Cancelled' and data['status'] != 'Filled':
            if data['permId'] not in self.active_orders:
                self.active_orders[data['permId']] = data
            else:
                self.active_orders[data['permId']].update(data)

    def __str__(self) -> str:
        string =""
        for permId, order in self.active_orders.items():
            string += f" {order} \n"
        return string