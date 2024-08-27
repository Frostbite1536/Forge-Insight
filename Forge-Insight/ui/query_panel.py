import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .ui_utils import CreateToolTip
from config import SCHEMA, EVMOS_DICTIONARY_PATH, USER_DICTIONARIES_DIR, FAVORITES_FILE, MAX_QUERY_LIMIT
import json
import os
import time
from datetime import datetime, timedelta
import re

class QueryPanel(ttk.Frame):
    def __init__(self, parent, subgraph_connector, query_callback):
        super().__init__(parent)
        self.subgraph_connector = subgraph_connector
        self.query_callback = query_callback
        self.blockchain_data = self.load_evmos_dictionary()
        self.user_dictionaries = self.load_user_dictionaries()
        self.favorites = self.load_favorites()
        self.schema = SCHEMA
        self.setup_ui()

    def load_evmos_dictionary(self):
        with open(EVMOS_DICTIONARY_PATH, 'r') as f:
            data = json.load(f)
            print(f"Loaded Evmos dictionary: {data.keys()}")
            print(f"Number of pools: {len(data.get('pools', []))}")
            print(f"Number of tokens: {len(data.get('tokens', []))}")
            return data

    def load_user_dictionaries(self):
        user_dicts = {}
        for filename in os.listdir(USER_DICTIONARIES_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(USER_DICTIONARIES_DIR, filename), 'r') as f:
                    data = json.load(f)
                    user_dicts[data['blockchain']] = data
        return user_dicts

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_favorites(self):
        with open(FAVORITES_FILE, 'w') as f:
            json.dump(self.favorites, f)

    def setup_ui(self):
        # Subgraph selection
        ttk.Label(self, text="Select Subgraph:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.subgraph_var = tk.StringVar()
        self.subgraph_combo = ttk.Combobox(self, textvariable=self.subgraph_var, state="readonly")
        self.subgraph_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.subgraph_combo.bind("<<ComboboxSelected>>", self.on_subgraph_selected)
        CreateToolTip(self.subgraph_combo, "Select the subgraph you want to query")

        # Blockchain selection
        ttk.Label(self, text="Select Blockchain:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.blockchain_var = tk.StringVar(value="Evmos")
        self.blockchain_combo = ttk.Combobox(self, textvariable=self.blockchain_var, values=self.get_blockchain_list(), state="readonly")
        self.blockchain_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.blockchain_combo.bind("<<ComboboxSelected>>", self.on_blockchain_selected)
        CreateToolTip(self.blockchain_combo, "Choose the blockchain you're interested in")

        # Entity selection
        ttk.Label(self, text="Select Entity:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entity_var = tk.StringVar()
        self.entity_dropdown = ttk.Combobox(self, textvariable=self.entity_var, state="readonly")
        self.entity_dropdown.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.entity_dropdown.bind("<<ComboboxSelected>>", self.update_fields)
        CreateToolTip(self.entity_dropdown, "Select the type of data you want to query")

        # Fields selection
        ttk.Label(self, text="Select Fields:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.fields_frame = ttk.Frame(self)
        self.fields_frame.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)
        self.field_vars = {}

        # Query target selection
        ttk.Label(self, text="Query Target:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.query_target = tk.StringVar(value="Pool")
        ttk.Radiobutton(self, text="Pool", variable=self.query_target, value="Pool", command=self.toggle_query_target).grid(row=4, column=1, sticky="w", padx=5, pady=2)
        ttk.Radiobutton(self, text="Token", variable=self.query_target, value="Token", command=self.toggle_query_target).grid(row=4, column=1, sticky="e", padx=5, pady=2)
        ttk.Radiobutton(self, text="Custom", variable=self.query_target, value="Custom", command=self.toggle_query_target).grid(row=5, column=1, sticky="w", padx=5, pady=2)

        # Pool selection
        self.pool_label = ttk.Label(self, text="Select Pool:")
        self.pool_label.grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.pool_var = tk.StringVar()
        self.pool_combo = ttk.Combobox(self, textvariable=self.pool_var, state="readonly")
        self.pool_combo.grid(row=6, column=1, sticky="ew", padx=5, pady=5)
        self.pool_combo.bind("<<ComboboxSelected>>", self.on_pool_selected)
        CreateToolTip(self.pool_combo, "Select a specific pool to query")

        # Token selection
        self.token_label = ttk.Label(self, text="Select Token:")
        self.token_label.grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.token_var = tk.StringVar()
        self.token_combo = ttk.Combobox(self, textvariable=self.token_var, state="readonly")
        self.token_combo.grid(row=7, column=1, sticky="ew", padx=5, pady=5)
        self.token_combo.bind("<<ComboboxSelected>>", self.on_token_selected)
        CreateToolTip(self.token_combo, "Select a specific token to query")

        # Custom address entry
        ttk.Label(self, text="Custom Address:").grid(row=8, column=0, sticky="w", padx=5, pady=5)
        self.address_entry = ttk.Entry(self)
        self.address_entry.grid(row=8, column=1, sticky="ew", padx=5, pady=5)
        CreateToolTip(self.address_entry, "Enter a custom address to query")

        # Initially hide token selection and disable custom address
        self.token_label.grid_remove()
        self.token_combo.grid_remove()
        self.address_entry.config(state="disabled")

        # Limit entry
        ttk.Label(self, text="Limit:").grid(row=9, column=0, sticky="w", padx=5, pady=5)
        self.limit_var = tk.StringVar(value="100")
        ttk.Entry(self, textvariable=self.limit_var).grid(row=9, column=1, sticky="ew", padx=5, pady=5)

        # Query Type selection
        ttk.Label(self, text="Query Type:").grid(row=10, column=0, sticky="w", padx=5, pady=5)
        self.query_type = tk.StringVar(value="Standard")
        self.query_types = ["Standard", "Wallet Overview", "Unique Traders Over Time"]
        self.query_type_combo = ttk.Combobox(self, textvariable=self.query_type, values=self.query_types, state="readonly")
        self.query_type_combo.grid(row=10, column=1, sticky="ew", padx=5, pady=5)
        self.query_type_combo.bind("<<ComboboxSelected>>", self.on_query_type_change)
        CreateToolTip(self.query_type_combo, "Choose the type of query to run")

        # Add fields for Unique Traders Over Time query
        self.days_var = tk.StringVar(value="180")
        self.interval_var = tk.StringVar(value="30")
        
        self.days_label = ttk.Label(self, text="Days:")
        self.days_entry = ttk.Entry(self, textvariable=self.days_var)
        self.interval_label = ttk.Label(self, text="Interval (days):")
        self.interval_entry = ttk.Entry(self, textvariable=self.interval_var)

        # Initially hide these fields
        self.days_label.grid(row=11, column=0, padx=5, pady=5)
        self.days_entry.grid(row=11, column=1, padx=5, pady=5)
        self.interval_label.grid(row=12, column=0, padx=5, pady=5)
        self.interval_entry.grid(row=12, column=1, padx=5, pady=5)
        self.days_label.grid_remove()
        self.days_entry.grid_remove()
        self.interval_label.grid_remove()
        self.interval_entry.grid_remove()

        # Advanced Options Frame
        self.advanced_frame = ttk.LabelFrame(self, text="Advanced Options")
        self.advanced_frame.grid(row=13, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Time Filter
        ttk.Label(self.advanced_frame, text="Time Filter:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.time_filter_var = tk.StringVar(value="All time")
        self.time_filter_combo = ttk.Combobox(self.advanced_frame, textvariable=self.time_filter_var, state="readonly")
        self.time_filter_combo['values'] = ['Last 24 hours', 'Last 7 days', 'Last 30 days', 'All time']
        self.time_filter_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        CreateToolTip(self.time_filter_combo, "Filter results by time range")

        # Custom Filter
        ttk.Label(self.advanced_frame, text="Custom Filter:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.custom_filter_var = tk.StringVar()
        self.custom_filter_entry = ttk.Entry(self.advanced_frame, textvariable=self.custom_filter_var)
        self.custom_filter_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        CreateToolTip(self.custom_filter_entry, "Add custom filtering conditions")

        # Order By
        ttk.Label(self.advanced_frame, text="Order By:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.order_by_var = tk.StringVar()
        self.order_by_combo = ttk.Combobox(self.advanced_frame, textvariable=self.order_by_var, state="readonly")
        self.order_by_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        CreateToolTip(self.order_by_combo, "Select a field to sort the results by")

        # Order Direction
        ttk.Label(self.advanced_frame, text="Order Direction:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.order_direction = tk.StringVar(value="desc")
        ttk.Radiobutton(self.advanced_frame, text="Ascending", variable=self.order_direction, value="asc").grid(row=3, column=1, sticky="w", padx=5, pady=2)
        ttk.Radiobutton(self.advanced_frame, text="Descending", variable=self.order_direction, value="desc").grid(row=4, column=1, sticky="w", padx=5, pady=2)

        # Initialize the advanced options
        self.toggle_query_options()

        # Search and filter
        ttk.Label(self, text="Search:").grid(row=14, column=0, sticky="w", padx=5, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self, textvariable=self.search_var)
        self.search_entry.grid(row=14, column=1, sticky="ew", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_lists)

        # Favorites
        ttk.Button(self, text="Add to Favorites", command=self.add_to_favorites).grid(row=15, column=0, padx=5, pady=5)
        ttk.Button(self, text="Manage Favorites", command=self.manage_favorites).grid(row=15, column=1, padx=5, pady=5)

        # User dictionary upload
        ttk.Button(self, text="Upload Custom Dictionary", command=self.upload_custom_dictionary).grid(row=16, column=0, columnspan=2, padx=5, pady=5)

        # Query button
        ttk.Button(self, text="Run Query", command=self.run_query).grid(row=17, column=0, columnspan=2, pady=10)

        # Help button
        ttk.Button(self, text="Help", command=self.show_help).grid(row=18, column=0, columnspan=2, pady=10)

        self.update_subgraph_list()
        self.update_lists()
        self.update_entity_list()

    def get_blockchain_list(self):
        blockchains = ["Evmos"] + [chain for chain in self.user_dictionaries.keys() if chain != "Evmos"]
        return blockchains

    def update_subgraph_list(self):
        subgraphs = self.subgraph_connector.get_subgraph_list()
        self.subgraph_combo['values'] = subgraphs
        if subgraphs:
            self.subgraph_combo.set(subgraphs[0])
            self.on_subgraph_selected()

    def on_subgraph_selected(self, event=None):
        selected_subgraph = self.subgraph_var.get()
        self.subgraph_connector.set_current_subgraph(selected_subgraph)
        self.update_entity_list()

    def update_entity_list(self):
        entities = self.subgraph_connector.get_entities()
        self.entity_dropdown['values'] = entities
        if entities:
            self.entity_dropdown.set(entities[0])
            self.update_fields()

    def update_fields(self, event=None):
        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        entity = self.entity_var.get()
        fields = self.subgraph_connector.get_entity_fields(entity)
        self.field_vars = {}
        for i, field in enumerate(fields):
            var = tk.BooleanVar(value=True)
            chk = ttk.Checkbutton(self.fields_frame, text=field, variable=var)
            chk.grid(row=i//3, column=i%3, sticky="w")
            self.field_vars[field] = var
            CreateToolTip(chk, self.subgraph_connector.get_field_description(entity, field))

        # Disable time filter for Factory entity
        if entity.lower() in ['factory', 'factories']:
            self.time_filter_combo.config(state="disabled")
            self.time_filter_var.set("All time")
        else:
            self.time_filter_combo.config(state="readonly")

    def on_blockchain_selected(self, event=None):
        print("Blockchain selected")  # Debug print
        self.update_lists()
        self.update_entity_list()

    def on_pool_selected(self, event=None):
        pool_name = self.pool_var.get()
        blockchain = self.blockchain_var.get()
        pool_data = next((pool for pool in self.get_pools(blockchain) if pool['name'] == pool_name), None)
        if pool_data:
            self.address_entry.config(state="normal")
            self.address_entry.delete(0, tk.END)
            self.address_entry.insert(0, pool_data['address'])
            self.address_entry.config(state="disabled")

    def on_token_selected(self, event=None):
        token_name = self.token_var.get()
        blockchain = self.blockchain_var.get()
        token_data = next((token for token in self.get_tokens(blockchain) if token['name'] == token_name), None)
        if token_data:
            self.address_entry.config(state="normal")
            self.address_entry.delete(0, tk.END)
            self.address_entry.insert(0, token_data['address'])
            self.address_entry.config(state="disabled")

    def get_pools(self, blockchain):
        pools = self.blockchain_data.get('pools', []) + self.user_dictionaries.get(blockchain, {}).get('pools', [])
        print(f"Getting pools for {blockchain}: {len(pools)} pools found")
        return pools

    def get_tokens(self, blockchain):
        tokens = self.blockchain_data.get('tokens', []) + self.user_dictionaries.get(blockchain, {}).get('tokens', [])
        print(f"Getting tokens for {blockchain}: {len(tokens)} tokens found")
        return tokens

    def update_lists(self):
        blockchain = self.blockchain_var.get()
        print(f"Updating lists for blockchain: {blockchain}")
        print(f"Blockchain data: {self.blockchain_data.keys()}")
        print(f"User dictionaries: {self.user_dictionaries.keys()}")
        pools = self.get_pools(blockchain)
        tokens = self.get_tokens(blockchain)
        
        print(f"Pools: {len(pools)}")
        print(f"Tokens: {len(tokens)}")

        self.pool_combo['values'] = [pool['name'] for pool in pools]
        self.token_combo['values'] = [token['name'] for token in tokens]

        # Update Order By options based on the selected entity
        entity = self.entity_var.get()
        if entity in self.schema:
            self.order_by_combo['values'] = list(self.schema[entity]['fields'].keys())

        # Ensure the dropdowns are populated
        if pools:
            self.pool_combo.set(pools[0]['name'])
        if tokens:
            self.token_combo.set(tokens[0]['name'])

        print(f"Updated pools: {self.pool_combo['values']}")
        print(f"Updated tokens: {self.token_combo['values']}")

    def filter_lists(self, event=None):
        search_term = self.search_var.get().lower()
        blockchain = self.blockchain_var.get()
        
        pools = [pool['name'] for pool in self.get_pools(blockchain) if search_term in pool['name'].lower()]
        tokens = [token['name'] for token in self.get_tokens(blockchain) if search_term in token['name'].lower()]
        
        self.pool_combo['values'] = pools
        self.token_combo['values'] = tokens

    def add_to_favorites(self):
        address = self.address_entry.get()
        if address:
            blockchain = self.blockchain_var.get()
            if blockchain not in self.favorites:
                self.favorites[blockchain] = []
            if address not in self.favorites[blockchain]:
                self.favorites[blockchain].append(address)
                self.save_favorites()
                messagebox.showinfo("Favorites", f"Added {address} to favorites for {blockchain}")
            else:
                messagebox.showinfo("Favorites", f"{address} is already in favorites for {blockchain}")
        else:
            messagebox.showwarning("Favorites", "Please enter an address to add to favorites")

    def manage_favorites(self):
        favorites_window = tk.Toplevel(self)
        favorites_window.title("Manage Favorites")
        
        for blockchain, addresses in self.favorites.items():
            ttk.Label(favorites_window, text=blockchain).pack(anchor="w")
            for address in addresses:
                frame = ttk.Frame(favorites_window)
                frame.pack(fill="x", padx=5, pady=2)
                ttk.Label(frame, text=address).pack(side="left")
                ttk.Button(frame, text="Remove", command=lambda b=blockchain, a=address: self.remove_favorite(b, a, favorites_window)).pack(side="right")

    def remove_favorite(self, blockchain, address, window):
        self.favorites[blockchain].remove(address)
        self.save_favorites()
        window.destroy()
        self.manage_favorites()

    def upload_custom_dictionary(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    custom_dict = json.load(file)
                    blockchain = custom_dict.get("blockchain")
                    if blockchain:
                        self.user_dictionaries[blockchain] = custom_dict
                        new_file_path = os.path.join(USER_DICTIONARIES_DIR, f"{blockchain.lower()}_custom.json")
                        with open(new_file_path, 'w') as new_file:
                            json.dump(custom_dict, new_file)
                        self.blockchain_combo['values'] = self.get_blockchain_list()
                        messagebox.showinfo("Custom Dictionary", f"Successfully loaded custom dictionary for {blockchain}")
                        self.update_lists()
                    else:
                        messagebox.showerror("Custom Dictionary", "Invalid dictionary format. Missing 'blockchain' key.")
            except json.JSONDecodeError:
                messagebox.showerror("Custom Dictionary", "Invalid JSON file")
            except Exception as e:
                messagebox.showerror("Custom Dictionary", f"Error loading dictionary: {str(e)}")

    def toggle_query_options(self):
        query_type = self.query_type.get()
        if query_type == "Standard":
            self.order_by_combo.config(state="readonly")
        else:  # Unique Traders
            self.order_by_combo.config(state="disabled")

    def toggle_query_target(self):
        target = self.query_target.get()
        if target == "Pool":
            self.pool_label.grid()
            self.pool_combo.grid()
            self.token_label.grid_remove()
            self.token_combo.grid_remove()
            self.address_entry.config(state="disabled")
        elif target == "Token":
            self.pool_label.grid_remove()
            self.pool_combo.grid_remove()
            self.token_label.grid()
            self.token_combo.grid()
            self.address_entry.config(state="disabled")
        else:  # Custom
            self.pool_label.grid_remove()
            self.pool_combo.grid_remove()
            self.token_label.grid_remove()
            self.token_combo.grid_remove()
            self.address_entry.config(state="normal")
            self.address_entry.delete(0, tk.END)

    def on_query_type_change(self, event):
        selected_query_type = self.query_type.get()
        if selected_query_type == "Unique Traders Over Time":
            self.days_label.grid()
            self.days_entry.grid()
            self.interval_label.grid()
            self.interval_entry.grid()
            # Hide or disable other advanced options
            self.time_filter_var.set("")
            self.time_filter_combo.config(state="disabled")
            # Hide or disable other advanced options as needed
        else:
            self.days_label.grid_remove()
            self.days_entry.grid_remove()
            self.interval_label.grid_remove()
            self.interval_entry.grid_remove()
            # Show or enable other advanced options
            self.time_filter_combo.config(state="normal")
            # Show or enable other advanced options as needed

    def run_query(self):
        query_type = self.query_type.get()
        query_target = self.query_target.get()
        
        print(f"Running query of type: {query_type}")
        print(f"Query target: {query_target}")

        try:
            # Validate and sanitize address
            address = self.get_sanitized_address()
        except ValueError as e:
            messagebox.showerror("Invalid Address", str(e))
            return

        # Validate limit
        try:
            limit = int(self.limit_var.get())
            if limit <= 0 or limit > MAX_QUERY_LIMIT:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", f"Limit must be a positive integer not exceeding {MAX_QUERY_LIMIT}.")
            return

        try:
            if query_type == "Unique Traders Over Time":
                if not address:
                    messagebox.showerror("Invalid Input", "Please provide a pool address for Unique Traders query.")
                    return
                days = int(self.days_var.get())
                interval = int(self.interval_var.get())
                results = self.subgraph_connector.query_unique_traders(address, days, interval)
                entity = "UniqueTraders"  # Use a custom entity name for this query type
            else:
                entity = self.entity_var.get()
                fields = [field for field, var in self.field_vars.items() if var.get()]
                if not fields:
                    messagebox.showerror("Invalid Query", "Please select at least one field.")
                    return
                
                order_by = self.order_by_var.get()
                order_direction = self.order_direction.get()
                time_filter = self.time_filter_var.get()
                custom_filter = self.validate_custom_filter(self.custom_filter_var.get())

                query = self.subgraph_connector.build_query(
                    entity, fields, address, limit, order_by, order_direction,
                    time_filter=time_filter, custom_filter=custom_filter
                )
                results = self.subgraph_connector.query_subgraph(query)
            
            print(f"Query results: {results}")
            self.query_callback(entity, results)
        except Exception as e:
            error_message = f"An error occurred while querying the subgraph: {str(e)}"
            print(f"Error: {error_message}")
            self.show_error("Query Error", error_message)

    def get_sanitized_address(self):
        address = self.address_entry.get().strip()
        if not address:
            return None  # Allow empty address for queries that don't require it
        # Basic validation for Ethereum address format
        if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
            raise ValueError("Invalid Ethereum address format. It should start with '0x' followed by 40 hexadecimal characters.")
        return address

    def validate_custom_filter(self, custom_filter):
        # Implement custom filter validation logic
        # This is a basic example and should be expanded based on your specific needs
        if custom_filter:
            # Remove any potentially harmful characters
            sanitized = re.sub(r'[^\w\s:,]', '', custom_filter)
            if sanitized != custom_filter:
                raise ValueError("Invalid characters in custom filter")
        return custom_filter

    def show_error(self, title, message):
        error_window = tk.Toplevel(self)
        error_window.title(title)
        error_window.geometry("500x300")

        error_text = tk.Text(error_window, wrap=tk.WORD, padx=10, pady=10)
        error_text.pack(expand=True, fill="both")
        error_text.insert(tk.END, message)
        error_text.config(state=tk.NORMAL)  # Make it editable so users can copy the text

        scrollbar = ttk.Scrollbar(error_window, orient="vertical", command=error_text.yview)
        scrollbar.pack(side="right", fill="y")
        error_text.configure(yscrollcommand=scrollbar.set)

        copy_button = ttk.Button(error_window, text="Copy to Clipboard", command=lambda: self.copy_to_clipboard(message))
        copy_button.pack(pady=10)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()  # To make sure the clipboard is updated

    def show_help(self):
        help_window = tk.Toplevel(self)
        help_window.title("Query Panel Help")
        help_window.geometry("600x400")

        help_text = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        help_text.pack(expand=True, fill="both")

        help_content = """
        Subgraph: Select the subgraph you want to query.
        Blockchain: Choose the blockchain you're interested in.
        Entity: Select the type of data you want to query (e.g., Pool, Token, Swap).
        Fields: Choose the specific data fields you want to retrieve.
        Query Target: Select whether you're querying a specific pool, token, or using a custom address.
        Limit: Set the maximum number of results to return.
        Query Type: Choose between Standard query or Unique Traders query.
        Advanced Options:
            - Time Filter: Filter results by time range.
            - Custom Filter: Add any custom filtering conditions.
            - Order By: Select a field to sort the results by.
            - Order Direction: Choose ascending or descending order.
        Search: Filter the pools and tokens lists.
        Favorites: Save and manage frequently used addresses.
        Custom Dictionary: Upload custom data for additional blockchains or tokens.
        """

        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)

        scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=help_text.yview)
        scrollbar.pack(side="right", fill="y")
        help_text.configure(yscrollcommand=scrollbar.set)