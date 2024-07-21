# The utilities file
import time, os, json, datetime
import click
import datetime

# Print with cyan color
def print_loading(message):
    click.echo(click.style(f"{message}", fg='cyan'))

# Print with green color
def print_success(message):
    click.echo(click.style(f"{message}", fg='green'))

# Print with blue color
def print_waiting(message):
    click.echo(click.style(f"{message}", fg='blue'))

# Print with red color
def print_error(message):
    click.echo(click.style(f"{message}", fg='red'))

# Print in loop
def loading(message):                                 
    wait = True   
    spaces = 0                                   
    while wait == True:                                                                                           
        if (spaces<=1):                              
            print_loading(f"\b {message}")
            time.sleep(0.3)
            spaces = spaces+1
        else: 
            wait = False

# Read from Json file
def read_json_files(file_paths):
    json_data = {}
    for file_name in file_paths:
        if os.path.isfile(file_name):
            with open(file_name, 'r') as file:
                json_data[file_name] = json.load(file)
    return json_data

# check if strings contains numbers
def contains_numbers(s):
    return any(char.isdigit() for char in s)


def get_current_month():
    current_date = datetime.datetime.now()
    current_month = current_date.month
    return current_month

# Format month with different type and format and return the results in a dict.
def format_month(month):
    # Check if the month is a single digit and add a leading '0' if needed
    formatted_month = f"{month:02}"
    year = datetime.date.today().year
    cm = f'{year}-{formatted_month}'
   
    # Calculate previous month (pm) and month before the previous month (bpm)
    if formatted_month == "01":  # Handle January for previous month            
        pm = f'{year - 1}-12'
        bpm = f'{year - 1}-11'
        nmint = int(formatted_month) + 1
        nm = f'{year}-{nmint:02}'
    elif formatted_month == "12": # Handle December
        cm = f'{year - 1}-{formatted_month}'
        pmint = int(formatted_month) - 1
        pm = f'{year - 1}-{pmint:02}'
        bpmint = int(formatted_month) - 2
        bpm = f'{year - 1}-{bpmint:02}'
        nm = f'{year}-01'
    elif formatted_month == "02":
        pmint = int(formatted_month) - 1
        pm = f'{year}-{pmint:02}'
        bpm = f'{year - 1}-12'
        nmint = int(formatted_month) + 1
        nm = f'{year}-{nmint:02}'
    else: 
        pmint = int(formatted_month) - 1
        pm = f'{year}-{pmint:02}'
        bpmint = int(formatted_month) - 2
        bpm = f'{year}-{bpmint:02}'
        nmint = int(formatted_month) + 1
        nm = f'{year}-{nmint:02}' 
       
    
    # Create a dictionary with month names
    month_names = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "October",
        "11": "November",
        "12": "December"
    }

    return {
        "cm": cm,
        "pm": pm,
        "bpm": bpm, 
        "nm": nm,
        "mstr": month_names.get(formatted_month, "Invalid")
    }