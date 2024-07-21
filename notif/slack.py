import logging,os
from slack_sdk.errors import SlackApiError
from src.utils import read_json_files
from src.constants import CHANNEL_ID
from src.client import slack_client

def send_message(message):
    
    client = slack_client()

    try:
        # Call the conversations.list method using the WebClient
        result = client.chat_postMessage(
            channel=CHANNEL_ID,
            text=message
        )
        # print(result)
    except SlackApiError as e:
        print(f"Error: {e}")

def create_unlabeled_tables(file_name, data):

    table_slack = ""

    list_slack = f"*_{file_name.split('/')[-1].replace('.json', '')} :_*\n"

    for n, row in data.items():
        main_point = f" {int(n)+1}.  `{row[list(row.keys())[0]]}`\n"
        sub_points = "".join(f"```{key}: {value}```\n" for key, value in row.items() if key != list(row.keys())[0])
        row_values = f"{main_point}{sub_points}\n"
        list_slack += row_values

    table_slack +=  f"{list_slack}\n"

    print(table_slack)

    return send_message(table_slack)   

def get_resources_from_json():
         # Define the JSON file names
    json_file_names = ["instances", "buckets", "volumes", "ips", "forwarding_rule"]
    json_file_path = []
    for name in json_file_names:
        json_file_path += [f'/tmp/unlabeled/{name}.json']
    # Read JSON data from files
    json_data = read_json_files(json_file_path)
    for file_name, data in json_data.items():
         create_unlabeled_tables(file_name, data)

def construct_unlabeled():
    message = "Hello <!subteam^S03HB8QQK62> team, :rotating_light: \nThis is an alert message for the unlabeled resources please check the lists below:"
    # send_message(message)
    get_resources_from_json()         