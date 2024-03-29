import os
import logging
import threading
from decimal import Decimal
from datetime import datetime
from ibapi.order import Order
from ibapi.client import EClient
from typing import get_type_hints
from ibapi.wrapper import EWrapper
from ibapi.order_state import OrderState
from ibapi.contract import Contract, ContractDetails

from midas.portfolio import PortfolioServer
from midas.performance import PerformanceManager
from midas.account_data import ActiveOrder, Position, Trade
from midas.account_data import Position,ActiveOrder, AccountDetails, EquityDetails

class BrokerApp(EWrapper, EClient):
    def __init__(self, logger:logging.Logger, portfolio_server: PortfolioServer, performance_manager: PerformanceManager):
        EClient.__init__(self, self)
        self.logger = logger
        self.portfolio_server = portfolio_server
        self.symbols_map = portfolio_server.symbols_map
        self.performance_manager = performance_manager

        #  Data Storage
        self.next_valid_order_id = None
        self.is_valid_contract = None
        self.account_info : AccountDetails = {} 
        self.account_info_keys = get_type_hints(AccountDetails)
        # self.executed_orders = {} 

        # Event Handling
        self.connected_event = threading.Event()
        self.valid_id_event = threading.Event()
        self.validate_contract_event = threading.Event()
        self.account_download_event = threading.Event()
        self.open_orders_event = threading.Event()

        # Thread Locks
        self.next_valid_order_id_lock = threading.Lock()

    def error(self, reqId:int, errorCode:int, errorString:str, advancedOrderRejectJson:str=None):
        super().error(reqId, errorCode, errorString)
        if errorCode == 502: # Error for wrong port
            self.logger.critical(f"Port Error : {errorCode} incorrect port entered.")
            os._exit(0)
        elif errorCode == 200: # Error for contract not found
            self.logger.critical(f"{errorCode} : {errorString}")
            self.is_valid_contract = False
            self.validate_contract_event.set()

    #### wrapper function to signifying completion of successful connection.      
    def connectAck(self):
        super().connectAck()
        self.logger.info('Established Broker Connection')
        self.connected_event.set()

    #### wrapper function for disconnect() -> Signals disconnection.
    def connectionClosed(self):
        super().connectionClosed()
        self.logger.info('Closed Broker Connection.')

    #### wrapper function for reqIds() -> This function manages the Order ID.
    def nextValidId(self, orderId:int):
        super().nextValidId(orderId)
        with self.next_valid_order_id_lock:
            self.next_valid_order_id = orderId
        
        self.logger.info(f"Next Valid Id {self.next_valid_order_id}")
        self.valid_id_event.set()

    def contractDetails(self, reqId:int, contractDetails: ContractDetails):
        self.is_valid_contract = True

    def contractDetailsEnd(self, reqId:int):
        self.logger.info(f"Contract Details Received.")
        self.validate_contract_event.set()
    
    #### wrapper function for reqAccountUpdates. returns accoutninformation whenever there is a change
    def updateAccountValue(self, key:str, val:str, currency:str, accountName:str):
        super().updateAccountValue(key, val, currency, accountName)
        if key in self.account_info_keys:
            if key == 'Currency':
                self.account_info[key] = val
            else:
                self.account_info[key] = float(val)

    #### wrapper function for reqAccountUpdates. Get position information
    def updatePortfolio(self, contract:Contract, position: Decimal, marketPrice: float, marketValue:float, averageCost:float, unrealizedPNL:float, realizedPNL:float, accountName:str):
        super().updatePortfolio(contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName)
        if position == 0:
            pass
        else:
            position_data = Position(
                action="BUY" if position > 0 else "SELL",
                avg_cost = averageCost,
                quantity= float(position),
                total_cost= abs(float(position)) * averageCost if contract.secType =='FUT' else float(position) * averageCost,
                market_value=marketValue, 
                multiplier=self.symbols_map[contract.symbol].multiplier,
                initial_margin=self.symbols_map[contract.symbol].initialMargin
            )
    
            self.portfolio_server.update_positions(contract, position_data)

    #### wrapper function for reqAccountUpdates. Signals the end of account information
    def accountDownloadEnd(self, accountName:str):
        super().accountDownloadEnd(accountName)

        # Set timestamp for account update
        self.account_info['Timestamp'] = current_time_iso = datetime.now().isoformat()
        self.portfolio_server.update_account_details(self.account_info)

        self.logger.info(f"AccountDownloadEnd. Account: {accountName}")
        self.account_download_event.set()

    def openOrder(self, orderId: int, contract: Contract, order: Order, orderState: OrderState):
        super().openOrder(orderId, contract, order, orderState)

        order_data = ActiveOrder(
            permId= order.permId,
            clientId= order.clientId, 
            orderId= orderId, 
            account= order.account, 
            symbol= contract.symbol, 
            secType= contract.secType,
            exchange= contract.exchange, 
            action= order.action, 
            orderType= order.orderType,
            totalQty= float(order.totalQuantity), # Decimal
            cashQty= order.cashQty, 
            lmtPrice= order.lmtPrice, 
            auxPrice= order.auxPrice, 
            status= orderState.status
        )
        self.portfolio_server.update_orders(order_data)

    # Wrapper function for openOrderEnd
    def openOrderEnd(self):
        self.logger.info(f"Initial Open Orders Received.")
        self.open_orders_event.set()

    # Wrapper function for orderStatus
    def orderStatus(self, orderId:int, status:str, filled:Decimal, remaining:Decimal, avgFillPrice:float, permId:int, parentId:int, lastFillPrice:float, clientId:int, whyHeld:str, mktCapPrice: float):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        self.logger.info(f"Received order status update for orderId {orderId}: {status}")
        
        order_data = ActiveOrder(
            permId = permId,
            orderId =  orderId,
            status =  status, # Options : PendingSubmit, PendingCancel PreSubmitted, Submitted, Cancelled, Filled, Inactive 
            filled =  float(filled),
            remaining =  float(remaining),
            avgFillPrice =  avgFillPrice, 
            parentId =  parentId,
            lastFillPrice =  lastFillPrice, 
            whyHeld =  whyHeld, 
            mktCapPrice =  mktCapPrice
        )

        self.portfolio_server.update_orders(order_data)
        
    ####   wrapper function for reqExecutions.   this function gives the executed orders                
    # def execDetails(self, reqId, contract, execution):
    #     print(reqId, contract, execution)
    #     super().execDetails(reqId, contract, execution)
    #     execution_data = Trade(permId = execution.permId, 
    #                                 reqId = reqId,
    #                                 Symbol = contract.symbol, 
    #                                 SecType= contract.secType, 
    #                                 Currency= contract.currency, 
    #                                 ExecId= execution.execId, 
    #                                 Time= execution.time, 
    #                                 Account= execution.acctNumber, 
    #                                 Exchange= execution.exchange,
    #                                 Side= execution.side, 
    #                                 Shares= execution.shares, 
    #                                 Price= execution.price,
    #                                 AvPrice= execution.avgPrice,
    #                                 cumQty= execution.cumQty, 
    #                                 OrderRef= execution.orderRef
    #                                 )
    #     self.performance_manager.update_trades(execution_data)
    
    
    

    # self.executed_orders[execution.permId] = {
    #     "reqId" : reqId,
    #     "Symbol":contract.symbol, 
    #     "SecType":contract.secType, 
    #     "Currency":contract.currency, 
    #     "ExecId":execution.execId, 
    #     "Time":execution.time, 
    #     "Account":execution.acctNumber, 
    #     "Exchange":execution.exchange,
    #     "Side":execution.side, 
    #     "Shares":execution.shares, 
    #     "Price":execution.price,
    #     "AvPrice":execution.avgPrice,
    #     "cumQty":execution.cumQty, 
    #     "OrderRef":execution.orderRef
    # }
    
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
    
    
    
    
    
    
    
    
    
    

    