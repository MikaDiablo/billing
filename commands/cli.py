# The place to add each command
import click
from commands.update import *
from commands.get import *
from commands.send import *
from commands.deploy import deploy

@click.group()
@click.version_option("0.1.0", prog_name="Billing")
def cli():
    pass

cli.add_command(update_labels)
cli.add_command(update_retro)
cli.add_command(update_billing)
cli.add_command(get_retro)
cli.add_command(get_diff)
cli.add_command(get_unlabeled)
cli.add_command(send_billing)
cli.add_command(send_unlabeled)
cli.add_command(slack_unlabeled)
cli.add_command(deploy)
cli.add_command(dump_billing)