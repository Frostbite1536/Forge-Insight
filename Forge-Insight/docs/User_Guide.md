# Forge Insight User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
   - [Installation](#installation)
   - [Launching the Application](#launching-the-application)
3. [User Interface Overview](#user-interface-overview)
4. [Querying Data](#querying-data)
   - [Selecting a Subgraph](#selecting-a-subgraph)
   - [Choosing Entities and Fields](#choosing-entities-and-fields)
   - [Applying Filters](#applying-filters)
   - [Setting Query Limits](#setting-query-limits)
5. [Visualizing Results](#visualizing-results)
   - [Chart Types](#chart-types)
   - [Visualizing Data](#visualizing-data)
6. [Exporting Data](#exporting-data)
   - [Export Formats](#export-formats)
   - [Exporting to Google Sheets](#exporting-to-google-sheets)
7. [Managing Favorites and Custom Dictionaries](#managing-favorites-and-custom-dictionaries)
8. [Error Handling](#error-handling)
9. [Advanced Features](#advanced-features)
   - [Plugin Management](#plugin-management)
   - [Scheduler](#scheduler)
10. [Frequently Asked Questions (FAQs)](#frequently-asked-questions-faqs)
11. [Support and Contributions](#support-and-contributions)

---

## 1. Introduction

Welcome to the Forge Insight user guide! This documentation is intended to help both beginners and advanced users navigate and utilize the features of the Forge Insight application effectively. Whether you are interested in querying blockchain data, visualizing results, or managing your preferences, this guide covers everything you need to get started.

## 2. Getting Started

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/forge-insight.git
   cd forge-insight
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Required Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Launching the Application

To launch the application, run:
```bash
python app.py
```
This will open the Forge Insight user interface.

## 3. User Interface Overview

Upon launching the application, you will see the main interface, which consists of several panels:

- **Query Panel**: Here, you can construct and submit queries.
- **Results Panel**: Displays the results of your queries.
- **Visualization Panel**: Allows you to create visual representations of your data.

The interface is designed to be intuitive, with tooltips and contextual help available for each component.

## 4. Querying Data

### Selecting a Subgraph

1. In the **Query Panel**, locate the "Select Subgraph" dropdown.
2. Choose a subgraph from the available options. The default is usually set to "Forge".

### Choosing Entities and Fields

1. After selecting the subgraph, the "Select Entity" dropdown will be populated with available entities.
2. Select an entity (e.g., Token, Pool).
3. The corresponding fields will be displayed. You can choose specific fields to include in your query.

### Applying Filters

1. You can add filters to refine your results. Filters should be in the format: `key: value`.
2. Enter custom filters in the provided field in the **Advanced Options** section.

### Setting Query Limits

1. Set a limit for the number of results returned by entering a value in the "Limit" entry box.
2. The maximum limit is defined in the application settings.

## 5. Visualizing Results

### Chart Types

Forge Insight supports several chart types for visualizing data:
- Bar Chart
- Line Chart
- Scatter Plot
- Pie Chart
- Heatmap

### Visualizing Data

1. Once you have queried data, navigate to the **Visualization Panel**.
2. Select the desired chart type from the dropdown.
3. The visualization will update based on the selected chart type and the results of your query.

## 6. Exporting Data

### Export Formats

You can export your query results in multiple formats:
- **CSV**
- **JSON**
- **Excel**
- **Google Sheets**

### Exporting to Google Sheets

1. Provide the required Sheet ID and credentials file in the **Google Sheets Configuration** section.
2. Click "Export Results" and select Google Sheets as the export format.
3. Follow the prompts to complete the export.

## 7. Managing Favorites and Custom Dictionaries

### Adding to Favorites

1. Enter an address in the designated field.
2. Click the "Add to Favorites" button to save the address for easy access later.

### Uploading Custom Dictionaries

You can upload custom dictionaries:
1. Click on "Upload Custom Dictionary".
2. Select a JSON file structured correctly with the appropriate blockchain data.

## 8. Error Handling

Forge Insight includes robust error handling:
- Errors are displayed in a user-friendly manner.
- The application logs errors for debugging and analysis.

## 9. Advanced Features

### Plugin Management

Forge Insight supports plugins:
- The **Plugin Manager** loads plugins dynamically, allowing for extended functionality.
- Users can create and add custom plugins to enhance the application's capabilities.

### Scheduler

The **Scheduler** allows users to schedule queries at specified intervals:
- Users can set up jobs to run queries automatically.

## 10. Frequently Asked Questions (FAQs)

**Q: What should I do if I encounter an error?**
- Check the logs for detailed error messages. You can access the logs in the `data/logs` directory.

**Q: How can I contribute to the project?**
- You can contribute by submitting issues, suggestions, or code via pull requests on GitHub.

## 11. Support and Contributions

If you have any questions or need further assistance, please reach out via the [GitHub Issues](https://github.com/yourusername/forge-insight/issues) page. Contributions are welcome, and we appreciate all feedback!

---

Thank you for using Forge Insight! We hope this guide helps you maximize your experience with the application.
