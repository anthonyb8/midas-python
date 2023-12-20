from abc import ABC, abstractmethod
from typing import Dict

class BasePortfolioHandler(ABC):
    """
    Abstract base class for a portfolio handler.

    This class defines the structure for various types of portfolio handlers,
    which are responsible for managing and reporting the state of a trading
    portfolio. This includes tracking positions, cash balance, and other
    relevant portfolio metrics.
    """

    @abstractmethod
    def get_positions(self) -> Dict:
        """
        Abstract method to return the current positions in the portfolio.

        This method should provide a detailed snapshot of all current positions,
        including quantities, symbols, and any other relevant information.

        Returns:
            Dict: A dictionary containing details of all positions in the portfolio.
                  The format and contents of this dictionary will depend on the
                  specific implementation and the requirements of the trading system.

        Raises:
            NotImplementedError: If the method is not implemented in the derived class.
        """
        raise NotImplementedError("Must implement get_positions method")

    @abstractmethod
    def get_cash(self) -> float:
        """
        Abstract method to return the available cash balance in the portfolio.

        This should reflect the cash available for trading, not including any
        reserved margin or locked amounts.

        Returns:
            float: The available cash balance in the portfolio.

        Raises:
            NotImplementedError: If the method is not implemented in the derived class.
        """
        raise NotImplementedError("Must implement get_cash method")
