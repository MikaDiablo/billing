# The definitions of all get commands
import click, base64
from src.client import gclient,resoto_client,opensee_client
from resoto import unlabeled
from opensee.opensee import ingest
# from bigquery.get_bigquery import get_retro_cost
from bigquery.build_bigquery import BigQuery
from gsheets.update_gsheets import GSheets
from src.utils import format_month
from src.constants import TIME_FILTER, SERVICE_RANGE, OWNER_RANGE, ENV_RANGE, BILLING_SPREADSHEET_ID


# Get retro data from bigquery
def get_data(month):
        bigquery = gclient("bigquery")
        bq = BigQuery(bigquery)
        retro = bq.get_retro_cost(month)
        return retro

@click.command("get_retro",
               help="Get retrospective billing info and save it to a csv file")
@click.option("-m", "--month", type=click.INT, help="Month from which get the retrospective")
# get_retro command by definning the month using -m flag
def get_retro(month):
        retro = get_data(month)
        return retro

@click.command("get_diff",
               help="Get the difference between Labeled and unlabeled services")
@click.option("-m", "--month", type=click.INT, help="Month from which get the retrospective")
# get_diff command by definning the month using -m flag
def get_diff(month):
        bigquery = gclient("bigquery")
        sheet = gclient("sheet")
        months = format_month(month)
        filter_time = TIME_FILTER.format(current_year_month = months["cm"], next_month = months["nm"])
        gs = GSheets(sheet)
        gs.labeled_unlabeled_diff(bigquery, SERVICE_RANGE, filter_time)


@click.command("get_unlabeled",
               help="Get the json files for the unlabeled resources")
# get_unlabeled resources in json format and saved in json file by kind
def get_unlabeled():
        client = resoto_client()
        unlabeled.forwarding_rule_unlabeled(client)
        unlabeled.buckets_unlabeled(client)
        unlabeled.disk_unlabeled(client)
        unlabeled.ip_unlabeled(client)
        unlabeled.instance_unlabeled(client)

@click.command("dump_billing",
               help="Get retrospective billing info and save it to a csv file")
# get_retro command by definning the month using -m flag
def dump_billing():
        
        bigquery = gclient("bigquery")
        bq = BigQuery(bigquery)
        dump = bq.dump_billing_dataset(["2023-12-20","2023-12-21"])
        # print(dump)
        df = bq.build_dataframe(dump)
        df.to_parquet("test.parquet")
        opensee_token =  opensee_client()
        print(opensee_token)
        ingest(opensee_token,"2023-12-21","test.parquet")
        # return dump