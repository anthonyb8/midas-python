from abc import ABC, abstractmethod

class BasePerformanceHandler(ABC):
    """
    Abstract base class for a performance handler.

    This class defines the structure for various types of performance handlers,
    which are responsible for tracking and analyzing the performance of a trading
    strategy over time. This includes maintaining a trade log, calculating metrics
    like return, risk, drawdown, and other relevant performance statistics.
    """

    # @abstractmethod
    # def update_trades(self):
    #     """
    #     Abstract method to update the trade log.

    #     This method should define how to record and update trade data,
    #     such as capturing trade execution details, updating performance
    #     metrics, and any other relevant information pertaining to trades.

    #     The specifics of what this method updates and how it does so will
    #     depend on the trading environment and the needs of the trading strategy.

    #     Raises:
    #         NotImplementedError: If the method is not implemented in the derived class.
    #     """
    #     raise NotImplementedError("Must implement update_trades method")
