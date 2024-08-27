import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import csv
import pandas as pd
from .ui_utils import CreateToolTip
from google_sheets_exporter import GoogleSheetsExporter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class ResultsPanel(ttk.Frame):
    def __init__(self, parent, visualization_panel):
        super().__init__(parent)
        self.google_sheets_exporter = GoogleSheetsExporter()
        self.visualization_panel = visualization_panel
        self.setup_ui()

    def setup_ui(self):
        self.results_text = tk.Text(self, wrap=tk.WORD, width=80, height=20)
        self.results_text.pack(expand=True, fill='both', padx=10, pady=10)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_text.configure(yscrollcommand=scrollbar.set)

        export_frame = ttk.Frame(self)
        export_frame.pack(pady=10)

        self.export_format = tk.StringVar(value="CSV")
        export_formats = ["CSV", "JSON", "Excel", "Google Sheets"]
        export_dropdown = ttk.Combobox(export_frame, textvariable=self.export_format, values=export_formats)
        export_dropdown.pack(side="left", padx=(0, 10))

        self.export_button = ttk.Button(export_frame, text="Export Results", command=self.export_results)
        self.export_button.pack(side="left")

        CreateToolTip(export_dropdown, "Select the format for exporting results")
        CreateToolTip(self.export_button, "Export the current results to a file")

        # Add Google Sheets configuration frame
        gs_frame = ttk.LabelFrame(self, text="Google Sheets Configuration")
        gs_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(gs_frame, text="Sheet ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.sheet_id_entry = ttk.Entry(gs_frame)
        self.sheet_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(gs_frame, text="Credentials File:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.credentials_entry = ttk.Entry(gs_frame)
        self.credentials_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(gs_frame, text="Browse", command=self.browse_credentials).grid(row=1, column=2, padx=5, pady=5)

        gs_frame.columnconfigure(1, weight=1)

        # Add a frame for the matplotlib figure
        self.graph_frame = ttk.Frame(self)
        self.graph_frame.pack(expand=True, fill='both', padx=10, pady=10)

    def update_preferences(self, font_size, default_query_limit):
        def update_font(widget):
            try:
                current_font = widget['font']
                if isinstance(current_font, str):
                    font_family = current_font
                else:
                    font_family = current_font.actual()['family']
                widget.configure(font=(font_family, font_size))
            except (tk.TclError, AttributeError, TypeError):
                pass  # Skip widgets that don't have a font option or can't be modified

        def recursive_update(widget):
            update_font(widget)
            for child in widget.winfo_children():
                recursive_update(child)

        recursive_update(self)

    def display_results(self, entity, results):
        self.results_text.delete('1.0', tk.END)
        self.results = results

        if not results:
            self.results_text.insert(tk.END, "No results found.")
            return

        self.results_text.insert(tk.END, json.dumps(results, indent=2))

        # Prepare data for visualization
        if 'interval_data' in results:
            df = pd.DataFrame(results['interval_data'])
            self.visualization_panel.update_data(df, 'start_date', 'unique_traders', 'Unique Traders Over Time')

    def display_unique_traders(self, results):
        unique_traders = results['uniqueTraders']
        debug_info = results['debug_info']

        self.results_text.insert(tk.END, f"Unique Traders (showing top 5 of {len(unique_traders)}):\n")
        for trader in unique_traders[:5]:
            self.results_text.insert(tk.END, f"{trader['origin']}: {trader['transactionCount']} transactions\n")

        self.results_text.insert(tk.END, f"\nTotal unique traders: {len(unique_traders)}\n\n")
        self.results_text.insert(tk.END, "Debug Info:\n")
        for key, value in debug_info.items():
            self.results_text.insert(tk.END, f"{key}: {value}\n")

        self.results_text.insert(tk.END, f"\nTotal Swaps: {debug_info['total_swaps']}\n")

        # Prepare data for visualization
        self.prepare_visualization_data(unique_traders)

    def prepare_visualization_data(self, unique_traders):
        df = pd.DataFrame(unique_traders)
        df = df.sort_values('transactionCount', ascending=False).head(10)  # Top 10 traders
        self.visualization_panel.update_data(df, 'origin', 'transactionCount', 'Top 10 Traders by Transaction Count')

    def export_results(self):
        if not hasattr(self, 'results') or not self.results:
            tk.messagebox.showwarning("No Data", "There are no results to export.")
            return

        file_format = self.export_format.get()
        
        if file_format == "Google Sheets":
            self.export_to_google_sheets()
        else:
            file_types = {
                "CSV": [("CSV files", "*.csv")],
                "JSON": [("JSON files", "*.json")],
                "Excel": [("Excel files", "*.xlsx")]
            }

            file_path = filedialog.asksaveasfilename(
                defaultextension=f".{file_format.lower()}",
                filetypes=file_types[file_format]
            )

            if not file_path:
                return

            try:
                if file_format == "CSV":
                    self.export_to_csv(file_path)
                elif file_format == "JSON":
                    self.export_to_json(file_path)
                elif file_format == "Excel":
                    self.export_to_excel(file_path)

                tk.messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
            except Exception as e:
                tk.messagebox.showerror("Export Error", f"An error occurred during export: {str(e)}")

    def export_to_csv(self, file_path):
        if isinstance(self.results, dict) and 'interval_data' in self.results:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write summary information
                writer.writerow(["Summary"])
                writer.writerow(["Total Unique Traders", self.results['total_unique_traders']])
                writer.writerow([])  # Empty row for separation

                # Write interval data
                writer.writerow(["Interval Data"])
                writer.writerow(["Start Date", "End Date", "Unique Traders"])
                for interval in self.results['interval_data']:
                    writer.writerow([interval['start_date'], interval['end_date'], interval['unique_traders']])
                writer.writerow([])  # Empty row for separation

                # Write debug information
                writer.writerow(["Debug Information"])
                writer.writerow(["Total Swaps", self.results.get('total_swaps', 'N/A')])
                writer.writerow(["Start Timestamp", self.results.get('start_timestamp', 'N/A')])
                writer.writerow(["End Timestamp", self.results.get('end_timestamp', 'N/A')])
                writer.writerow([])

                # Write individual swap information
                writer.writerow(["Individual Swaps"])
                writer.writerow(["Trader", "Timestamp", "Human Readable Time"])
                for swap in self.results.get('processed_swaps', []):
                    human_readable_time = datetime.fromtimestamp(swap['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                    writer.writerow([swap['trader'], swap['timestamp'], human_readable_time])

        else:
            # Handle other data formats or show an error message
            print("Unsupported data format for CSV export")

    def export_to_json(self, file_path):
        with open(file_path, 'w') as jsonfile:
            json.dump(self.results, jsonfile, indent=2)

    def export_to_excel(self, file_path):
        if isinstance(self.results, dict):
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Total Unique Traders': [self.results.get('total_unique_traders', 'N/A')],
                    'Total Swaps': [self.results.get('total_swaps', 'N/A')],
                    'Start Timestamp': [self.results.get('start_timestamp', 'N/A')],
                    'End Timestamp': [self.results.get('end_timestamp', 'N/A')]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

                # Interval data
                if 'interval_data' in self.results:
                    df_interval = pd.DataFrame(self.results['interval_data'])
                    df_interval.to_excel(writer, sheet_name='Interval Data', index=False)

                # Processed swaps
                if 'processed_swaps' in self.results:
                    df_swaps = pd.DataFrame(self.results['processed_swaps'])
                    df_swaps['human_readable_time'] = pd.to_datetime(df_swaps['timestamp'], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
                    df_swaps.to_excel(writer, sheet_name='Processed Swaps', index=False)

        else:
            pd.DataFrame(self.results).to_excel(file_path, index=False)

    def export_to_google_sheets(self):
        sheet_id = self.sheet_id_entry.get()
        credentials_path = self.credentials_entry.get()

        if not sheet_id or not credentials_path:
            tk.messagebox.showerror("Export Error", "Please provide both Sheet ID and Credentials file path.")
            return

        sheet_name = simpledialog.askstring("Sheet Name", "Enter the sheet name:")
        if not sheet_name:
            return

        try:
            updated_cells = self.google_sheets_exporter.export_to_sheets(
                credentials_path, sheet_id, sheet_name, self.results)
            tk.messagebox.showinfo("Export Successful", f"{updated_cells} cells updated in Google Sheets.")
        except Exception as e:
            tk.messagebox.showerror("Export Error", f"An error occurred: {str(e)}")

    def results_to_dataframe(self):
        if isinstance(self.results, dict):
            if 'uniqueTraders' in self.results:
                return pd.DataFrame(self.results['uniqueTraders'])
            elif 'all_swaps' in self.results:
                return pd.DataFrame(self.results['all_swaps'])
        return pd.DataFrame()

    def browse_credentials(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            self.credentials_entry.delete(0, tk.END)
            self.credentials_entry.insert(0, filename)