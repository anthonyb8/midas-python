# main.py
from core.strategies.strategya.config import StrategyaConfig
from command.driver import EventDriver, Mode


def main():
    # Set the mode (LIVE or BACKTEST)
    mode = Mode.BACKTEST

    # Initialize the strategy configuration
    strategy_config = StrategyaConfig(mode)

    # Initialize the event driver
    event_driver = EventDriver(strategy_config)
    event_driver.run()

if __name__ == "__main__":
    main()
