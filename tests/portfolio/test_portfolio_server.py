import unittest
from ibapi.order import Order
from ibapi.contract import Contract
from unittest.mock import patch, Mock

from midas.events import Action
from midas.portfolio import PortfolioServer
from midas.account_data import Position, AccountDetails, ActiveOrder
from midas.symbols.symbols import Future, Equity, Currency, Exchange

#TODO: edge cases, integration

class TestPortfolioServer(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_symbols_map = {'HEJ4' : Future(ticker='HEJ4',
                                                  currency=Currency.USD,
                                                  exchange=Exchange.CME,
                                                  fees=0.1,
                                                  lastTradeDateOrContractMonth='202412',
                                                  multiplier=400,
                                                  tickSize=0.0025,
                                                  initialMargin=4000),
                                    'AAPL' : Equity(ticker="APPL", 
                                                currency=Currency.CAD , 
                                                exchange=Exchange.NYSE, 
                                                fees= 0.10)}
        self.mock_logger= Mock() 
        self.portfolio_server = PortfolioServer(symbols_map=self.valid_symbols_map, logger=self.mock_logger)
    
    # Basic Validation
    def test_update_positions_new_valid(self):
        contract = Contract()
        contract.symbol = 'AAPL'
        position = Position(action='BUY', 
                            avg_cost=10.9,
                            quantity=100,
                            total_cost=100000,
                            market_value=10000,
                            multiplier=1,
                            initial_margin=0)
        
        # Test
        self.portfolio_server.update_positions(contract, position)

        # Validation
        self.assertEqual(self.portfolio_server.positions[contract.symbol], position)
        self.mock_logger.info.assert_called_once()

    def test_update_positions_old_valid(self):
        contract = Contract()
        contract.symbol = 'AAPL'
        position = Position(action='BUY', 
                            avg_cost=10.9,
                            quantity=100,
                            total_cost=100000,
                            market_value=10000,
                            multiplier=1,
                            initial_margin=0)
        
        self.portfolio_server.positions[contract.symbol] = position
        
        # Test
        response = self.portfolio_server.update_positions(contract, position)

        # Validation
        self.assertEqual(response, None)
        self.assertEqual(self.portfolio_server.positions[contract.symbol], position)
        self.assertEqual(len(self.portfolio_server.positions), 1)
        self.assertFalse(self.mock_logger.info.called)

    def test_output_positions(self):
        contract = Contract()
        contract.symbol = 'AAPL'
        position = Position(action='BUY', 
                    avg_cost=10.9,
                    quantity=100,
                    total_cost=100000,
                    market_value=10000,
                    multiplier=1,
                    initial_margin=0)
        
        # Test
        self.portfolio_server.update_positions(contract, position)

        # Validation
        self.mock_logger.info.assert_called_once_with("\nPositions Updated: \n AAPL: {'action': 'BUY', 'avg_cost': 10.9, 'quantity': 100, 'total_cost': 100000, 'market_value': 10000, 'multiplier': 1, 'initial_margin': 0} \n")

    def test_update_account_details_valid(self):
        account_info = AccountDetails(FullAvailableFunds = 100000.0, 
                                        FullInitMarginReq =  100000.0,
                                        NetLiquidation = 100000.0,
                                        UnrealizedPnL =  100000.0,
                                        FullMaintMarginReq =  100000.0,
                                        Currency = 'USD') 
        
        # Test
        self.portfolio_server.update_account_details(account_info)

        # Validation
        self.assertEqual(self.portfolio_server.account, account_info)
        self.assertEqual(self.portfolio_server.capital, account_info['FullAvailableFunds'])
        self.mock_logger.info.assert_called_once()
    
    def test_output_account(self):
        account_info = AccountDetails(FullAvailableFunds = 100000.0, 
                                FullInitMarginReq =  100000.0,
                                NetLiquidation = 100000.0,
                                UnrealizedPnL =  100000.0,
                                FullMaintMarginReq =  100000.0,
                                Currency = 'USD') 
        # Test
        self.portfolio_server.update_account_details(account_info)

        # Validation
        self.mock_logger.info.assert_called_once_with('\nAccount Updated: \n FullAvailableFunds : 100000.0 \n FullInitMarginReq : 100000.0 \n NetLiquidation : 100000.0 \n UnrealizedPnL : 100000.0 \n FullMaintMarginReq : 100000.0 \n Currency : USD \n')
        
    def test_update_orders_new_valid(self):
        order_id = 10
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'NASDAQ'

        order = Order()
        order.permId = 10
        order.clientId = 1
        order.account = 'account_name'
        order.action = 'BUY'
        order.orderType = 'MKT'
        order.totalQuantity = 100
        order.cashQty = 100909
        order.lmtPrice = 0
        order.auxPrice = 0

        order_state = Mock()
        order_state.status = 'PreSubmitted'

        active_order = ActiveOrder(permId = order.permId,
                                    clientId= order.clientId, 
                                    orderId= order_id, 
                                    account= order.account, 
                                    symbol= contract.symbol, 
                                    secType= contract.secType,
                                    exchange= contract.exchange, 
                                    action= order.action, 
                                    orderType= order.orderType,
                                    totalQty= order.totalQuantity, 
                                    cashQty= order.cashQty, 
                                    lmtPrice= order.lmtPrice, 
                                    auxPrice= order.auxPrice, 
                                    status= order_state.status)
        
        # Test
        self.portfolio_server.update_orders(active_order)

        # Validation
        self.assertEqual(self.portfolio_server.active_orders[order.permId], active_order)
        self.mock_logger.info.assert_called_once()

    def test_update_orders_update_valid(self):
        order_id = 10
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'NASDAQ'

        order = Order()
        order.permId = 10
        order.clientId = 1
        order.account = 'account_name'
        order.action = 'BUY'
        order.orderType = 'MKT'
        order.totalQuantity = 100
        order.cashQty = 100909
        order.lmtPrice = 0
        order.auxPrice = 0

        order_state = Mock()
        order_state.status = 'PreSubmitted'

        active_order = ActiveOrder(permId = order.permId,
                                    clientId= order.clientId, 
                                    orderId= order_id, 
                                    account= order.account, 
                                    symbol= contract.symbol, 
                                    secType= contract.secType,
                                    exchange= contract.exchange, 
                                    action= order.action, 
                                    orderType= order.orderType,
                                    totalQty= order.totalQuantity, 
                                    cashQty= order.cashQty, 
                                    lmtPrice= order.lmtPrice, 
                                    auxPrice= order.auxPrice, 
                                    status= order_state.status)
        
        self.portfolio_server.active_orders[order.permId] = active_order
        active_order['status'] = 'Submitted'

        # Test
        self.portfolio_server.update_orders(active_order)

        # Validation
        self.assertEqual(self.portfolio_server.active_orders[order.permId], active_order)
        self.assertEqual(len(self.portfolio_server.active_orders), 1)
        self.assertEqual(self.portfolio_server.active_orders[order.permId]['status'], 'Submitted')

        self.mock_logger.info.assert_called_once()

    def test_update_orders_filled_valid(self):
        order_id = 10
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'NASDAQ'

        order = Order()
        order.permId = 10
        order.clientId = 1
        order.account = 'account_name'
        order.action = 'BUY'
        order.orderType = 'MKT'
        order.totalQuantity = 100
        order.cashQty = 100909
        order.lmtPrice = 0
        order.auxPrice = 0

        order_state = Mock()
        order_state.status = 'PreSubmitted'

        active_order = ActiveOrder(permId = order.permId,
                                    clientId= order.clientId, 
                                    orderId= order_id, 
                                    account= order.account, 
                                    symbol= contract.symbol, 
                                    secType= contract.secType,
                                    exchange= contract.exchange, 
                                    action= order.action, 
                                    orderType= order.orderType,
                                    totalQty= order.totalQuantity, 
                                    cashQty= order.cashQty, 
                                    lmtPrice= order.lmtPrice, 
                                    auxPrice= order.auxPrice, 
                                    status= order_state.status)
        
        self.portfolio_server.active_orders[order.permId] = active_order
        self.assertEqual(len(self.portfolio_server.active_orders), 1) # ensure order in portfolio server active orders
        active_order['status'] = 'Filled'

        # Test
        self.portfolio_server.update_orders(active_order)

        # Validation
        self.assertEqual(self.portfolio_server.active_orders, {})
        self.assertEqual(len(self.portfolio_server.active_orders), 0)
        self.mock_logger.info.assert_called_once()

    def test_update_orders_cancelled_valid(self):
        order_id = 10
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'NASDAQ'

        order = Order()
        order.permId = 10
        order.clientId = 1
        order.account = 'account_name'
        order.action = 'BUY'
        order.orderType = 'MKT'
        order.totalQuantity = 100
        order.cashQty = 100909
        order.lmtPrice = 0
        order.auxPrice = 0

        order_state = Mock()
        order_state.status = 'PreSubmitted'

        active_order = ActiveOrder(permId = order.permId,
                                    clientId= order.clientId, 
                                    orderId= order_id, 
                                    account= order.account, 
                                    symbol= contract.symbol, 
                                    secType= contract.secType,
                                    exchange= contract.exchange, 
                                    action= order.action, 
                                    orderType= order.orderType,
                                    totalQty= order.totalQuantity, 
                                    cashQty= order.cashQty, 
                                    lmtPrice= order.lmtPrice, 
                                    auxPrice= order.auxPrice, 
                                    status= order_state.status)
        
        self.portfolio_server.active_orders[order.permId] = active_order
        self.assertEqual(len(self.portfolio_server.active_orders), 1)  # ensure order in portfolio server active orders
        active_order['status'] = 'Cancelled'

        # Tests
        self.portfolio_server.update_orders(active_order)

        # Validation
        self.assertEqual(self.portfolio_server.active_orders, {})
        self.assertEqual(len(self.portfolio_server.active_orders), 0)
        self.mock_logger.info.assert_called_once()

    def test_output_orders(self):
        order_id = 10
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'NASDAQ'

        order = Order()
        order.permId = 10
        order.clientId = 1
        order.account = 'account_name'
        order.action = 'BUY'
        order.orderType = 'MKT'
        order.totalQuantity = 100
        order.cashQty = 100909
        order.lmtPrice = 0
        order.auxPrice = 0

        order_state = Mock()
        order_state.status = 'PreSubmitted'

        active_order = ActiveOrder(permId = order.permId,
                                    clientId= order.clientId, 
                                    orderId= order_id, 
                                    account= order.account, 
                                    symbol= contract.symbol, 
                                    secType= contract.secType,
                                    exchange= contract.exchange, 
                                    action= order.action, 
                                    orderType= order.orderType,
                                    totalQty= order.totalQuantity, 
                                    cashQty= order.cashQty, 
                                    lmtPrice= order.lmtPrice, 
                                    auxPrice= order.auxPrice, 
                                    status= order_state.status)
        
        # Tests
        self.portfolio_server.update_orders(active_order)

        # Validation
        self.mock_logger.info.assert_called_once_with("\nOrder Updated: \n {'permId': 10, 'clientId': 1, 'orderId': 10, 'account': 'account_name', 'symbol': 'AAPL', 'secType': 'STK', 'exchange': 'NASDAQ', 'action': 'BUY', 'orderType': 'MKT', 'totalQty': 100, 'cashQty': 100909, 'lmtPrice': 0, 'auxPrice': 0, 'status': 'PreSubmitted'} \n")
        
if __name__ == "__main__":
    unittest.main()