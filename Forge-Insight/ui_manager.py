import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, font
import json
import os
from config import WINDOW_TITLE, WINDOW_SIZE, THEME, SCHEMA
from subgraph_connector import SubgraphConnector
from ui.query_panel import QueryPanel
from ui.results_panel import ResultsPanel
from ui.visualization_panel import VisualizationPanel

class UIManager:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        self.subgraph_connector = SubgraphConnector()
        self.setup_ui()
        self.load_preferences()
        self.apply_theme()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Create visualization_panel first
        self.visualization_panel = VisualizationPanel(self.notebook)
        
        # Now create query_panel and results_panel, passing the visualization_panel to results_panel
        self.query_panel = QueryPanel(self.notebook, self.subgraph_connector, self.display_results)
        self.results_panel = ResultsPanel(self.notebook, self.visualization_panel)
        
        # Add panels to notebook
        self.notebook.add(self.query_panel, text="Query")
        self.notebook.add(self.results_panel, text="Results")
        self.notebook.add(self.visualization_panel, text="Visualization")

        self.setup_menu()

    def display_results(self, entity, results):
        self.results_panel.display_results(entity, results)

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Preferences", command=self.open_preferences)

    def open_preferences(self):
        # Implement preferences dialog
        pass

    def load_preferences(self):
        try:
            with open('preferences.json', 'r') as f:
                self.preferences = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Preferences file not found or corrupted. Using default settings.")
            self.preferences = {
                "theme": THEME,
                "bg_color": "#FFFFFF",
                "font_family": "Arial",
                "font_size": 10,
                "default_query_limit": 100,
                "default_chart_type": "bar"
            }

    def save_preferences(self):
        # Implement saving preferences to file
        pass

    def apply_theme(self):
        try:
            style = ttk.Style()
            style.theme_use(self.preferences.get("theme", THEME))
            # Apply other theme settings...
        except tk.TclError:
            print(f"Failed to apply theme {self.preferences.get('theme')}. Falling back to default.")
            style.theme_use(THEME)

    def apply_preferences(self, theme, bg_color, font_family, font_size, default_query_limit, default_chart_type):
        # Implement applying preferences to UI components
        pass

    def update_ui_components(self):
        for component in [self.query_panel, self.results_panel, self.visualization_panel]:
            if hasattr(component, 'update_preferences'):
                component.update_preferences(self.font_size, self.default_query_limit)

    def show_error(self, message):
        self.query_panel.show_error("Error", message)

def run_app():
    root = tk.Tk()
    UIManager(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()