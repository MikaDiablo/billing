# The constants file
import os

SCOPES = ["https://www.googleapis.com/auth/bigquery", 
          "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive.readonly",
          "https://www.googleapis.com/auth/cloud-platform",
          "https://www.googleapis.com/auth/cloud-platform.read-only",]

SCOPES_MAIL = [
          "https://mail.google.com/",
          "https://www.googleapis.com/auth/gmail.send",]


TIME_FILTER = 'DATE(_PARTITIONTIME) >= "{current_year_month}-01" and  DATE(_PARTITIONTIME) < "{next_month}-01"'

BILLING_SPREADSHEET_ID = '1qX0vy5swTlkGYWhxoJ98-Me0mZ9WXkGYD7k_OFDK7-8'
LABEL_SPREADSHEET_ID = '1B7CZYrLNFXHz0pN-CJV5Zpk8F0L-PLMrZHUUB4r5LdU'
LABEL_RANGE = 'A1:H1000'
OWNER_RANGE = 'automate-billing!A1:B1000'
ENV_RANGE = 'automate-billing!D1:F1000'
SERVICE_RANGE = 'automate-billing!H1:L1000'
RETRO_OWNER_RANGE = 'automate-billing!M1:P15'
RETRO_SAAS_RANGE = 'automate-billing!R1:V19'
RETRO_PURPOSE_RANGE = 'automate-billing!M21:Q60'
BILLING_DATASET = 'opensee-ci.billing_export.gcp_billing_export_resource_v1_011362_37C412_FD7D09'
MAIL_LIST = 'cloud-billing@opensee.io'
CHANNEL_ID = 'C062JL2NR19'
PROJECT_ID = "opensee-ci"
ENV_SECRET_LIST = {
    "/api/secrets/billing_google_application_credentials": "billing_google_application_credentials",
    "RESOTO_PSK": "billing_resoto_psk",
    "SLACK_BOT_TOKEN": "billing_slack_bot_token"
}
FUNC_LABELS = "used_by=devops,purpose=saas"
OPENSEE_URL = "http://ui-dev-test.opensee.team"