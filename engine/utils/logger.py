import logging

def setup_logger(name, log_file, level=logging.INFO):
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
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(handler)

    return logger


def log_dataframe(logger, df):
    """
    Log a DataFrame with consistent indentation.
    """
    message = df.to_string()
    padding = " "*40   # Adjust this padding to align with the timestamp and other info
    message = padding + message.replace("\n", "\n"+padding)
    logger.info(message)


