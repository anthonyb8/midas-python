import yaml
import importlib

def load_main_config():
    """Load the main configuration file."""
    with open('/Users/anthony/git-projects/EventTrader/system/config.yml', 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_config_for_api():
    main_config = load_main_config()
    return main_config['API']

# # STRATEGY SET-UP
# def get_strategy_config(strategy_name: str):
#     """Load a specific strategy's configuration using its name."""
    
#     # First, load the main configuration
#     main_config = load_main_config()
#     # Get the path to the strategy's configuration
#     strategy_config = main_config['strategy_name'].get(strategy_name)

#     return strategy_config

# def load_strategy(strategy_name: str):
#     strategy_config = get_strategy_config(strategy_name)

#     module_path = strategy_config.get('module_path')
#     class_name = strategy_config.get('class_name')
#     try:
#         module = importlib.import_module(module_path)
#         strategy_class = getattr(module, class_name)
#         return strategy_class
#     except (ModuleNotFoundError, AttributeError) as e:
#         raise ImportError(f"Failed to import strategy {strategy_name}. Error: {e}")
    
# # BACKTEST or LIVE SET-UP
# def get_config_for_mode(mode: str):
#     """Get the configuration for a given mode (LIVE or BACKTEST)."""
#     main_config = load_main_config()
#     mode_config = main_config.get(mode.upper(), {}) 
#     if not mode_config:
#         raise ValueError(f"Invalid mode: {mode}. Only 'LIVE' and 'BACKTEST' are supported.")
#     return mode_config

# def load_module_from_config(path_key, config):
#     """Load a module from a configuration."""
#     module_path = config.get(path_key)
  
#     try:
#         module = importlib.import_module(module_path)
#         return module
#     except ModuleNotFoundError as e:
#         raise ImportError(f"Failed to import module from {module_path}. Error: {e}")

# def load_handlers_for_mode(mode: str):
#     mode_config = get_config_for_mode(mode)
#     handlers = {}

#     for handler_name, handler_path in mode_config.items():
#         handlers[handler_name] = load_module_from_config(handler_name, mode_config)

#     return handlers
