from abc import ABC, abstractmethod
from typing import Any, List

class BaseDataHandler(ABC):
    """
    Abstract base class for a data handler.

    This class provides a structure for various types of data handlers,
    such as those for live trading and backtesting environments. It ensures
    that all derived data handler classes implement the required methods.
    """

    @abstractmethod
    def get_data(self, *args, **kwargs) -> Any:
        """
        Abstract method to retrieve data.

        The implementation of this method should handle data retrieval
        in a manner appropriate for the specific trading environment
        (live, backtest, etc.). The method's signature can be flexible
        to accommodate different types of data requests.

        Parameters:
            args: Variable length argument list.
            kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The format of the return value depends on the implementation.
                 It could be a DataFrame, a list of market events, or any other
                 data structure relevant to the trading environment.

        Raises:
            NotImplementedError: If the method is not implemented in the derived class.
        """
        raise NotImplementedError("Must implement get_data method")
