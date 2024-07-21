# The definitions of all send commands
import click, base64
from src.client import gclient
from notif.gmail import create_unlabeled_mail, create_monthly_mail
from notif.slack import construct_unlabeled
from commands.update import update_retro
from src.utils import print_waiting

@click.command("send_billing",
               help="Send billing report with the latest updated information in the spreadsheet")
@click.option("-m", "--month", type=click.INT, help="Month from which get the retrospective")
@click.pass_context
# Send billing report with the latest updated information in the spreadsheet
def send_billing(ctx, month):
    client = gclient("gmail")
    sheet = gclient("sheet")
    ctx.forward(update_retro)
    print_waiting("Creating Mail")
    create_monthly_mail(month, client, sheet)

@click.command("send_unlabeled",
               help="Send a notification email with the unlabeled resources")
# Send a notification email with the unlabeled resources
def send_unlabeled():
    client = gclient("gmail")
    print_waiting("Creating Mail")
    create_unlabeled_mail(client)

@click.command("slack_unlabeled",
               help="Send a notification email with the unlabeled resources")
# Send a notification email with the unlabeled resources
def slack_unlabeled():
    construct_unlabeled()