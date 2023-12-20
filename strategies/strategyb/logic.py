import math
import json
import sys
from dataclasses import dataclass, field
from decimal import Decimal

import pandas as pd
import databento as db

API_KEY = 'YOUR_API_KEY'

from .config import Config

@dataclass
class Strategy:

    ## -- Below are instance variables that will.

    # Dataset
    dataset: str

    # Instrument to trade
    symbol: str

    # Current position, in contract units
    position: int = 0
    # Number of long contract sides traded
    buy_qty: int = 0
    # Number of short contract sides traded
    sell_qty: int = 0

    ## Total realized buy price
    real_total_buy_px: Decimal = 0
    ## Total realized sell price
    real_total_sell_px: Decimal = 0

    # Total buy price to liquidate current position
    theo_total_buy_px: Decimal = 0
    # Total sell price to liquidate current position
    theo_total_sell_px: Decimal = 0

    # Total fees paid
    fees: Decimal = 0

    # List to track results
    results: list = field(default_factory=list)

    def run(self) -> None:
        client = db.Live()
        client.subscribe(
            dataset=self.dataset,
            schema='mbp-1',
            stype_in='raw_symbol',
            symbols=[self.symbol],
            # start="2023-08-08T12:00",    # Burn-in start time
        )
        for record in client:
            if not isinstance(record, db.MBP1Msg):
                continue
            self.update(record)

    def update(self, record: db.MBP1Msg) -> None:
        ask_size = record.levels[0].ask_sz
        bid_size = record.levels[0].bid_sz
        ask_price = record.levels[0].ask_px / Decimal("1e9")
        bid_price = record.levels[0].bid_px / Decimal("1e9")

        skew = math.log10(bid_size) - math.log10(ask_size)
        mid_price = (ask_price + bid_price) / 2

        # Buy/sell based when skew signal is large
        if skew > Config.ALPHA_THRESHOLD and self.position < Config.POSITION_MAX:
            self.position += 1
            self.buy_qty += 1
            self.real_total_buy_px += ask_price
            self.fees += Config.FEES_PER_SIDE
        elif skew < -Config.ALPHA_THRESHOLD and self.position > -Config.POSITION_MAX:
            self.position -= 1
            self.sell_qty += 1
            self.real_total_sell_px += bid_price
            self.fees += Config.FEES_PER_SIDE

        # Update prices
        # Fill prices are based on BBO with assumed zero latency
        # In practice, should be worse because of alpha decay
        if self.position == 0:
            self.theo_total_buy_px = 0
            self.theo_total_sell_px = 0
        elif self.position > 0:
            self.theo_total_sell_px = bid_price * abs(self.position)
        elif self.position < 0:
            self.theo_total_buy_px = ask_price * abs(self.position)

        # Compute PnL
        theo_pnl = (
            Config.POINT_VALUE
            * (
                self.real_total_sell_px
                + self.theo_total_sell_px
                - self.real_total_buy_px
                - self.theo_total_buy_px
            )
            - self.fees
        )

        result = {
            'ts_strategy': str(pd.Timestamp(record.ts_recv, tz='UTC')),
            'bid': f'{bid_price:0.2f}',
            'ask': f'{ask_price:0.2f}',
            'skew' : f'{skew:0.3f}',
            'position': self.position,
            'trade_ct': self.buy_qty + self.sell_qty,
            'fees': f'{self.fees:0.2f}',
            'pnl': f'{theo_pnl:0.2f}',
        }

        print(json.dumps(result, indent=4))

        self.results.append(result)


if __name__ == "__main__":
    strategy = Strategy(dataset=Config.DATASET, symbol=Config.SYMBOL)
    while True:
        try:
            strategy.run()
        # Allow for a graceful exit
        except KeyboardInterrupt:
            df = pd.DataFrame(strategy.results)
            df.to_csv('strategy_log.csv', index=False)
            sys.exit()
