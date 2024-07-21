# The clients configuration for google, spreadsheet and bigquery
from googleapiclient.discovery import build
from google.cloud import bigquery
from google.oauth2 import service_account
from resotoclient import ResotoClient
from slack_sdk import WebClient
from src.constants import SCOPES, SCOPES_MAIL, OPENSEE_URL
import os, requests, json
     
# Google spreadsheet client
def sheet_client(path):
    credentials = service_account.Credentials.from_service_account_file(path, scopes= SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    return sheet

# Google BigQuery Client
def bigquery_client(path):
    credentials = service_account.Credentials.from_service_account_file(path, scopes= SCOPES)
    big_client = bigquery.Client(project='opensee-ci', credentials=credentials)
    return big_client

# Google Mail Client
def gmail_client(path):
    credentials = service_account.Credentials.from_service_account_file(path, scopes= SCOPES_MAIL)
    # Delegate the credentials to the user you want to impersonate
    delegated_credentials = credentials.with_subject('billing@opensee.io')
    gmail_client = build('gmail', 'v1', credentials=delegated_credentials)
    return gmail_client

# The google clients
def gclient(client, cloudfuc=None):
    if cloudfuc:
        path = "/api/secrets/billing_google_application_credentials"
    else:
        path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if client == "bigquery":
        return bigquery_client(path)
    elif client == "sheet":
        return sheet_client(path)
    elif client == "gmail":
        return gmail_client(path)

# Resoto client
def resoto_client():
    client = ResotoClient(url="https://resoto.opensee.team", psk=os.environ.get('RESOTO_PSK'), verify=False)
    return client

# Slack client
def slack_client():
    # WebClient instantiates a client that can call API methods
    client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
    return client

def opensee_client():
    url = f'{OPENSEE_URL}/login'
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "identifier": "admin",
        "password": "Welcome?"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        response_data = response.json()
    else:
        return f"Request failed with status code {response.status_code}"

    return response_data['token']