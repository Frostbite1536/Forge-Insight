import os
import importlib
import inspect

class PluginManager:
    def __init__(self):
        self.plugins = []

    def load_plugins(self):
        plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        if not os.path.exists(plugin_dir):
            return

        for filename in os.listdir(plugin_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'plugins.{module_name}')
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and hasattr(obj, 'initialize'):
                            self.plugins.append(obj())
                except ImportError as e:
                    print(f"Error loading plugin {module_name}: {str(e)}")

    def get_plugins(self):
        return self.plugins

    def execute_hook(self, hook_name, *args, **kwargs):
        for plugin in self.plugins:
            if hasattr(plugin, hook_name):
                try:
                    getattr(plugin, hook_name)(*args, **kwargs)
                except Exception as e:
                    print(f"Error executing hook {hook_name} in plugin {plugin.__class__.__name__}: {str(e)}")