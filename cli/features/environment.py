import os
import subprocess
import shutil
import tempfile
import time


def before_all(context):
    context.basedir = os.getcwd()
    context.cli = None
    context.cli_last_result = []


def after_scenario(context, scenario):
    if context.cli:
        print('Closing CLI Client')
        context.cli.terminate(force=True)
