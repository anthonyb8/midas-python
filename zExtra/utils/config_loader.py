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
