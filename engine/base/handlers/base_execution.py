from abc import ABC, abstractmethod
from typing import Any
from ..events import OrderEvent

class BaseExecutionHandler(ABC):
    """
    Abstract base class for an execution handler.

    This class defines the structure for various types of execution handlers,
    which are responsible for processing and executing orders in different
    trading environments (e.g., live trading, backtesting).
    """

    @abstractmethod
    def on_order(self, order_event: OrderEvent):
        """
        Abstract method to handle order events.

        This method should define how to process an order event, such as
        sending it to a broker in a live trading environment or handling it
        in a simulated environment for backtesting.

        Parameters:
            order_event (OrderEvent): The order event to be processed.

        Raises:
            NotImplementedError: If the method is not implemented in the derived class.
        """
        raise NotImplementedError("Must implement handle_order_event method")

    @abstractmethod
    def handle_order(self, order_event: OrderEvent) -> Any:
        """
        Abstract method to execute an order and return the result.

        The implementation of this method should handle the actual execution
        of the order, such as sending it to a trading venue or simulating the
        order execution in backtesting.

        Parameters:
            order_event (OrderEvent): The order event to be executed.

        Returns:
            Any: The result of the order execution. The format of the return
                 value can vary depending on the specific execution mechanism.
                 It could be an execution confirmation, a transaction ID, or
                 any other relevant information.

        Raises:
            NotImplementedError: If the method is not implemented in the derived class.
        """
        raise NotImplementedError("Must implement execute_order method")
