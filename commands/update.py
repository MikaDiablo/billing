# The definitions of updates commands
import click
from src.client import gclient
from bigquery.build_bigquery import *
# from bigquery.get_bigquery import get_cost_by_env, get_cost_by_owner, get_labels_env
from commands.get import get_data
from gsheets.update_gsheets import GSheets
from src.constants import RETRO_PURPOSE_RANGE, RETRO_SAAS_RANGE, RETRO_OWNER_RANGE, OWNER_RANGE, ENV_RANGE, TIME_FILTER, LABEL_RANGE, LABEL_SPREADSHEET_ID
from src.utils import print_waiting, print_success, print_loading, format_month

@click.command("update_retro",
               help="Update retrospective billing info to google sheets")
@click.option("-m", "--month", type=click.INT, help="Month from which get the retrospective")
# update_retro command by definning the month using -m flag the retro data will be update into the spreadsheets
def update_retro(month):
        sheet = gclient("sheet")
        print_loading(f"Getting retrospective data for month {month} ")
        retro = get_data(month)
        print_success("retrospective data saved to a csv file")
        print_waiting("Preparing report to be pushed")
        months = format_month(month)
        retro_owner_cost = get_report(retro[retro.env_purpose!='saas'], [f"{months['bpm']}", f"{months['pm']}",f"{months['cm']}"], 'env_owner')
        retro_purpose_cost = get_report(retro[retro.env_purpose!='saas'], [f"{months['bpm']}", f"{months['pm']}",f"{months['cm']}"], 'env_owner', 'env_purpose')
        retro_saas_cost = get_report(retro[retro.env_purpose=='saas'], [f"{months['bpm']}", f"{months['pm']}",f"{months['cm']}"], 'env_owner', 'env_customer')
        print_success("Retrospective report is ready to be pushed")
        print_waiting("Pushing data to google sheets")
        gs = GSheets(sheet)
        gs.update_retro_to_sheet(retro_owner_cost, RETRO_OWNER_RANGE)
        gs.update_retro_to_sheet(retro_purpose_cost, RETRO_PURPOSE_RANGE)
        gs.update_retro_to_sheet(retro_saas_cost, RETRO_SAAS_RANGE)
        print_success("Retrospective report is ready on your google sheets")

@click.command("update_billing", help="Update Billing information into sheets")
@click.option("-m", "--month", type=click.INT, help="Month from which get the retrospective")
# update_billing command by definning the month using -m flag the billing data will be update into the spreadsheets
def update_billing(month):
    bigquery = gclient("bigquery")
    sheet = gclient("sheet")
    months = format_month(month)
    filter_time = TIME_FILTER.format(current_year_month = months["cm"], next_month = months["nm"])
    print_loading("Getting owners data")
    bq = BigQuery(bigquery)
    owners = bq.get_cost_by_owner(filter_time)
    gs = GSheets(sheet)
    print_waiting("Pushing owners data to google sheets")
    gs.create_dataset(owners, OWNER_RANGE)
    print_loading("Getting env data")
    envs = bq.get_cost_by_env(filter_time)
    print_waiting("Pushing env data to google sheets")
    gs.create_dataset(envs, ENV_RANGE)

@click.command("update_labels", help="Update labels env and owner into enc owner google sheets")
# update_labels command will get labels from BigQuery and will be update into the spreadsheets
def update_labels():
    bigquery = gclient("bigquery")
    sheet = gclient("sheet")
    gs = GSheets(sheet)
    sheet_values = gs.get_data_from_sheet(LABEL_RANGE,LABEL_SPREADSHEET_ID)
    if not sheet_values:
        print('No data found.')
    bq = BigQuery(bigquery)
    lines = bq.get_labels_env()
    gs.update_labels_into_sheet(sheet_values, lines)