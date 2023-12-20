import math
import json
import sys
from dataclasses import dataclass, field
from decimal import Decimal

import pandas as pd
import databento as db

class Config:

    # Alpha threshold to buy/sell, k
    ALPHA_THRESHOLD: int = 1.7

    # Symbol
    DATASET = 'GLBX.MDP3'
    SYMBOL = 'ESU3'
    POINT_VALUE = 50    # $50 per index point

    # Fees
    VENUE_FEES_PER_SIDE: Decimal = Decimal('0.39')
    CLEARING_FEES_PER_SIDE: Decimal = Decimal('0.05')
    FEES_PER_SIDE: Decimal = VENUE_FEES_PER_SIDE + CLEARING_FEES_PER_SIDE

    # Position limit
    POSITION_MAX: int = 10