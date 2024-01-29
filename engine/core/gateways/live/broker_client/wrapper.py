
import os
import logging
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from utilities.portfolio_server import PortfolioServer

class BrokerApp(EWrapper, EClient):
    ACCOUNT_INFO_KEYS = {'AccruedCash', 'AvailableFunds', 'BuyingPower', 'CashBalance', 
                    'Currency', 'EquityWithLoanValue', 'ExcessLiquidity', 'FullAvailableFunds', 
                    'FullInitMarginReq', 'FundValue', 'FutureOptionValue', 'FuturesPNL', 
                    'GrossPositionValue', 'InitMarginReq', 'IssuerOptionValue', 
                    'MaintMarginReq', 'NetLiquidation', 'RealizedPnL', 'TotalCashBalance', 
                    'TotalCashValue', 'UnrealizedPnL'}
    
    def __init__(self, portfolio_logger:logging.Logger,portfolio_server: PortfolioServer):
        EClient.__init__(self, self)

        self.portfolio_logger = portfolio_logger

        #  Data Storage
        self.portfolio_server = portfolio_server
        self.next_valid_order_id = None
        self.is_valid_contract = None
        self.account_info = {} # Account Manager
        self.executed_orders = {} # Trades Manager
        # self.positions = {} # Positions Manager
        # self.active_orders = {} # Will really only be utilized by LIVE

        # Event Handling
        self.connected_event = threading.Event()
        self.valid_id_event = threading.Event()
        self.validate_contract_event = threading.Event()
        self.account_download_event = threading.Event()
        self.open_orders_event = threading.Event()

        # Thread Locks
        self.next_valid_order_id_lock = threading.Lock()

    def error(self, reqId, errorCode, errorString):
        super().error(reqId, errorCode, errorString)
        if errorCode == 502: # Error for wrong port
            self.portfolio_logger.critical(f"Port Error : {errorCode} incorrect port entered.")
            os._exit(0)
        elif errorCode == 200: # Error for contract not found
            self.portfolio_logger.critical(f"{errorCode} : {errorString}")
            self.is_valid_contract = False
            self.validate_contract_event.set()

    #### wrapper function to signifying completion of successful connection.      
    def connectAck(self):
        super().connectAck()
        self.portfolio_logger.info('Established Broker Connection')
        self.connected_event.set()

    #### wrapper function for disconnect() -> Signals disconnection.
    def connectionClosed(self):
        super().connectionClosed()
        self.portfolio_logger.info('Closed Broker Connection.')

    #### wrapper function for reqIds() -> This function manages the Order ID.
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        with self.next_valid_order_id_lock:
            self.next_valid_order_id = orderId
        
        self.portfolio_logger.info(f"Next Valid Id {self.next_valid_order_id}")
        self.valid_id_event.set()

    def contractDetails(self, reqId, contractDetails):
        self.is_valid_contract = True

    def contractDetailsEnd(self, reqId):
        self.portfolio_logger.info(f"Contract Details Received.")
        self.validate_contract_event.set()
    
    #### wrapper function for reqAccountUpdates. returns accoutninformation whenever there is a change
    def updateAccountValue(self, key:str, val:str, currency:str,accountName:str):
        super().updateAccountValue(key, val, currency, accountName)
        if key in self.ACCOUNT_INFO_KEYS:
            self.account_info[key] = val

    #### wrapper function for reqAccountUpdates. Get position information
    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName):
        super().updatePortfolio(contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName)
        
        position_data = {
            "direction": "BUY" if position > 0 else "SELL", 
            "quantity": position,
            "avg_cost": averageCost, 
            "total_cost": position * averageCost*-1,
            "market_value": marketValue, 
        }
 
        self.portfolio_server.update_positions(contract, position_data)

    #### wrapper function for reqAccountUpdates. Signals the end of account information
    def accountDownloadEnd(self, accountName):
        super().accountDownloadEnd(accountName)
        self.portfolio_server.update_account(self.account_info)
        self.portfolio_logger.info(f"AccountDownloadEnd. Account: {accountName}")
        self.account_download_event.set()

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        data = {
            "permId" : order.permId,
            "clientId": order.clientId, 
            "orderId": orderId, 
            "account": order.account, 
            "symbol": contract.symbol, 
            "secType": contract.secType,
            "exchange": contract.exchange, 
            "action": order.action, 
            "orderType": order.orderType,
            "totalQty": order.totalQuantity, 
            "cashQty": order.cashQty, 
            "lmtPrice": order.lmtPrice, 
            "auxPrice": order.auxPrice, 
            "status": orderState.status
        }
        self.portfolio_server.update_orders(**data)

    # Wrapper function for openOrderEnd
    def openOrderEnd(self):
        self.portfolio_logger.info(f"Initial Open Orders Received.")
        self.open_orders_event.set()

    # Wrapper function for orderStatus
    def orderStatus(self, orderId:int, status:str, filled:float, remaining:float, avgFillPrice:float, permId:int, parentId:int, lastFillPrice:float, clientId:int, whyHeld:str, mktCapPrice: float):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        self.portfolio_logger.info(f"Received order status update for orderId {orderId}: {status}")

        data = {
            "permId" : permId,
            "orderId": orderId,
            "status": status, 
            "filled": filled,
            "remaining": remaining,
            "avgFillPrice": avgFillPrice, 
            "parentId": parentId, 
            "lastFillPrice": lastFillPrice, 
            "whyHeld": whyHeld, 
            "mktCapPrice": mktCapPrice
        }
        self.portfolio_server.update_orders(**data)
        
    #####   wrapper function for reqExecutions.   this function gives the executed orders                
    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)

        self.executed_orders[execution.permId] = {
            "reqId" : reqId,
            "Symbol":contract.symbol, 
            "SecType":contract.secType, 
            "Currency":contract.currency, 
            "ExecId":execution.execId, 
            "Time":execution.time, 
            "Account":execution.acctNumber, 
            "Exchange":execution.exchange,
            "Side":execution.side, 
            "Shares":execution.shares, 
            "Price":execution.price,
            "AvPrice":execution.avgPrice,
            "cumQty":execution.cumQty, 
            "OrderRef":execution.orderRef
        }
        
    
    
    
    
    # def _update_active_orders(self, data):
    #     # If the status is 'Cancelled' and the order is present in the dict, remove it
    #     if data['status'] == 'Cancelled' or data['status'] == 'Filled' and data['permId'] in self.active_orders:
    #         del self.active_orders[data['permId']]
    #     # If not cancelled, either update the existing order or add a new one
    #     elif data['status'] != 'Cancelled' and data['status'] != 'Filled':
    #         if data['permId'] not in self.active_orders:
    #             self.active_orders[data['permId']] = data
    #         else:
    #             self.active_orders[data['permId']].update(data)
    
    
    
    
    
    
    
    
    
    

    