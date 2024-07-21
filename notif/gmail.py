import base64, io
import matplotlib.pyplot as plt
import pandas as pd
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.utils import read_json_files, contains_numbers, format_month, print_success, print_error
from gsheets.update_gsheets import GSheets
from requests import HTTPError
from src.constants import RETRO_PURPOSE_RANGE, RETRO_SAAS_RANGE, RETRO_OWNER_RANGE, OWNER_RANGE, ENV_RANGE, BILLING_SPREADSHEET_ID, MAIL_LIST

tables_list = {
            "Saas Env": RETRO_SAAS_RANGE,
            "Owner Internal Cost": RETRO_OWNER_RANGE,
            "Owner/Purpose": RETRO_PURPOSE_RANGE,
            "Env/Owner Cost": ENV_RANGE             
            }

# Construct the message and send it
def construct_mail(client, message):
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    try:
        message = (client.users().messages().send(userId="me", body=create_message).execute())
        print_success(F'Message Sent. Message Id: {message["id"]}')
    except HTTPError as error:
        print_error(F'An error occurred: {error}')
        message = None

# Create the unlabeled mail withe the body message and tables.
def create_unlabeled_mail(client):
    message = MIMEMultipart()  # Use MIMEMultipart to compose a more complex email
    
    # Add a paragraph to the email body
    body_text = "Hello @DevOps team,\n\nThis mail is auto-generated and send from the billing tool.\nYou can find below the list of unlabeled resources:"


    # Add the body text to the email
    message.attach(MIMEText(body_text))

    # Define the JSON file names
    json_file_names = ["instances", "buckets", "volumes", "ips", "forwarding_rule"]
    json_file_path = []
    for name in json_file_names:
        json_file_path += [f'/tmp/unlabeled/{name}.json']
    # Read JSON data from files
    json_data = read_json_files(json_file_path)

    for file_name, data in json_data.items():
            # Create an HTML table for each JSON file
            table_html = f"<h2>{file_name.split('/')[-1].replace('.json', '')}</h2>"
            table_html += "<table border='1'><tr>"
            table_html += "".join(f"<th>{key}</th>" for key in data["0"].keys())  # Assuming keys are the same for all items
            table_html += "</tr>"

            for _, row in data.items():
                table_html += "<tr>"
                table_html += "".join(f"<td>{value}</td>" for value in row.values())
                table_html += "</tr>"

            table_html += "</table>"

            # Add the table to the email body
            table_message = MIMEText(table_html, 'html')
            message.attach(table_message)
    
    message['to'] = 'devops@opensee.io, guillaume.coffin@gmail.com'
    message['subject'] = 'Unlabeled resources'

    return construct_mail(client, message)

# Function to create a chart based on the data in the table
def create_chart(table_name, table_data, type):
   # Extract months and categories from the input list
    if len(table_data[1]) > 0 and table_data[1][0] == "Owner":
        months = table_data[0][2:]
        categories = table_data[1]
        columns = categories + months
        data = table_data[2:]
        xlabel = 'Months'
        ylabel = 'Costs'
    elif table_data[0][0] == "Month":
        months = table_data[0][1:]
        categories = ["Owner"]  # Assigning a list with "Owner" as a single element
        columns = categories + months
        data = table_data[1:]
        xlabel = 'Months'
        ylabel = 'Costs'
    else:
        months = table_data[0][2:]
        categories = ["Env","Owner"]  # Assigning a list with "Env" as a single element
        columns = categories + months
        data = table_data[1:]
        ylabel = ''

    # Create a DataFrame excluding the first two rows which contain headers
    df = pd.DataFrame(data, columns=columns)

    # Set 'Month' as the index and select only columns for 'Category'
    chart_data = df.set_index(categories)
    chart_data.columns = months  
    chart_data=chart_data.apply((lambda x: x.str.replace(',', '.').astype(float)))
  
    # Plotting the chart
    
    if type == 'pie':
        grouped = chart_data.groupby("Owner").sum()
        grouped.plot(kind=type, y=months[0], subplots=True, autopct='%1.1f%%', startangle=275, legend=False, ylabel=ylabel )
    else:
        chart_data.T.plot(kind=type)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    
    plt.title(f'{table_name}')    
    

    # Convert plot to a base64-encoded image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    chart_image = buffer.read()
    plt.close()

    return chart_image

# Create the billing tables for the billing mail.
def create_billing_tables(table_name, sheet_values):

    message = MIMEMultipart()
    # table_html = '<div>'
    table_html = f'<h2>{table_name}</h2>'
    table_html += f'<img src="cid:{str(hash(table_name))}"; style="float: right; margin-left: 100px; margin-right: 20px">'
    table_html += "<table class=striped style='border: 3px solid #000; text-align: center;'><thead><tr>"

    column_totals = [0] * len(sheet_values[0])

    for i, key in enumerate(sheet_values[0]):
        table_html += f"<th title='Field #{i + 1}' style='border: 2px solid #000;'>{key}</th>"
    
    table_html += "</tr></thead><tbody>"

    for row in sheet_values[1:]:
        table_html += "<tr>"
        for i, value in enumerate(row):
            if i > 0 and contains_numbers(value):
                column_totals[i] += round(float(value.replace(',', '.')),2) if value else 0
                table_html += f"<td style='border: 1px solid #000;'>{round(float(value.replace(',', '.')),2)}</td>"
            else:
                table_html += f"<td style='border: 1px solid #000;'>{value}</td>"

        table_html += "</tr>"

    table_html += "<tr>"
    for i, total in enumerate(column_totals):
        if i == 0:
            table_html += "<td style='border: 2px solid #000;'><strong>Total</strong></td>"
        else:
            table_html += f"<td style='border: 2px solid #000;'><strong>{total:,.1f}</strong></td>"
    table_html += "</tr></tbody></table>"
    
    table_message = MIMEText(table_html, 'html')
    message.attach(table_message)

    if table_name != "Env/Owner Cost":
        chart_image = create_chart(table_name, sheet_values, 'line')
    else:
        chart_image = create_chart(table_name, sheet_values, 'pie')  
    
    chart = MIMEImage(chart_image)
    chart.add_header('Content-ID', f'<{str(hash(table_name))}>')
    message.attach(chart)

    return message

# Create the billing mail and add the body message and thr tables.
def create_monthly_mail(month, client, sheet):
    months = format_month(month)

    message = MIMEMultipart()  # Use MIMEMultipart to compose a more complex email
    
    # Add a paragraph to the email body
    body_text = f"""
Good Morning Everyone, 

You can find our monthly costing report for {months["mstr"]} that will be discussed over our meeting.
You can have more detailed information on the grafana Cloud Cost billing via this link: https://grafana.opensee.team/d/zziWi1t7k/google-cloud-billing-costs?orgId=1&from=now-1M%2FM&to=now-1M%2FM

"""


    # Add the body text to the email
    message.attach(MIMEText(body_text))

    gs = GSheets(sheet)
    for key, value in tables_list.items():
        owner_values = gs.get_data_from_sheet(value,BILLING_SPREADSHEET_ID)
        if value == ENV_RANGE:
            new = [['Env', 'Owner', 'Cost']]
            for env, owner, cost in owner_values[1:]:
                if float(cost.replace(',', '.')) > 10:
                    new.append([env,owner,cost])
            owner_values = new        
        table_owner = create_billing_tables(key,owner_values)
        message.attach(table_owner)
       

    message['to'] = f'{MAIL_LIST}, eric.tea@opensee.io'
    message['subject'] = f'{months["mstr"]} Monthly Cost'

    return construct_mail(client, message)
