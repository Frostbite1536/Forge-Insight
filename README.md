# Forge Insight

## Overview

Forge Insight is a user-friendly desktop application designed for querying, visualizing, and exporting data from blockchain subgraphs, specifically tailored for the **Forge** decentralized exchange (DEX) on the **Evmos** network. This powerful tool provides users with the insights needed to analyze DEX activities, understand token metrics, and monitor user behaviors efficiently.

## Key Features

- **Multi-Subgraph Support**: Query data from multiple subgraphs on the Evmos network.
- **Data Visualization**: Create various chart types to visualize query results, including bar charts, line charts, scatter plots, and pie charts.
- **Data Export**: Export your results in multiple formats such as CSV, JSON, Excel, or directly to Google Sheets.
- **Custom Queries**: Build and customize your GraphQL queries with filters and sorting options.
- **User-Friendly Interface**: An intuitive interface designed for both novice and experienced users.
- **Plugin Management**: Extend the application's capabilities through a flexible plugin system.
- **Error Handling**: Comprehensive error handling and logging to aid in debugging and user support.

## Project Structure

```
forge-insight/
│
├── app.py                  # Main application entry point
├── config.py               # Configuration settings and constants
├── query_builder.py        # Constructs GraphQL queries
├── subgraph_connector.py   # Handles API communication
├── data_processor.py       # Processes and transforms query results
├── ui_manager.py           # Manages the main UI components
├── data_exporter.py        # Handles data export to various formats
├── auth_manager.py         # Manages user authentication
├── error_handler.py        # Centralizes error handling and logging
├── scheduler.py            # Manages scheduled queries
├── notifier.py             # Handles user notifications
├── plugin_manager.py       # Manages and loads plugins
│
├── ui/                     # UI-related modules
│   ├── query_panel.py
│   ├── results_panel.py
│   └── visualization_panel.py
│
├── utils/                  # Utility functions and helpers
│   ├── date_utils.py
│   └── string_utils.py
│
├── plugins/                # Directory for plugin modules
│
├── subgraph_schemas/       # Subgraph schemas
│   ├── forge_subgraph_schema.py
│   └── ...
│
├── tests/                  # Test directory
│   ├── test_query_builder.py
│   ├── test_subgraph_connector.py
│   └── ...
│
├── data/                   # Directory for stored data
│   ├── cache/
│   └── logs/
│
├── docs/                   # Documentation
│   ├── user_guide.md
│   └── developer_guide.md
│
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation (this file)
```

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/forge-insight.git
   cd forge-insight
   ```

2. **Create a virtual environment and activate it**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:

   ```bash
   python app.py
   ```

## Configuration

Configuration settings can be found in `config.py`. Default settings for various aspects of the application, such as API endpoints and UI preferences, can be adjusted here.

## Usage

Upon launching the application, you will be greeted with a simple and intuitive interface where you can:

- Select the desired subgraph.
- Construct queries by selecting entities and fields.
- Apply filters to refine your search.
- Visualize the results in various formats.
- Export data to your preferred format.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License. You can view the full license [here](https://creativecommons.org/licenses/by-nc/4.0/).

## Support

If you encounter any issues or have questions, please file an issue on the GitHub issue tracker. Your feedback is essential for the continuous improvement of the Forge Insight application.

---

A special thanks to all contributors and users of this tool!
