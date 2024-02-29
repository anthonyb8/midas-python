import unittest
import random
from datetime import datetime
from ibapi.contract import Contract
from ibapi.order import Order

from midas.events import ExecutionEvent,Trade
from midas.events import TradeInstruction, Action
            
class TestExecutionEvent(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_timetamp = 1651500000
        self.valid_trade_details = Trade(trade_id='1',
                                            leg_id='2',
                                            timestamp=datetime(2024,1,1),
                                            symbol='HEJ4',
                                            quantity=10,
                                            price= 85.98,
                                            cost=9000.90,
                                            action= random.choice(['BUY', 'SELL']),
                                            fees= 9.87)
        self.valid_action = random.choice([Action.LONG,Action.COVER,Action.SELL,Action.SHORT])
        self.valid_contract = Contract()
        self.valid_order = Order()
    
    # Basic Validation
    def test_valid_construction(self):
        exec = ExecutionEvent(timestamp=self.valid_timetamp,
                               trade_details=self.valid_trade_details,
                               action=self.valid_action,
                               contract=self.valid_contract)
        
        self.assertEqual(exec.timestamp, self.valid_timetamp)
        self.assertEqual(exec.action, self.valid_action)
        self.assertEqual(exec.contract, self.valid_contract)
        self.assertEqual(exec.trade_details, self.valid_trade_details)
        self.assertEqual(type(exec.action), Action)
        self.assertEqual(type(exec.contract), Contract)

    # Type Check
    def test_timestamp_type_validation(self):
        self.invalid_timetamp = datetime(2024,1,1)

        with self.assertRaisesRegex(TypeError,"'timestamp' should be in UNIX format of type float or int"):
            ExecutionEvent(timestamp=self.invalid_timetamp,
                               trade_details=self.valid_trade_details,
                               action=self.valid_action,
                               contract=self.valid_contract)
            
    def test_action_type_validation(self):
        with self.assertRaisesRegex(TypeError, "'action' must be of type Action enum."): 
            ExecutionEvent(timestamp=self.valid_timetamp,
                               trade_details=self.valid_trade_details,
                               action="self.valid_action",
                               contract=self.valid_contract)
            
    def test_trade_details_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'trade_details' must be of type Trade instance."): 
            ExecutionEvent(timestamp=self.valid_timetamp,
                               trade_details="elf.valid_trade_details,",
                               action=self.valid_action,
                               contract=self.valid_contract)
            
    def test_contract_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'contract' must be of type Contract instance."): 
            ExecutionEvent(timestamp=self.valid_timetamp,
                               trade_details=self.valid_trade_details,
                               action=self.valid_action,
                               contract="self.valid_contract")
    
    # Constraints
    def test_timestamp_format_validation(self):
        invalid_timestamp = "14-10-2020"
        with self.assertRaisesRegex(TypeError, "'timestamp' should be in UNIX format of type float or int"):
            ExecutionEvent(timestamp=invalid_timestamp,
                    trade_details=self.valid_trade_details,
                    action=self.valid_action,
                    contract="self.valid_contract")        
    

if __name__=="__main__":
    unittest.main()