import unittest
import random
from datetime import datetime

from midas.account_data import Position, Trade


#TODO:  Edge case testing 

class TestPosition(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_action =  random.choice(['BUY', 'SELL'])
        self.valid_avg_cost = 10.90
        self.valid_quantity = 100
        self.valid_multiplier = 10
        self.valid_initial_margin = 100.90
        self.valid_total_cost = 9000.90
        self.valid_market_value = 1000000.9
    
    # Basic Validation
    def test_construction(self):
        position = Position(action=self.valid_action,
                            avg_cost=self.valid_avg_cost,
                            quantity=self.valid_quantity,
                            multiplier=self.valid_multiplier,
                            initial_margin=self.valid_initial_margin,
                            total_cost=self.valid_total_cost,
                            market_value=self.valid_market_value)
    
        self.assertEqual(type(position), Position)
    
    def test_equality(self):
        base_position = Position(action='BUY',
                    avg_cost=self.valid_avg_cost,
                    quantity=self.valid_quantity,
                    multiplier=self.valid_multiplier,
                    initial_margin=self.valid_initial_margin,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)
        
        new_position = Position(action="BUY", 
                    avg_cost=self.valid_avg_cost,
                    quantity=self.valid_quantity,
                    multiplier=self.valid_multiplier,
                    initial_margin=self.valid_initial_margin,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)
        
        self.assertTrue(new_position ==  base_position)

    def test_inequality_action(self):
        base_position = Position(action='BUY',
                    avg_cost=self.valid_avg_cost,
                    quantity=self.valid_quantity,
                    multiplier=self.valid_multiplier,
                    initial_margin=self.valid_initial_margin,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)
        
        new_position = Position(action="SELL", 
                    avg_cost=self.valid_avg_cost,
                    quantity=self.valid_quantity,
                    multiplier=self.valid_multiplier,
                    initial_margin=self.valid_initial_margin,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)

        self.assertFalse(new_position == base_position)

    def test_inequality_avg_cost(self):
        base_position = Position(action='BUY',
                    avg_cost=10,
                    quantity=self.valid_quantity,
                    multiplier=self.valid_multiplier,
                    initial_margin=self.valid_initial_margin,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)
        
        new_position = Position(action="BUY", 
                    avg_cost=20,
                    quantity=self.valid_quantity,
                    multiplier=self.valid_multiplier,
                    initial_margin=self.valid_initial_margin,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)

        self.assertFalse(new_position == base_position)

    def test_inequality_quantity(self):
        base_position = Position(action='BUY',
                    avg_cost=self.valid_avg_cost,
                    quantity=9,
                    multiplier=self.valid_multiplier,
                    initial_margin=self.valid_initial_margin,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)
        
        new_position = Position(action="BUY", 
                    avg_cost=self.valid_avg_cost,
                    quantity=10,
                    multiplier=self.valid_multiplier,
                    initial_margin=self.valid_initial_margin,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)

        self.assertFalse(new_position == base_position)

    def test_inequality_multiplier(self):
        base_position = Position(action='BUY',
                    avg_cost=self.valid_avg_cost,
                    quantity=self.valid_quantity,
                    multiplier=60,
                    initial_margin=self.valid_initial_margin,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)
        
        new_position = Position(action="BUY", 
                    avg_cost=self.valid_avg_cost,
                    quantity=self.valid_quantity,
                    multiplier=90,
                    initial_margin=self.valid_initial_margin,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)

        self.assertFalse(new_position == base_position)

    def test_inequality_initial_margin(self):
        base_position = Position(action='BUY',
                    avg_cost=self.valid_avg_cost,
                    quantity=self.valid_quantity,
                    multiplier=self.valid_multiplier,
                    initial_margin=9000,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)
        
        new_position = Position(action="BUY", 
                    avg_cost=self.valid_avg_cost,
                    quantity=self.valid_quantity,
                    multiplier=self.valid_multiplier,
                    initial_margin=8657,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)

        self.assertFalse(new_position == base_position)

    def test_inequality_total_cost(self):
        base_position = Position(action='BUY',
                    avg_cost=self.valid_avg_cost,
                    quantity=self.valid_quantity,
                    multiplier=self.valid_multiplier,
                    initial_margin=self.valid_initial_margin,
                    total_cost=-9000,
                    market_value=self.valid_market_value)
        
        new_position = Position(action="BUY", 
                    avg_cost=self.valid_avg_cost,
                    quantity=self.valid_quantity,
                    multiplier=self.valid_multiplier,
                    initial_margin=self.valid_initial_margin,
                    total_cost=9000,
                    market_value=self.valid_market_value)

        self.assertFalse(new_position == base_position)

    # Type/Constraint Validation
    def test_action_type_validation(self):
        with self.assertRaisesRegex(TypeError, "action must be of type str"):
            Position(action=1234,
                        avg_cost=self.valid_avg_cost,
                        quantity=self.valid_quantity,
                        multiplier=self.valid_multiplier,
                        initial_margin=self.valid_initial_margin,
                        total_cost=self.valid_total_cost,
                        market_value=self.valid_market_value)

    def test_avg_cost_type_validation(self):
        with self.assertRaisesRegex(TypeError, "avg_cost must be of type int or float"):
            Position(action=self.valid_action,
                        avg_cost="self.valid_avg_cost",
                        quantity=self.valid_quantity,
                        multiplier=self.valid_multiplier,
                        initial_margin=self.valid_initial_margin,
                        total_cost=self.valid_total_cost,
                        market_value=self.valid_market_value)

    def test_quantity_type_validation(self):
        with self.assertRaisesRegex(TypeError,"quantity must be of type int or float"):
            Position(action=self.valid_action,
                        avg_cost=self.valid_avg_cost,
                        quantity="self.valid_quantity",
                        multiplier=self.valid_multiplier,
                        initial_margin=self.valid_initial_margin,
                        total_cost=self.valid_total_cost,
                        market_value=self.valid_market_value)

    def test_multiplier_type_validation(self):
        with self.assertRaisesRegex(TypeError, "multiplier must be of type int"):
            Position(action=self.valid_action,
                        avg_cost=self.valid_avg_cost,
                        quantity=self.valid_quantity,
                        multiplier="self.valid_multiplier",
                        initial_margin=self.valid_initial_margin,
                        total_cost=self.valid_total_cost,
                        market_value=self.valid_market_value)
            
    def test_initial_margin_type_validation(self):
        with self.assertRaisesRegex(TypeError, "initial_margin must be of type int or float"):
            Position(action=self.valid_action,
                        avg_cost=self.valid_avg_cost,
                        quantity=self.valid_quantity,
                        multiplier=self.valid_multiplier,
                        initial_margin="self.valid_initial_margin",
                        total_cost=self.valid_total_cost,
                        market_value=self.valid_market_value)
            
    def test_total_cost_type_validation(self):
        with self.assertRaisesRegex(TypeError, "total_cost must be of type int or float"):
            Position(action=self.valid_action,
                        avg_cost=self.valid_avg_cost,
                        quantity=self.valid_quantity,
                        multiplier=self.valid_multiplier,
                        initial_margin=self.valid_initial_margin,
                        total_cost="self.valid_total_cost,",
                        market_value=self.valid_market_value)
                
    def test_market_value_type_validation(self):
        with self.assertRaisesRegex(TypeError, "market_value must be of type int or float"):
            Position(action=self.valid_action,
                        avg_cost=self.valid_avg_cost,
                        quantity=self.valid_quantity,
                        multiplier=self.valid_multiplier,
                        initial_margin=self.valid_initial_margin,
                        total_cost=self.valid_total_cost,
                        market_value="self.valid_market_value)")

    def test_action_value_constraint(self):
        with self.assertRaisesRegex(ValueError,"action must be either 'BUY' or 'SELL'"):
            Position(action="Cover",
                        avg_cost=self.valid_avg_cost,
                        quantity=self.valid_quantity,
                        multiplier=self.valid_multiplier,
                        initial_margin=self.valid_initial_margin,
                        total_cost=self.valid_total_cost,
                        market_value=self.valid_market_value)
            
    def test_multiplier_negative_constraint(self):
        with self.assertRaisesRegex(ValueError,"multiplier must be greater than zero"):
            Position(action=self.valid_action,
                avg_cost=self.valid_avg_cost,
                quantity=self.valid_quantity,
                multiplier=-1,
                initial_margin=self.valid_initial_margin,
                total_cost=self.valid_total_cost,
                market_value=self.valid_market_value)
    
    def test_multiplier_zero_constraint(self):
        with self.assertRaisesRegex(ValueError,"multiplier must be greater than zero"):
            Position(action=self.valid_action,
                avg_cost=self.valid_avg_cost,
                quantity=self.valid_quantity,
                multiplier=0,
                initial_margin=self.valid_initial_margin,
                total_cost=self.valid_total_cost,
                market_value=self.valid_market_value)

    def test_initial_margin_negative_constraint(self):
        with self.assertRaisesRegex(ValueError,"initial_margin must be non-negative."):
            Position(action=self.valid_action,
                avg_cost=self.valid_avg_cost,
                quantity=self.valid_quantity,
                multiplier=self.valid_multiplier,
                initial_margin=-1.1,
                total_cost=self.valid_total_cost,
                market_value=self.valid_market_value)
            
    def test_equality_position_type_validation(self):
        base_position = Position(action=self.valid_action,
                    avg_cost=self.valid_avg_cost,
                    quantity=self.valid_quantity,
                    multiplier=self.valid_multiplier,
                    initial_margin=self.valid_initial_margin,
                    total_cost=self.valid_total_cost,
                    market_value=self.valid_market_value)
        
        # Creating a random other object to compare to
        class RandomObject:
            def __init__(self):
                self.some_attribute = random.randint(1, 100)

        random_object = RandomObject()
        self.assertFalse(base_position == random_object, "A Position should not be equal to an instance of a different class")

class TestTrade(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_trade_id = '1'
        self.valid_leg_id = '2'
        self.valid_timetamp = datetime(2024,1,1) 
        self.valid_symbol = 'HEJ4'
        self.valid_quantity = 10
        self.valid_price= 85.98
        self.valid_cost = 900.90
        self.valid_action = random.choice(['BUY', 'SELL'])
        self.valid_fees = 9.87
    
    # Basic Validation
    def test_valid_construction(self):
        trade = Trade(trade_id=self.valid_trade_id,
                      leg_id=self.valid_leg_id,
                      timestamp=self.valid_timetamp,
                      symbol=self.valid_symbol,
                      quantity=self.valid_quantity,
                      price=self.valid_price,
                      cost=self.valid_cost,
                      action=self.valid_action,
                      fees=self.valid_fees)
        
        self.assertEqual(trade.trade_id, self.valid_trade_id)
        self.assertEqual(trade.leg_id, self.valid_leg_id)
        self.assertEqual(trade.timestamp, self.valid_timetamp)
        self.assertEqual(trade.symbol, self.valid_symbol)
        self.assertEqual(trade.quantity, self.valid_quantity)
        self.assertEqual(trade.price, self.valid_price)
        self.assertEqual(trade.cost, self.valid_cost)
        self.assertEqual(trade.action, self.valid_action)
        self.assertEqual(trade.fees, self.valid_fees)

    # Type Validation
    def test_trade_id_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'trade_id' must be of type str"):
            Trade(trade_id=1,
                      leg_id=self.valid_leg_id,
                      timestamp=self.valid_timetamp,
                      symbol=self.valid_symbol,
                      quantity=self.valid_quantity,
                      price=self.valid_price,
                      cost=self.valid_cost,
                      action=self.valid_action,
                      fees=self.valid_fees)
            
    def test_leg_id_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'leg_id' must be of type str"):
            Trade(trade_id=self.valid_trade_id,
                      leg_id=2,
                      timestamp=self.valid_timetamp,
                      symbol=self.valid_symbol,
                      quantity=self.valid_quantity,
                      price=self.valid_price,
                      cost=self.valid_cost,
                      action=self.valid_action,
                      fees=self.valid_fees)
            
    def test_timestamp_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'timestamp' must be of type datetime"):
            Trade(trade_id=self.valid_trade_id,
                      leg_id=self.valid_leg_id,
                      timestamp="2022-08-08",
                      symbol=self.valid_symbol,
                      quantity=self.valid_quantity,
                      price=self.valid_price,
                      cost=self.valid_cost,
                      action=self.valid_action,
                      fees=self.valid_fees)
            
    def test_symbol_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'symbol' must be of type str"):
            Trade(trade_id=self.valid_trade_id,
                      leg_id=self.valid_leg_id,
                      timestamp=self.valid_timetamp,
                      symbol=1234,
                      quantity=self.valid_quantity,
                      price=self.valid_price,
                      cost=self.valid_cost,
                      action=self.valid_action,
                      fees=self.valid_fees)
            
    def test_quantity_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'quantity' must be of type float or int"):
            Trade(trade_id=self.valid_trade_id,
                      leg_id=self.valid_leg_id,
                      timestamp=self.valid_timetamp,
                      symbol=self.valid_symbol,
                      quantity="1234",
                      price=self.valid_price,
                      cost=self.valid_cost,
                      action=self.valid_action,
                      fees=self.valid_fees)
            
    def test_price_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'price' must be of type float or int"):
            Trade(trade_id=self.valid_trade_id,
                      leg_id=self.valid_leg_id,
                      timestamp=self.valid_timetamp,
                      symbol=self.valid_symbol,
                      quantity=self.valid_quantity,
                      price="90.9",
                      cost=self.valid_cost,
                      action=self.valid_action,
                      fees=self.valid_fees)
            
    def test_cost_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'cost' must be of type float or int"):
            Trade(trade_id=self.valid_trade_id,
                      leg_id=self.valid_leg_id,
                      timestamp=self.valid_timetamp,
                      symbol=self.valid_symbol,
                      quantity=self.valid_quantity,
                      price=self.valid_price,
                      cost="90.90",
                      action=self.valid_action,
                      fees=self.valid_fees)
            
    def test_action_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'action' must be of type str"):
            Trade(trade_id=self.valid_trade_id,
                      leg_id=self.valid_leg_id,
                      timestamp=self.valid_timetamp,
                      symbol=self.valid_symbol,
                      quantity=self.valid_quantity,
                      price=self.valid_price,
                      cost=self.valid_cost,
                      action=12234,
                      fees=self.valid_fees)
            
    def test_fees_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'fees' must be of type float or int"):
            Trade(trade_id=self.valid_trade_id,
                      leg_id=self.valid_leg_id,
                      timestamp=self.valid_timetamp,
                      symbol=self.valid_symbol,
                      quantity=self.valid_quantity,
                      price=self.valid_price,
                      cost=self.valid_cost,
                      action=self.valid_action,
                      fees="90.99")
            
    # Constraint validation
    def test_action_constraint(self):
        with self.assertRaisesRegex(ValueError,"'action' must be either 'BUY' or 'SELL'"):
            Trade(trade_id=self.valid_trade_id,
                      leg_id=self.valid_leg_id,
                      timestamp=self.valid_timetamp,
                      symbol=self.valid_symbol,
                      quantity=self.valid_quantity,
                      price=self.valid_price,
                      cost=self.valid_cost,
                      action='LONG',
                      fees=self.valid_fees)
            
    def test_price_negative_constraint(self):
        with self.assertRaisesRegex(ValueError,"'price' must be greater than zero"):
            Trade(trade_id=self.valid_trade_id,
                      leg_id=self.valid_leg_id,
                      timestamp=self.valid_timetamp,
                      symbol=self.valid_symbol,
                      quantity=self.valid_quantity,
                      price=-1.0,
                      cost=self.valid_cost,
                      action=self.valid_action,
                      fees=self.valid_fees)
            
    def test_price_zero_constraint(self):
        with self.assertRaisesRegex(ValueError,"'price' must be greater than zero"):
            Trade(trade_id=self.valid_trade_id,
                      leg_id=self.valid_leg_id,
                      timestamp=self.valid_timetamp,
                      symbol=self.valid_symbol,
                      quantity=self.valid_quantity,
                      price=0.0,
                      cost=self.valid_cost,
                      action=self.valid_action,
                      fees=self.valid_fees)


#      Basic Construction: You've tested that a Position object can be instantiated with valid parameters.
# Equality and Inequality: Through various scenarios, you've checked that the __eq__ method correctly identifies when two Position objects should be considered equal or not.
# Type and Constraint Validations: You've tested that your class raises appropriate errors when initialized with incorrect types or values that violate defined constraints.
# Given this comprehensive coverage, here are some potential edge cases and additional tests you might consider:

# Floating-Point Precision: Test cases where floating-point arithmetic might lead to precision issues in comparisons, especially for avg_cost, initial_margin, total_cost, and market_value.

# Extreme Values: Test with boundary values for each attribute, such as the maximum and minimum possible integers and floating-point numbers, to ensure your class handles them gracefully.

# Optional Attributes: Explicitly test cases where optional attributes (multiplier, initial_margin, total_cost, market_value) are None to ensure your class behaves correctly in their absence, especially in the __eq__ method.

# Mixed Types in Comparison: For attributes that accept multiple types (int or float), test comparisons where one Position object has an attribute as int and another as float with the same logical value (e.g., avg_cost=10 vs. avg_cost=10.0) to ensure equality checks work as expected.

# Negative Quantities: Although not explicitly mentioned, if your domain logic allows, testing with negative quantities could be interesting, depending on whether such scenarios are valid in your application's context.

# Comprehensive Equality Check: Ensure that all attributes are included in the __eq__ method's comparison logic. Your current implementation omits market_value from the comparison. If this omission was unintentional, adding it would be necessary to fully validate object equality.

# Serialization/Deserialization: If your Position objects are ever serialized to a string format (e.g., JSON) and deserialized back, tests to ensure that the object remains consistent through these processes could be beneficial.

# Immutability Checks: Since you're using dataclasses, consider testing for immutability if your Position objects are not meant to be changed after creation. This would involve attempts to modify attributes after object creation and ensuring that either it's not possible or does not affect equality comparisons inappropriately.   

if __name__ =="__main__":
    unittest.main()



