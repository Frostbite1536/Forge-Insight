import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
import pandas as pd

class GoogleSheetsExporter:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self):
        self.creds = None

    def get_credentials(self, client_secret_path):
        token_file = 'token.json'
        if os.path.exists(token_file):
            self.creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(token_file, 'w') as token:
                token.write(self.creds.to_json())
        
        return self.creds

    def export_to_sheets(self, client_secret_path, sheet_id, sheet_name, data):
        creds = self.get_credentials(client_secret_path)
        service = build('sheets', 'v4', credentials=creds)
        
        # Ensure the sheet exists
        try:
            service.spreadsheets().get(spreadsheetId=sheet_id, ranges=sheet_name).execute()
        except HttpError:
            # If the sheet doesn't exist, create it
            request = {'addSheet': {'properties': {'title': sheet_name}}}
            service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={'requests': [request]}).execute()

        # Clear existing content
        range_name = f"{sheet_name}!A1:ZZ"
        service.spreadsheets().values().clear(spreadsheetId=sheet_id, range=range_name).execute()

        # Prepare the data
        sheet_data = []
        sheet_data.append(["Summary"])
        sheet_data.append(["Total Unique Traders", data.get('total_unique_traders', 'N/A')])
        sheet_data.append(["Total Swaps", data.get('total_swaps', 'N/A')])
        sheet_data.append(["Start Timestamp", data.get('start_timestamp', 'N/A')])
        sheet_data.append(["End Timestamp", data.get('end_timestamp', 'N/A')])
        sheet_data.append([])  # Empty row

        if 'interval_data' in data:
            sheet_data.append(["Interval Data"])
            interval_df = pd.DataFrame(data['interval_data'])
            sheet_data.append(interval_df.columns.tolist())
            sheet_data.extend(interval_df.values.tolist())
            sheet_data.append([])  # Empty row

        if 'processed_swaps' in data:
            sheet_data.append(["Processed Swaps"])
            swaps_df = pd.DataFrame(data['processed_swaps'])
            swaps_df['human_readable_time'] = pd.to_datetime(swaps_df['timestamp'], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
            sheet_data.append(swaps_df.columns.tolist())
            sheet_data.extend(swaps_df.values.tolist())

        # Update with new data
        body = {'values': sheet_data}
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id, 
            range=f"{sheet_name}!A1",
            valueInputOption='USER_ENTERED', 
            body=body
        ).execute()
        
        return result.get('updatedCells')

    def update_sheet(self, service, spreadsheet_id, sheet_name, data):
        try:
            # Check if the sheet exists
            service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges=sheet_name).execute()
        except HttpError:
            # If the sheet doesn't exist, create it
            request = {'addSheet': {'properties': {'title': sheet_name}}}
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': [request]}).execute()

        # Clear existing content
        range_name = f"{sheet_name}!A1:ZZ"
        service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_name).execute()

        # Update with new data
        body = {'values': data}
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, 
            range=f"{sheet_name}!A1",
            valueInputOption='USER_ENTERED', 
            body=body
        ).execute()
        
        return result.get('updatedCells')

    def clear_sheet(self, service, spreadsheet_id, sheet_name):
        try:
            service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=sheet_name
            ).execute()
        except HttpError as error:
            raise Exception(f"An error occurred while clearing the sheet: {error}")

    def create_or_update_sheet(self, client_secret_path, spreadsheet_id, sheet_name, data):
        creds = self.get_credentials(client_secret_path)
        service = build('sheets', 'v4', credentials=creds)

        try:
            # Try to clear the existing sheet
            self.clear_sheet(service, spreadsheet_id, sheet_name)
        except:
            # If clearing fails (likely because the sheet doesn't exist), create a new sheet
            request = {'addSheet': {'properties': {'title': sheet_name}}}
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': [request]}).execute()

        # Now update the sheet with new data
        return self.update_sheet(service, spreadsheet_id, sheet_name, data)