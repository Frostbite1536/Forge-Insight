import tkinter as tk
from ui_manager import UIManager
from subgraph_connector import SubgraphConnector
from auth_manager import AuthManager
from error_handler import ErrorHandler
from notifier import Notifier
from plugin_manager import PluginManager
from scheduler import Scheduler

class ForgeInsight:
    def __init__(self):
        self.root = tk.Tk()
        self.subgraph_connector = SubgraphConnector()
        self.auth_manager = AuthManager()
        self.error_handler = ErrorHandler()
        self.notifier = Notifier()
        self.plugin_manager = PluginManager()
        self.scheduler = Scheduler()
        
        self.ui_manager = UIManager(self.root)
        
        self.setup_error_handling()
        self.load_plugins()

    def setup_error_handling(self):
        self.error_handler.set_ui_callback(lambda msg: self.ui_manager.show_error(msg))

    def load_plugins(self):
        self.plugin_manager.load_plugins()
        for plugin in self.plugin_manager.get_plugins():
            plugin.initialize(self)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ForgeInsight()
    app.run()