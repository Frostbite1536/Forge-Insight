import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

class HelpSystem(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Forge Insight Help")
        self.geometry("600x400")
        self.setup_ui()

    def setup_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')

        self.add_help_page(notebook, "Overview", self.get_overview_text())
        self.add_help_page(notebook, "Query Panel", self.get_query_panel_text())
        self.add_help_page(notebook, "Results Panel", self.get_results_panel_text())
        self.add_help_page(notebook, "Visualization Panel", self.get_visualization_panel_text())

    def add_help_page(self, notebook, title, content):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)

        text_widget = ScrolledText(frame, wrap=tk.WORD)
        text_widget.pack(expand=True, fill='both')
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

    def get_overview_text(self):
        return """
        Forge Insight is a tool for querying and visualizing data from Forge subgraphs on Evmos.

        Key Features:
        - Query multiple subgraphs
        - Visualize data with various chart types
        - Export data in multiple formats
        - Customizable user interface

        Use the tabs above to learn more about each component of the application.
        """

    def get_query_panel_text(self):
        return """
        The Query Panel allows you to construct and submit queries to the selected subgraph.

        Steps to use:
        1. Select a subgraph from the dropdown
        2. Choose an entity to query
        3. Select the fields you want to retrieve
        4. (Optional) Add filters to refine your query
        5. Set a limit for the number of results
        6. Click 'Submit Query' to run your query

        Filters should be in the format: key1: value1, key2: value2
        """

    def get_results_panel_text(self):
        return """
        The Results Panel displays the data returned from your query.

        Features:
        - View raw data in JSON format
        - Export data to CSV, JSON, or Excel formats

        To export data:
        1. Select the desired export format from the dropdown
        2. Click the 'Export Results' button
        3. Choose a location to save the file
        """

    def get_visualization_panel_text(self):
        return """
        The Visualization Panel allows you to create charts and graphs from your query results.

        Steps to create a visualization:
        1. Select a chart type from the dropdown
        2. Choose the fields for the X and Y axes
        3. (Optional) Select a color scheme

        Available chart types:
        - Bar chart
        - Line chart
        - Scatter plot
        - Pie chart
        - Box plot
        - Violin plot
        - Heatmap

        Experiment with different combinations to find the best way to represent your data!
        """