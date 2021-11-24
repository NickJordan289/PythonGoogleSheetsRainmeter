from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-S', '--sid', dest='sid',
                    help='Google sheet SPREADSHEET_ID')
parser.add_argument('-R', '--range', dest='range',
                    help='Google sheet table range')
parser.add_argument('-H', '--header', dest='header',
                    help='Google sheet header to get total from')
args = parser.parse_args()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID, range and header of the spreadsheet / column.
SAMPLE_SPREADSHEET_ID = args.sid
SAMPLE_RANGE_NAME = args.range
SAMPLE_HEADER_NAME = args.header


def main():
    service = build('sheets', 'v4', credentials=get_creds())
    df = get_table(service)
    if df is not None:
        profit = df[SAMPLE_HEADER_NAME].tail(
            1).values[0]  # Get value from total row
        print(profit)  # Output to Rainmeter


def get_table(service):
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')  # Output to Rainmeter
        return None
    else:
        # Get data from google sheet and convert to pandas dataframe
        # Convert top row to column names
        df = pd.DataFrame.from_records(values)
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header
        return df


def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


if __name__ == '__main__':
    main()
