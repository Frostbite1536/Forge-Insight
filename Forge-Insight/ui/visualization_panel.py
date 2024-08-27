import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import seaborn as sns
from .ui_utils import CreateToolTip
import matplotlib.dates as mdates

class VisualizationPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.df = None
        self.entity = None
        self.x_column = None
        self.y_column = None
        self.title = None
        self.setup_ui()

    def setup_ui(self):
        self.figure, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(expand=True, fill='both')

        control_frame = ttk.Frame(self)
        control_frame.pack(pady=10)

        ttk.Label(control_frame, text="Chart Type:").grid(row=0, column=0, padx=5)
        self.chart_type_var = tk.StringVar(value="Bar")
        self.chart_type = ttk.Combobox(control_frame, textvariable=self.chart_type_var)
        self.chart_type['values'] = ['Bar', 'Line', 'Scatter', 'Pie', 'Heatmap']
        self.chart_type.grid(row=0, column=1, padx=5)
        self.chart_type.bind("<<ComboboxSelected>>", self.update_visualization)

    def update_data(self, df, x_column, y_column, title):
        self.df = df
        self.x_column = x_column
        self.y_column = y_column
        self.title = title
        self.update_visualization()

    def update_visualization(self, event=None):
        if self.df is None or self.df.empty:
            self.clear_visualization()
            return

        chart_type = self.chart_type_var.get()

        try:
            self.ax.clear()

            # Convert 'start_date' to datetime
            self.df['start_date'] = pd.to_datetime(self.df['start_date'])

            if chart_type == "Bar":
                self.create_bar_chart()
            elif chart_type == "Line":
                self.create_line_chart()
            elif chart_type == "Scatter":
                self.create_scatter_plot()
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")

            self.ax.set_title(self.title)
            self.ax.set_xlabel(self.x_column)
            self.ax.set_ylabel(self.y_column)
            
            # Format x-axis to show dates nicely
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            self.ax.xaxis.set_major_locator(mdates.DayLocator())
            plt.xticks(rotation=45, ha='right')

            plt.tight_layout()
            self.canvas.draw()

        except Exception as e:
            self.show_error("Visualization Error", str(e))

    def create_bar_chart(self):
        self.ax.bar(self.df['start_date'], self.df[self.y_column])

    def create_line_chart(self):
        self.ax.plot(self.df['start_date'], self.df[self.y_column], marker='o')

    def create_scatter_plot(self):
        self.ax.scatter(self.df['start_date'], self.df[self.y_column])

    def create_pie_chart(self):
        self.ax.pie(self.df[self.y_column], labels=self.df[self.x_column], autopct='%1.1f%%')

    def create_heatmap(self):
        sns.heatmap(self.df.pivot(self.x_column, self.y_column, 'value'), ax=self.ax)

    def clear_visualization(self):
        self.df = None
        self.entity = None
        self.ax.clear()
        self.ax.text(0.5, 0.5, "No data to visualize", ha='center', va='center')
        self.canvas.draw()

    def update_preferences(self, font_size, default_query_limit):
        plt.rcParams.update({'font.size': font_size})
        self.update_visualization()

    def show_error(self, title, message):
        tk.messagebox.showerror(title, message)