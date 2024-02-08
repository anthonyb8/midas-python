import os
import logging

class BacktestLogger:
    def __init__(self, strategy:str):
        self.strategy_name = strategy
        self.setup()

    def setup(self):
        # Define the log directory path
        base_dir = os.path.dirname('/Users/anthony/git-projects/midas/')
        log_dir = os.path.join(base_dir, 'research','strategies',self.strategy_name,'outputs')

        # Create the log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Set up the logger
        log_file_name = os.path.join(log_dir, f'{self.strategy_name}.log')
        self.logger = self.settings(f'{self.strategy_name}_logger', log_file_name)
    
        self.logger.info("Backtest logger setup complete.")

    def settings(self,name, log_file, level=logging.INFO):
        """
        Create a logger with the specified name, log file, and log level.

        Parameters:
        - name (str): Name of the logger.
        - log_file (str): File path where logs should be written.
        - level (int): Logging level (default: logging.INFO).

        Returns:
        - logging.Logger: Configured logger instance.
        """
        
        # Get a logger instance for the specified name
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Create a file handler for writing logs
        handler = logging.FileHandler(log_file, mode='w')
        
        # Set a logging format
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # handler.setFormatter(formatter)
        
        # Add the handler to the logger
        logger.addHandler(handler)

        return logger

    # def log_dataframe(self,logger, df):
    #     """
    #     Log a DataFrame with consistent indentation.
    #     """
    #     message = df.to_string()
    #     padding = " "*40   # Adjust this padding to align with the timestamp and other info
    #     message = padding + message.replace("\n", "\n"+padding)
    #     logger.info(message)