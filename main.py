# Main file for cloud functions
import functions_framework
from cloud_function.gcp_send import *


@functions_framework.http
# Send endpoint
def send(request):
    request_json = request.get_json(silent=True)

    if request_json and "content" in request_json:
        content = request_json["content"]
        destination = request_json["destination"]
    else:
        print('Missing Body request')

    if content == "billing":
        return billing_gcp_mail()
    elif content == "unlabeled" and destination == "mail":
        return unlabeled_gcp_mail()
    elif content == "unlabeled" and destination == "slack":
        return slack_gcp_unlabeled()
    else:
        return print('Wrong Message content')
 
    