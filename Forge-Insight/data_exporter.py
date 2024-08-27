import csv
import json
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class DataExporter:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager

    def export_to_csv(self, data, filename):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for key, value in data.items():
                writer.writerow([key])
                if isinstance(value, list) and value:
                    writer.writerow(value[0].keys())
                    for item in value:
                        writer.writerow(item.values())
                writer.writerow([])

    def export_to_json(self, data, filename):
        with open(filename, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=2)

    def export_to_excel(self, data, filename):
        with pd.ExcelWriter(filename) as writer:
            for key, value in data.items():
                if isinstance(value, list) and value:
                    df = pd.DataFrame(value)
                    df.to_excel(writer, sheet_name=key, index=False)

    def export_to_google_sheets(self, data, spreadsheet_name):
        creds = self.auth_manager.get_credentials()
        if not creds:
            raise ValueError("Not authenticated for Google Sheets")

        try:
            service = build('sheets', 'v4', credentials=creds)
            spreadsheet = {
                'properties': {
                    'title': spreadsheet_name
                }
            }
            spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
            spreadsheet_id = spreadsheet.get('spreadsheetId')

            for key, value in data.items():
                if isinstance(value, list) and value:
                    df = pd.DataFrame(value)
                    values = [df.columns.tolist()] + df.values.tolist()
                    body = {
                        'values': values
                    }
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f'{key}!A1',
                        valueInputOption='RAW',
                        body=body
                    ).execute()

            return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")