# The definitions of updates commands
from src.client import gclient,resoto_client
from resoto import unlabeled
from bigquery.build_bigquery import *
from gsheets.update_gsheets import GSheets
from src.constants import RETRO_PURPOSE_RANGE, RETRO_SAAS_RANGE, RETRO_OWNER_RANGE, OWNER_RANGE, ENV_RANGE, TIME_FILTER
from src.utils import print_waiting, print_success, print_loading, format_month

# Get retro data from bigquery
def get_data(month):
        bigquery = gclient("bigquery", cloudfuc=True)
        bq = BigQuery(bigquery)
        retro = bq.get_retro_cost(month)
        return retro

# update_retro command by definning the month using -m flag the retro data will be update into the spreadsheets
def update_gcp_retro(month):
        sheet = gclient("sheet", cloudfuc=True)
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


# update_billing command by definning the month using -m flag the billing data will be update into the spreadsheets
def update_gcp_billing(month):
    bigquery = gclient("bigquery", cloudfuc=True)
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

def get_gcp_unlabeled():
        client = resoto_client()
        unlabeled.forwarding_rule_unlabeled(client)
        unlabeled.buckets_unlabeled(client)
        unlabeled.disk_unlabeled(client)
        unlabeled.ip_unlabeled(client)
        unlabeled.instance_unlabeled(client)