from enum import Enum , auto

class Action(Enum):
    """ Long and short are treated as entry actions and short/cover are treated as exit actions. """
    LONG = auto()  # BUY
    COVER = auto() # BUY
    SHORT = auto() # SELL
    SELL = auto()  # SELL

    def to_broker_standard(self):
        """Converts the enum to the standard BUY or SELL action for the broker."""
        if self in [Action.LONG, Action.COVER]:
            return 'BUY'
        elif self in [Action.SHORT, Action.SELL]:
            return 'SELL'
        else:
            raise ValueError(f"Invalid action: {self}")