import os, subprocess
import click
from src.constants import PROJECT_ID, ENV_SECRET_LIST, FUNC_LABELS

# Build the Cloud Function.
def deploy_cloud_function(function_name, runtime, source_file):
  
  command = ["gcloud", "functions", "deploy", function_name, "--runtime", runtime, "--source", source_file, "--trigger-http", "--entry-point=send", "--update-labels", FUNC_LABELS]

  # Set the secrets as environment variables.
  for env_var, secret in ENV_SECRET_LIST.items():
    command += ["--set-secrets", f"{env_var}=projects/{PROJECT_ID}/secrets/{secret}:1"]

  # Deploy the Cloud Function.
  subprocess.run(command)

# Create a temporary directory in the current directory
def create_source_dir():

    tmp_dir = os.path.join(os.getcwd(), "cloud_function_deployment")
    subprocess.run(["mkdir", "-p", tmp_dir])

    # Copy your source code files to the temporary directory
    source_dirs = ["src", "resoto", "gsheets", "bigquery", "notif", "cloud_function", "main.py", "requirements.txt"]
    for dir in source_dirs:
        subprocess.run(["cp", "-r", os.path.join(os.getcwd(), dir), tmp_dir])

    return tmp_dir

@click.command("deploy",
               help="deploy the billing tool to the cloud function")
# Deploy cloud function command
def deploy():
    tmp_dir = create_source_dir()
    deploy_cloud_function('billing-function', 'python311', tmp_dir)
    subprocess.run(["rm", "-r", tmp_dir])

