import pandas as pd
import numpy as np
from engine.core.base.data import Direction, TradeInstruction
from engine.core.strategies import BaseStrategy
from typing import Tuple, List, Dict, Any
from .performance import BacktestPerformance

class Backtest(BacktestPerformance):
    def __init__(self, strategy: BaseStrategy, full_data: pd.DataFrame, trade_allocation: int=0.20, initial_capital: int = 10000) -> None:
        self.full_data = full_data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.trade_allocation = trade_allocation

    def print_summary(self,title: str, summary_dict: Dict[str, Any]) -> None:
        print(f"{title}:\n" + "=" * len(title))
        for key, value in summary_dict.items():
            print(f"{key}: {value}")
        print("\n")

    def split_data(self,data: pd.DataFrame, train_ratio: float = 0.8) -> Tuple[pd.DataFrame, pd.DataFrame]:
        train_size = int(len(data) * train_ratio)
        return data.iloc[:train_size], data.iloc[train_size:]

    def walk_forward_analysis(self, total_segments: int, entry_thresholds: List[float], exit_thresholds: List[float]) -> None:
        segment_size = len(self.full_data) // total_segments

        for i in range(1, total_segments + 1):
            current_window_data = self.full_data.iloc[:segment_size * i]
            train_data, test_data = self.split_data(current_window_data)
            
            segment_summary = {
                'Segment': i,
                'Initial Capital': self.initial_capital,
                'Training Data Range': f"{train_data.index[0]} to {train_data.index[-1]}",
                'Testing Data Range': f"{test_data.index[0]} to {test_data.index[-1]}"
            }
            self.print_summary("Parameter Summary", segment_summary)

            # Reset the strategy before sensitivity analysis
            self.strategy.reset()

            # Prepare the strategy with training data
            self.strategy.prepare(train_data)

            # Validate
            self.strategy.data_validation()

            performance_metrics = self.sensitivity_analysis(test_data, entry_thresholds, exit_thresholds)
            self.print_sensitivity_results(performance_metrics)
    
    def print_sensitivity_results(self, results: Dict) -> None:
        header = "Entry Threshold, Exit Threshold | Total Return(%) | Sharpe Ratio | Max Drawdown(%)"
        print(header)
        print("=" * len(header))
        for thresholds, metrics in results.items():
            row = f"{thresholds[0]}, {thresholds[1]} | {metrics['Total Return(%)']:.2f}% | {metrics['Sharpe Ratio']:.2f} | {metrics['Max Drawdown(%)']:.2f}%"
            print(row)
    
    def sensitivity_analysis(self, test_data: pd.DataFrame, entry_thresholds: List[float], exit_thresholds: List[float]) -> Dict:
        results = {}

        for entry_threshold in entry_thresholds:
            for exit_threshold in exit_thresholds:
                self.strategy.reset()  
                sensitivity_params = {
                    'Entry Threshold': entry_threshold,
                    'Exit Threshold': exit_threshold
                }
                self.print_summary("Sensitivity Analysis Parameters", sensitivity_params)

                equity_curve, signals = self.run_backtest(test_data, entry_threshold, exit_threshold)
                results[(entry_threshold, exit_threshold)] = self.calculate_metrics(equity_curve)

        return results

    def run_backtest(self, data: pd.DataFrame, entry_threshold: float, exit_threshold: float) -> Tuple[List[float], List[Dict]]:
        equity_curve = [self.initial_capital]
        signals = []
        positions = {}
        capital = self.initial_capital  # Get the last known capital

        for i, row in data.iterrows():
            trade_instructions = self.strategy.handle_market_data(row, entry_threshold, exit_threshold)

            if trade_instructions != None:
                print(capital)
                print(positions)
                capital = self.update_positions_and_signals(trade_instructions, row, positions, signals, capital)
                print(positions)
                print(capital)
                
            # Update equity curve
            current_portfolio_value = self.calculate_portfolio_value(row, positions)
            equity_curve.append(capital + current_portfolio_value)

        return equity_curve, signals
    
    def calculate_portfolio_value(self, market_data, positions):
        # Calculate the current value of all positions
        portfolio_value = 0
        for symbol, pos_info in positions.items():
            portfolio_value += (market_data[symbol] - pos_info['entry_price']) * pos_info['weight']
        return portfolio_value

    def update_positions_and_signals(self, trade_instructions, market_data, positions, signals, capital):
        timestamp = market_data.name

        for trade in trade_instructions:
            symbol = trade.contract
            direction = trade.direction
            weight = trade.allocation_percent
            current_price = market_data[symbol]
            units = ((self.trade_allocation * capital) * weight)/ current_price
            
            # Record signal
            signals.append({
                "timestamp": timestamp,
                "symbol": symbol,
                "direction": direction,
                "weight":weight,
                "price": current_price, 
                "units": units

            })

            if symbol in positions:
                position_info = positions[symbol]
                if direction == position_info['direction']:
                    current_value = position_info['entry_price'] * position_info['units'] # value of position before trade
                    added_value = current_price * units # value of trade
                    position_info['units'] += units # updated units
                    position_info['entry_price'] = (current_value + added_value) / position_info['units'] # adjust price to accoutn for new units
                    capital -= current_price * weight  # Deduct the investment from capital
                else:
                    # Calculate P&L for exiting position
                    trade_value = self.record_trade(position_info['entry_price'], current_price, position_info['units'])
                    capital += trade_value # Update capital with P&L
                    # Remove the position
                    del positions[symbol]
            else:
                # Enter new position
                positions[symbol] = {'direction': direction, 'units': units, 'entry_price': current_price, 'weight': weight}
                capital -= units * current_price # Deduct the investment from capital

        return capital

    def record_trade(self, entry_price, current_price, units):
        trade_value = (current_price - entry_price) * units
        return trade_value