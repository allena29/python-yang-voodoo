from behave import given, when, then, step
import sys
import pexpect
import time
import os


@when("we open the command line interface")
def step_impl(context):
    os.chdir(context.basedir)
    context.config_prompt = 'steg@localhost% '
    context.normal_prompt = 'steg@localhost> '
    context.cli = pexpect.spawn('bash -ci ./cli', cwd=context.basedir)


@then("we should be presented with a welcome prompt containing")
def step_impl(context):
    context.cli.expect(context.text, timeout=2)


@when("we send the following command")
def step_impl(context):
    for command in context.text.split('\n'):
        context.cli.write("%s\n" % (command))


@then("we should be in configuration mode")
def step_impl(context):
    context.cli.expect([context.config_prompt])


@then("we should be in operational mode")
def step_impl(context):
    context.cli.expect([context.normal_prompt])


@then("the command line should have cleanly closed")
def step_impl(context):
    time.sleep(1)
    context.cli.write('sdf')
