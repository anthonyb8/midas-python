import cmd
import os
from datetime import datetime
import importlib
import subprocess
from engine.driver import EventDriver, Mode

class MIDASTraderShell(cmd.Cmd):
    ruler = '-'
    
    dashboard_process = None

    def preloop(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.midas_header()    
        print("Welcome to Midas Terminal")
        self.home()

    def midas_header(self):
        midas_art = """
 __  __ _____ _____      _      ____
|  \/  |_   _|  __ \    / \    /  __|
| \  / | | | | |  | |  / _ \   \  \    
| |\/| | | | | |  | | / ___ \   \  \ 
| |  | |_| |_| |__/ |/ /   \ \  _\  \`
|_|  |_|_____|_____//_/     \_\|____/  
=====================================
        """
        print(midas_art)
    
    def home(self):
        help_text = """╭─────────────────────────────────── Home ────────────────────────────────────╮
│                                                                             │
│ \033[33mCommands available:\033[0m                                                         │
│ \033[36m>    dashboard           Open the trading dashboard\033[0m                         │
│ \033[36m>    live                Start live trading with a specified strategy\033[0m       │
│ \033[36m>    backtest            Run a backtest with a specified strategy\033[0m           │
│ \033[36m>    help                Show this help message\033[0m                             │
│ \033[36m>    exit                Exit the MIDAS Trading Terminal\033[0m                    │
│                                                                             │
╰───────────────────────────────── MIDAS Terminal ────────────────────────────╯
                    """
        print(help_text)

    def do_help(self, arg):
        """Show the home tool box on help"""
        self.home()

    def get_prompt(self):
        current_time = datetime.now().strftime("%Y %b %d, %H:%M")
        return f"{current_time} (MIDAS) $ "

    def do_backtest(self, strategy_name):

        # Correctly format the module path and class name
        module_path = f"strategies.{strategy_name.lower()}.config"
        class_name = f"{strategy_name.capitalize()}Config"

        # Dynamically import the strategy module
        strategy_config_module = importlib.import_module(module_path)

        # Get the strategy configuration class
        strategy_config_class = getattr(strategy_config_module, class_name)

        # Initialize and run the strategy
        strategy_config = strategy_config_class(Mode.BACKTEST)
        
        # Initialize the event driver
        print(f"Started backtest with strategy: {strategy_name}")
        event_driver = EventDriver(strategy_config)
        event_driver.run()

    def do_live(self, strategy_name):
        '''Start live trading with the specified strategy: START_LIVE_TRADING strategy_name'''
        # Correctly format the module path and class name
        module_path = f"strategies.{strategy_name.lower()}.config"
        class_name = f"{strategy_name.capitalize()}Config"

        # Dynamically import the strategy module
        strategy_config_module = importlib.import_module(module_path)

        # Get the strategy configuration class
        strategy_config_class = getattr(strategy_config_module, class_name)

        # Initialize and run the strategy
        strategy_config = strategy_config_class(Mode.LIVE)
        
        # Initialize the event driver
        print(f"Started live trading with strategy: {strategy_name}")
        event_driver = EventDriver(strategy_config)
        event_driver.run()

    def do_dashboard(self, arg):
        '''Open the trading dashboard'''
        script_dir = os.path.dirname(os.path.realpath(__file__))
        frontend_path = os.path.join(script_dir, 'frontend')

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
    
    def do_exit(self, arg):
        """Exit the MIDAS Trading Terminal"""
        # Close the dashboard if it's running
        if self.dashboard_process and self.dashboard_process.poll() is None:
            print("Closing the dashboard...")
            self.dashboard_process.terminate()
            self.dashboard_process = None

        print("Exiting the Trading Manager.")
        return True  # This will stop cmdloop and exit the program

    def cmdloop(self, intro=None):
        self.preloop()
        if intro is not None:
            self.intro = intro
        else:
            self.intro = ''
        stop = None
        while not stop:
            self.prompt = self.get_prompt()  # Update prompt with current time
            try:
                line = input(self.prompt)
                stop = self.onecmd(line)
            except KeyboardInterrupt:
                print("^C")
            except Exception as e:
                print(e)
        self.postloop()

if __name__ == '__main__':
    MIDASTraderShell().cmdloop()
