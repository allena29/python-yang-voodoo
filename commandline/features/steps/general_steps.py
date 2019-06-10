from behave import given, when, then, step
import time


@given("we wait for some poking around")
@when("we wait for some poking around")
@then("we wait for some poking around")
def step_impl(context):
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Continue after keyboard interrupt")
