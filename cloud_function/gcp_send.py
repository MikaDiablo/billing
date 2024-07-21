# The definitions of all send commands

from src.client import gclient
from notif.gmail import create_unlabeled_mail, create_monthly_mail
from notif.slack import construct_unlabeled
from cloud_function.gcp_update import *
from src.utils import print_waiting, get_current_month

def billing_gcp_mail():
    client = gclient("gmail", cloudfuc=True)
    sheet = gclient("sheet", cloudfuc=True)
    month = get_current_month()
    update_gcp_retro(month)
    update_gcp_billing(month)
    print_waiting("Creating Mail")
    create_monthly_mail(month, client, sheet)
    return "Message Sent"

def unlabeled_gcp_mail():
    client = gclient("gmail", cloudfuc=True)
    get_gcp_unlabeled()
    print_waiting("Creating Mail")
    create_unlabeled_mail(client)
    return "Message Sent"

# Send a notification email with the unlabeled resources
def slack_gcp_unlabeled():
    get_gcp_unlabeled()
    construct_unlabeled()
    return "Message Sent"