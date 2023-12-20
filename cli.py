#!/Users/anthony/git-projects/midas/venv_alpha/bin/python3
import cmd
import os
import importlib
import threading
import subprocess
# from uvicorn import Config, Server
import asyncio
# from system.config import MODE_LIVE, MODE_BACKTEST
import time

class EventTraderShell(cmd.Cmd):

    def preloop(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def postloop(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    intro = 'Welcome to the Alpha Trader. Type help or ? to list commands.\n'
    prompt = '>'
    ruler = '='

    api_thread = None
    dashboard_process = None

    def start_api(self):
        if self.api_thread is None or not self.api_thread.is_alive():
            # Define the command to start the Django server
            django_server_command = ["python", "manage.py", "runserver", "127.0.0.1:8000"]
            # Start the Django server as a subprocess
            self.api_thread = subprocess.Popen(django_server_command)
            print("Django API server started.")


    def stop_api(self):
        if self.api_thread and self.api_thread.is_alive():
            self.server.should_exit = True
            try:
                self.api_thread.join()  # Wait for the server thread to exit
            except asyncio.CancelledError:
                pass  # Ignore CancelledError during shutdown
            print("API server stopped.")

    def do_backtest(self, strategy_name):
        self.start_api()
        time.sleep(2)
        # Correctly format the module path and class name
        module_path = f"strategies.{strategy_name.lower()}.config"
        class_name = f"{strategy_name.capitalize()}Config"

        # Dynamically import the strategy module
        strategy_config_module = importlib.import_module(module_path)

        # Get the strategy configuration class
        strategy_config_class = getattr(strategy_config_module, class_name)

        # Initialize and run the strategy
        strategy_config = strategy_config_class(MODE_BACKTEST)
        strategy_config.run()
        print(f"Started backtest with strategy: {strategy_name}")
        time.sleep(2)
        self.stop_api()

    def do_live_trade(self, strategy_name):
        '''Start live trading with the specified strategy: START_LIVE_TRADING strategy_name'''
        # Correctly format the module path and class name
        module_path = f"strategies.{strategy_name.lower()}.config"
        class_name = f"{strategy_name.capitalize()}Config"

        # Dynamically import the strategy module
        strategy_config_module = importlib.import_module(module_path)

        # Get the strategy configuration class
        strategy_config_class = getattr(strategy_config_module, class_name)

        # Initialize and run the strategy
        strategy_config = strategy_config_class(MODE_LIVE)
        strategy_config.run()
        print(f"Started live trading with strategy: {strategy_name}")

    def do_dashboard(self, arg):
        '''Open the trading dashboard'''
        script_dir = os.path.dirname(os.path.realpath(__file__))
        frontend_path = os.path.join(script_dir, 'frontend')

        self.start_api()
        time.sleep(2)  # Wait for the API to start

        # Start the React app
        print("Opening dashboard...")
        self.dashboard_process = subprocess.Popen(["npm", "start"], cwd=frontend_path)
        print("Dashboard is running...")

    def do_close_dashboard(self, arg):
        '''Close the trading dashboard'''
        # Stop the React app
        if self.dashboard_process:
            self.dashboard_process.terminate()
            self.dashboard_process = None
            print("Dashboard has been closed.")

        # Stop the API
        self.stop_api()
    
    def do_exit(self, arg):
        '\nExit the program: EXIT\nThis command will exit the Trading Manager.\n'

        # Close the dashboard if it's running
        if self.dashboard_process and self.dashboard_process.poll() is None:
            print("Closing the dashboard...")
            self.dashboard_process.terminate()
            self.dashboard_process = None

        # Stop the API if it's running
        if self.api_thread and self.api_thread.is_alive():
            print("Stopping the API server...")
            self.stop_api()

        print("Exiting the Trading Manager.")
        return True  # This will stop cmdloop and exit the program

if __name__ == '__main__':
    EventTraderShell().cmdloop()
