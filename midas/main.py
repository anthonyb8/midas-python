# main.py
from midas.strategies.cointegrationzscore import CointegrationzscoreConfig
from midas.command import MidasShell, EventController, Mode



### Development
def main():
    # Set the mode (LIVE or BACKTEST)
    mode = Mode.BACKTEST
    # Initialize the strategy configuration
    strategy_config = CointegrationzscoreConfig(mode)

    # Initialize the event driver
    event_driver = EventController(strategy_config)
    event_driver.run()

if __name__ == "__main__":
    main()


### Production 
# if __name__ == '__main__':
#     MidasShell().cmdloop()