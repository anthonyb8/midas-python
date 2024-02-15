import os
import logging
import pandas as pd
import numpy as np
from ibapi.order import Order
from ibapi.contract import Contract
from typing import Tuple, List, Dict, Any

from midas.events import TradeInstruction, Action
from midas.portfolio import Position
from midas.strategies import BaseStrategy
from midas.symbols import Symbol


from .performance import BacktestPerformance
from .report import HTMLReportGenerator

class Backtest(BacktestPerformance):
    def __init__(self, strategy: BaseStrategy, symbols_map: Dict[str, Symbol], full_data: pd.DataFrame, trade_allocation: int=0.20, initial_capital: int = 10000, logger:logging.Logger = None, report_generator: HTMLReportGenerator=None) -> None:
        self.full_data = full_data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.trade_allocation = trade_allocation
        self.symbols_map = symbols_map
        self.logger = logger
        self.report_generator = report_generator
        
    def output_summary(self, title: str, summary_dict: Dict[str, Any]) -> None:
        # Add title and summary items to the report using the report generator
        self.report_generator.add_section_title(title)
        self.report_generator.add_summary(summary_dict)

        # Log the information if a logger is available
        if self.logger:
            self.logger.info(f"\n{title}:\n" + "=" * len(title))
            for key, value in summary_dict.items():
                self.logger.info(f"{key}: {value}")
            self.logger.info("\n")

    def output_sensitivity_results(self, results: Dict) -> None:
        # Add section title for Sensitivity Results
        self.report_generator.add_section_title("Sensitivity Results")

        # Prepare table headers and rows
        headers = ["Entry Threshold", "Exit Threshold", "Total Return(%)", "Sharpe Ratio", "Max Drawdown(%)"]
        rows = []
  
        for thresholds, metrics in results.items():
            rows.append([
                thresholds[0], thresholds[1], 
                f"{metrics['Total Return(%)']:.2f}%", 
                f"{metrics['Sharpe Ratio']:.2f}", 
                f"{metrics['Max Drawdown(%)']:.2f}%"
            ])

        # Add the table to the HTML report
        self.report_generator.add_table(headers, rows)

        # # Optionally, log the information
        # if self.logger:
        #     header = "\nEntry Threshold, Exit Threshold | Total Return(%) | Sharpe Ratio | Max Drawdown(%)"
        #     self.logger.info(header)
        #     self.logger.info("=" * len(header))
        #     for thresholds, metrics in results.items():
        #         row = f"{thresholds[0]}, {thresholds[1]} | {metrics['Total Return(%)']:.2f}% | {metrics['Sharpe Ratio']:.2f} | {metrics['Max Drawdown(%)']:.2f}%"
        #         self.logger.info(row)

    def split_data(self,data: pd.DataFrame, train_ratio: float = 0.8) -> Tuple[pd.DataFrame, pd.DataFrame]:
        train_size = int(len(data) * train_ratio)
        return data.iloc[:train_size], data.iloc[train_size:]
    
    def calculate_metrics(self, equity_curve, return_plots=False):
        cum_return_curve = BacktestPerformance.cumulative_return(equity_curve)
        drawdown_curve = BacktestPerformance.drawdown(equity_curve)

        if return_plots:
            # Generate and add plots to the HTML report using report_generator
            self.report_generator.add_image(self.plot_equity_curve, equity_curve, show_plot=False)
            self.report_generator.add_image(self.plot_return_curve, cum_return_curve, show_plot=False)
            self.report_generator.add_image(self.plot_drawdown_curve, drawdown_curve, show_plot=False)
        else:
            # Display plots as usual
            self.plot_equity_curve(equity_curve)
            self.plot_return_curve(cum_return_curve)
            self.plot_drawdown_curve(drawdown_curve)

        # Calculate Sharpe ratio, Max drawdown, and Total return
        sharpe_ratio = BacktestPerformance.sharpe_ratio(equity_curve)
        max_drawdown = min(drawdown_curve)
        total_return = cum_return_curve[-1]

        metrics = {'Total Return(%)': total_return, 'Sharpe Ratio': sharpe_ratio, 'Max Drawdown(%)': max_drawdown}
        
        # Add metrics to the HTML report
        self.report_generator.add_section_title("Performance Metrics")
        self.report_generator.add_summary(metrics)

        return metrics
    
    def walk_forward_analysis(self, total_segments: int, entry_thresholds: List[float], exit_thresholds: List[float]) -> None:
        segment_size = len(self.full_data) // total_segments

        for i in range(1, total_segments + 1):
            current_window_data = self.full_data.iloc[:segment_size * i]
            train_data, test_data = self.split_data(current_window_data)
            print(len(train_data),len(test_data))
            segment_summary = {
                'Segment': i,
                'Initial Capital': self.initial_capital,
                'Training Data Range': f"{train_data.index[0]} to {train_data.index[-1]}",
                'Testing Data Range': f"{test_data.index[0]} to {test_data.index[-1]}"
            }
            self.output_summary("Parameter Summary", segment_summary)

            # # Reset the strategy before sensitivity analysis
            # self.strategy.reset()

            # Prepare the strategy with training data
            self.strategy.prepare(train_data)

            # # Validate
            # self.strategy.data_validation(self.report_generator)

            performance_metrics = self.sensitivity_analysis(current_window_data, test_data, entry_thresholds, exit_thresholds)

            self.output_sensitivity_results(performance_metrics)
    
    def sensitivity_analysis(self, current_window: pd.DataFrame, test_data: pd.DataFrame, entry_thresholds: List[float], exit_thresholds: List[float]) -> Dict:
        results = {}

        for entry_threshold in entry_thresholds:
            for exit_threshold in exit_thresholds:
                self.strategy.reset()  
                sensitivity_params = {
                    'Entry Threshold': entry_threshold,
                    'Exit Threshold': exit_threshold
                }
                self.output_summary("Sensitivity Analysis Parameters", sensitivity_params)

                equity_curve, signals = self.run_backtest(test_data, entry_threshold, exit_threshold)

                oldest_timestamp = test_data.index.min()
                # self.plot_price_and_spread(current_window, self.strategy.historical_zscore,signals, oldest_timestamp, show_plot=True)
                # print(len(current_window), len(self.strategy.historical_zscore))
                self.report_generator.add_image(self.plot_price_and_spread,current_window, self.strategy.historical_zscore,signals, oldest_timestamp, show_plot=False)
                results[(entry_threshold, exit_threshold)] = self.calculate_metrics(equity_curve, return_plots=True)

        return results
    
    def run_backtest(self, data: pd.DataFrame, entry_threshold: float, exit_threshold: float) -> Tuple[List[float], List[Dict]]:
        pass

class FuturesBacktest(Backtest):  
    def __init__(self,  strategy: BaseStrategy, symbols_map: Dict[str, Symbol], full_data: pd.DataFrame, trade_allocation=0.20, initial_capital=10000, slippage_factor:int=1,logger:logging.Logger = None,report_generator: HTMLReportGenerator=None):
        super().__init__(strategy, symbols_map, full_data, trade_allocation, initial_capital, logger, report_generator)
        self.initial_capital = initial_capital  
        self.slippage_factor = slippage_factor # multiplied by tick size, so slippage will be x ticks against the position   

    def run_backtest(self, data: pd.DataFrame, entry_threshold: float, exit_threshold: float) -> Tuple[List[float], List[Dict]]:
        self.signals = []
        self.positions = {}
        self.trades = []
        self.equity_curve = [self.initial_capital]
        self.account = {"AvailableFunds": self.initial_capital, "RequiredMargin": 0, "CurrentMargin": 0, "UnrealizedPnl": 0}  


        for i, row in data.iterrows():
            trade_instructions = self.strategy.handle_market_data(row, self.positions, entry_threshold, exit_threshold)
            timestamp = row.name
            position_allocation = self.trade_allocation * self.account['AvailableFunds'] # capital available for the next trade

            if trade_instructions != None:
                trades = self.execute_trade(timestamp, trade_instructions, row, position_allocation)
                if trades != None:
                    # Update Trades
                    self.trades.append(trades)
                    
                    # Update Account
                    self.update_account(trades)
                    account_details = "\n ".join([f"{key}: {value}" for key, value in self.account.items()])
                    self.logger.info(f"{timestamp} - \nAccount Details:\n {account_details}")
                    
                    # Update Positions
                    self.update_positions(trades)
                    positions_details = "\n ".join([f"{position}: {{'action': {details['action']}, 'quantity': {details['quantity']}, 'avg_cost': {details['avg_cost']}, 'contract_size': {details['contract_size']}, 'initial_margin': {details['initial_margin']}}}"
                                                    for position, details in self.positions.items()
                                                    ])
                    self.logger.info(f"{timestamp} -\nPositions:\n {positions_details}")

                
            # Update equity curve
            self.mark_to_market(row) # mark-to-market
            self.check_margin_call()
            self.equity_curve.append(round(self.account['AvailableFunds'] +  self.calculate_portfolio_value(row), 2))
            self.logger.info(f"{timestamp} - Equity Value : {self.equity_curve[-1]}")
            account_details = "\n ".join([f"{key}: {value}" for key, value in self.account.items()])
            self.logger.info(f"{timestamp} - \nAccount Details:\n {account_details}")   

        return self.equity_curve, self.signals
    
    def execute_trade(self, timestamp, trade_instructions:TradeInstruction, market_data, position_allocation):
        trades = []
        total_margin = 0

        for trade in trade_instructions:
            ticker = trade.ticker
            action = trade.action
            weight = trade.weight
            current_price = market_data[ticker]
            contract_size = self.symbols_map[ticker].contractSize

            # Record signal
            self.signals.append({
                "timestamp": timestamp,
                "ticker": ticker,
                "action": action.name,
                "weight": weight,
                "price": current_price, 
            })

            original_allocation = position_allocation * abs(weight)  # Assuming weight can be negative

            # Adjust price for slippage
            tick_size = self.symbols_map[ticker].tickSize
            adjusted_price = self.calculate_slippage_price(tick_size, current_price, action)

            # Calculate potential quantity (without commission and slippage)
            potential_quantity = original_allocation / (adjusted_price * contract_size)

            # Calculate commission fees (based on potential quantity)
            commission_fees = self.calculate_commission_fees(ticker, potential_quantity)

            # Final allocation considers commission fees but not slippage directly (since price was adjusted)
            trade_allocation = original_allocation - commission_fees

            # Adjust quantity based on the trade allocation
            if action in [Action.LONG, Action.SHORT]:  # Entry signal
                quantity = trade_allocation / (current_price * contract_size)
                if action == Action.LONG:
                    quantity_factor = 1
                elif action == Action.SHORT:
                    quantity_factor = -1
            elif action in [Action.SELL, Action.COVER]:  # Exit signal
                # print(self.positions[ticker])
                quantity = self.positions[ticker]['quantity']
                quantity_factor = -1

        
            quantity = quantity * quantity_factor

            margin = abs(quantity) * self.symbols_map[ticker].initialMargin
            total_margin += abs(margin)

            trades.append({
                'ticker': ticker,
                'action': action,
                'quantity': quantity,
                'avg_cost': adjusted_price,
                'contract_size': contract_size,
                'initial_margin': self.symbols_map[ticker].initialMargin, 
                'original_allocation': original_allocation,
                'trade_allocation': trade_allocation,
                'commission_fees': commission_fees,
            })

        # Check if total margin requirement is met
        if (total_margin + self.account['RequiredMargin']) <= (self.account['AvailableFunds'] + self.account['CurrentMargin']):
            return trades
        else:
            return None

    def calculate_slippage_price(self, tick_size: float, current_price: float, action: Action):
        slippage = tick_size * self.slippage_factor

        if action in [Action.LONG, Action.COVER]:  # Entry signal for a long position or covering a short
            adjusted_price = current_price + slippage
        elif action in [Action.SHORT, Action.SELL]:  # Entry signal for a short position or selling a long
            adjusted_price = current_price - slippage
        else:
            raise ValueError(f"{action} not in ['LONG','COVER', 'SHORT', 'SELL']")
        
        return adjusted_price

    def calculate_commission_fees(self,ticker: str,quantity:float):
        return quantity * self.symbols_map[ticker].fees
    
    def update_account(self, trades):
        for trade in trades:
            self.account['AvailableFunds'] -= trade['commission_fees']
            margin_impact = trade['initial_margin'] * abs(trade['quantity'])

            if trade['action'] in [Action.LONG, Action.SHORT]:
                self.account['RequiredMargin']  += margin_impact
                self.account['AvailableFunds']  -= margin_impact
                self.account['CurrentMargin']  += margin_impact
            elif trade['action'] in [Action.SELL, Action.COVER]:
                entry_price = self.positions[trade['ticker']]['avg_cost'] 
                exit_price = trade['avg_cost']
                pnl = (exit_price - entry_price) * trade['quantity'] * trade['contract_size']
                
                self.account['AvailableFunds']  += pnl + margin_impact
                self.account['CurrentMargin'] -= pnl + margin_impact
                self.account['RequiredMargin'] -= margin_impact  # remove the margin  required as postion is exited
    
    def update_positions(self, trades):
        for trade in trades:
            ticker = trade['ticker']
            contract_size = trade['contract_size']
            avg_cost = trade['avg_cost']
            quantity = trade['quantity']
            action = trade['action'].to_broker_standard() # Buy or sell
            print(ticker,trade['action'],action, quantity)
            

             # If no position then postions is equal to new order attributes
            if ticker not in self.positions.keys():
                self.positions[ticker] = {
                    'action': action,
                    'quantity': quantity,
                    'avg_cost': round(avg_cost,4),
                    'contract_size': contract_size,      
                    'initial_margin': self.symbols_map[ticker].initialMargin
                    # 'total_cost': round(quantity * avg_cost * -1,4) # Cost (-) if a buy, (+) if a sell    
                }

            else:
                current_position = self.positions[ticker]
                existing_value = current_position['avg_cost'] * current_position['quantity'] * current_position['contract_size']
                added_value = avg_cost * quantity * contract_size
                net_quantity = current_position['quantity'] + quantity
                print(current_position['quantity'],  quantity)

                # If nets the old position ot 0 the position no longer exists
                if net_quantity == 0:
                    del self.positions[ticker]
                    return

                net_cost = existing_value + added_value

                # Adding to the old position
                if action == current_position['action']:
                    self.positions[ticker]['quantity'] = net_quantity
                    self.positions[ticker]['avg_cost'] = (existing_value + added_value) / (net_quantity * contract_size)
                    # self.positions[contract]['total_cost'] = net_cost

                # If order less than current position quantity
                elif action != current_position['action'] and abs(quantity) < abs(current_position['quantity']):
                    self.positions[ticker]['quantity'] = net_quantity
                    self.positions[ticker]['total_cost'] = net_quantity * self.positions[ticker]['avg_cost']
                
                # If order great than current position quantity
                elif action != current_position['action'] and abs(quantity) > abs(current_position['quantity']):
                    # avg_cost = self.fill_price(contract,order.action)
                    # quantity = self.check_action(order.action,order.totalquantity)
                    self.positions[ticker]['action'] = 'BUY' if net_quantity > 0 else 'SELL'
                    self.positions[ticker]['quantity'] = net_quantity
                    self.positions[ticker]['avg_cost'] = avg_cost
                    self.positions[ticker]['total_cost'] = quantity * avg_cost
                else: 
                    raise ValueError(f"{action} not BUY or SELL")
    
    def calculate_portfolio_value(self, market_data):
        portfolio_value = 0

        for ticker, position in self.positions.items():
            current_price = market_data[ticker]
            portfolio_value += self.position_value(position, current_price)

        return portfolio_value
    
    def position_value(self, position, current_price):
        initial_margin = position['initial_margin'] * abs(position['quantity'])
        entry_price = position['avg_cost'] # This needs to be correctly sourced]
        pnl = (current_price - entry_price) * position['quantity'] * position['contract_size']
        return pnl + initial_margin

    def mark_to_market(self, market_data):
        pnl = 0

        for ticker, position in self.positions.items():
            current_price = market_data[ticker]
            entry_price = position['avg_cost'] # This needs to be correctly sourced]
            pnl += (current_price - entry_price) * position['quantity'] * position['contract_size']
        self.account['UnrealizedPnl'] = pnl
        self.account['CurrentMargin'] = self.account['RequiredMargin'] + pnl

    def check_margin_call(self):
        # Assuming 'margin_balance' needs to be greater than a certain percentage of 'portfolio_value' to avoid a margin call
        if self.account['AvailableFunds'] + self.account['CurrentMargin'] < self.account['RequiredMargin']:
            # Logic to handle margin call, e.g., liquidate positions to meet margin requirements
            self.logger.info("Margin call triggered.")
            return True
        return False

class EquityBacktest(Backtest):
    def __init__(self, strategy, symbols_map, full_data, trade_allocation=0.20, initial_capital=10000):
        super().__init__(strategy, symbols_map, full_data, trade_allocation, initial_capital)
    
    def execute_trade(self, trade_instruction, market_data, positions, position_allocation, capital):
        executed_trades = []
        
        symbol = trade_instruction.contract.symbol
        current_price = market_data[symbol]
        action = trade_instruction.action
        weight = trade_instruction.allocation_percent

        if action in ['LONG', 'SHORT']:  # Entry signal
            trade_value = position_allocation * weight
            quantity = trade_value / current_price
        elif action in ['SELL','COVER']:  # Exit signal
            quantity = positions[symbol]['quantity'] * -1

        trade_details = {
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'avg_price': current_price,
        }

        return self.update_positions(trade_details, positions, capital)
    
    def update_positions(self, trade_confirmation, positions, capital):
        symbol = trade_confirmation['symbol']
        avg_price = trade_confirmation['avg_price']
        quantity = trade_confirmation['quantity']
        position_type = trade_confirmation['type']

        if symbol in positions:
            position_info = positions[symbol]
            if trade_confirmation['action'] == position_info['action']:
                # Update existing position
                position_info['quantity'] += quantity
                current_value = position_info['avg_price'] * position_info['quantity']
                added_value = avg_price * quantity 
                position_info['avg_price'] = (current_value + added_value) / position_info['quantity']
                capital -= added_value 
            else:
                # Exit or reverse position
                capital_change = avg_price * position_info['quantity']
                capital += capital_change
                del positions[symbol]
        else:
            # Enter new position
            positions[symbol] = {
                'action': trade_confirmation['action'],
                'quantity': quantity,
                'avg_price': avg_price,
            }
            capital_change = avg_price * quantity
            capital -= capital_change

        return capital

    def calculate_portfolio_value(self, market_data, positions):
        portfolio_value = 0

        for symbol, position in positions.items():
            current_price = market_data[symbol]
            position_value = current_price * position['quantity']
            portfolio_value += position_value

        return portfolio_value

