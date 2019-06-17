from behave import given, when, then, step
import time
import sys
import pexpect
import time
import os


@when("we open the command line interface")
def step_impl(context):
    os.chdir(context.basedir)
    context.config_prompt = 'steg@localhost% '
    context.normal_prompt = 'steg@localhost'
    context.cli = pexpect.spawn('bash -ci ./cli', cwd=context.basedir)


@then("we should be presented with a welcome prompt containing")
def step_impl(context):
    context.cli.expect(context.text, timeout=2)


@when("we send the following commands")
def step_impl(context):
    for command in context.text.split('\n'):
        context.cli.write("%s\n" % (command))
        sys.stderr.write(command+"\r\n")
        time.sleep(0.05)
    context.cli.expect([context.normal_prompt], timeout=2)


@when("we send the following configuration commands")
def step_impl(context):
    for command in context.text.split('\n'):
        context.cli.write("%s\n" % (command))
        sys.stderr.write(command+"\r\n")
        time.sleep(0.05)
    context.cli.expect([context.config_prompt], timeout=2)


@then("we should be in configuration mode")
def step_impl(context):
    context.cli.expect([context.config_prompt])


@then("we should be in operational mode")
def step_impl(context):
    context.cli.expect([context.normal_prompt], timeout=2)
    raise ValueError(context.cli.before)


@then("the command line should have cleanly closed")
def step_impl(context):
    time.sleep(1)
    context.cli.write('sdf')
