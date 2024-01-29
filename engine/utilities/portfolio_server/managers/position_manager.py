
class Position:
    def __init__(self, direction:str, avg_price:float, quantity:int, total_cost: float):
        self.direction = direction # BUY/SELL
        self.avg_price = avg_price
        self.quantity = quantity
        self.total_cost = total_cost

class PositionManager:
    def __init__(self):
        self.positions = {}

    def update(self, contract, position_data):
        contract_id = contract.conId
        self.positions[contract_id] = Position(position_data['direction'],position_data['avg_cost'], position_data['quantity'], position_data['total_cost'])

    def __str__(self) -> str:
        string =""
        for contract, position in self.positions.items():
            string += f" {contract}: {position.__dict__} \n"
        return string