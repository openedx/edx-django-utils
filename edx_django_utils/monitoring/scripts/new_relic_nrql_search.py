"""
This script takes a regex to search through the NRQL of New Relic alert policies
and New dashboards.

For help::

    python edx_django_utils/monitoring/scripts/new_relic_nrql_search.py --help

"""
import os
import re

import click
import requests


@click.command()
@click.option(
    '--regex',
    required=True,
    help="The regex to use to search NRQL in alert policies and dashboards.",
)
@click.option(
    '--policy_id',
    type=int,
    multiple=True,
    help="Optionally provide a specific policy id to check. Multiple can be supplied.",
)
@click.option(
    '--dashboard_id',
    type=int,
    multiple=True,
    help="Optionally provide a specific dashboard id to check. Multiple can be supplied.",
)
def main(regex, policy_id, dashboard_id):
    """
    Search NRQL in New Relic alert policies and dashboards using regex.

    Example usage:

        new_relic_nrql_search.py --regex tnl

    Note: The search ignores case since NRQL is case insensitive.

    Pre-requisite, set the following environment variable (in a safe way):

    NEW_RELIC_API_KEY=XXXXXXX

    See https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/#user-api-key for details
    on setting an API key.

    To skip alert policies or dashboards, just use a non-existent id, like --policy_id 0 or --dashboard_id 0.

    WARNING: NRQL Baseline alert conditions can't be searched. See
    https://docs.newrelic.com/docs/alerts-applied-intelligence/new-relic-alerts/rest-api-alerts/rest-api-calls-alerts/#excluded
    """
    # Set environment variables
    api_key = os.environ['NEW_RELIC_API_KEY']
    headers = {"X-Api-Key": api_key}
    compiled_regex = re.compile(regex)

    audit_alert_policies(compiled_regex, headers, policy_id)
    print()
    audit_dashboards(compiled_regex, dashboard_id, headers)
    print(flush=True)


def audit_alert_policies(regex, headers, policy_id):
    """
    Searches New Relic alert policy NRQL using the regex argument.

    Arguments:
        regex (re.Pattern): compiled regex used to compare against NRQL
        policy_id (tuple): optional tuple of policy ids supplied from the command-line.
        headers (dict): headers required to make http requests to New Relic
    """
    policies = []
    page = 1
    while True:
        response = requests.get(
            'https://api.newrelic.com/v2/alerts_policies.json',
            headers=headers,
            params={'page': page},
        )
        response.raise_for_status()  # could be an error response
        response_data = response.json()
        if not response_data['policies']:
            break
        policies += response_data['policies']
        page += 1
    # Note: policy_id is an optional tuple of policy ids supplied from the command-line.
    if policy_id:
        policies = [policy for policy in policies if policy['id'] in policy_id]
    print(f"Searching for regex {regex.pattern} in {len(policies)} alert policies...")
    policy_ids_printed = {}
    for policy in policies:
        print('.', end='', flush=True)

        # get the (static) NRQL alert conditions from the alert policy
        response = requests.get(
            'https://api.newrelic.com/v2/alerts_nrql_conditions.json',
            headers=headers,
            params={'policy_id': policy['id']},
        )
        response.raise_for_status()  # could be an error response
        response_data = response.json()

        for nrql_condition in response_data['nrql_conditions']:
            nrql_query = nrql_condition['nrql']['query']
            if regex.search(nrql_query, re.IGNORECASE):

                # Print the alert policy header for the first alert condition matched
                if policy['id'] not in policy_ids_printed:
                    policy_ids_printed[policy['id']] = True
                    print('\n')
                    print(f"Found in {policy['id']}: {policy['name']}:")
                    print('')

                # Print the alert condition that matched
                print(f"- {nrql_condition['name']}: {nrql_query}")

    if policy_ids_printed:
        command_line = ''
        for policy_id in policy_ids_printed.keys():
            command_line += f'--policy_id {policy_id} '
        print("\n\nRun again with found policies: {}".format(command_line))
    else:
        print("\n\nNo alert policies matched.")

    print(
        "\nWARNING: NRQL Baseline alert conditions can't be searched. See "
        "https://docs.newrelic.com/docs/alerts-applied-intelligence/new-relic-alerts/rest-api-alerts/"
        "rest-api-calls-alerts/#excluded"
    )


def audit_dashboards(regex, dashboard_id, headers):
    """
    Searches New Relic alert policy NRQL using the regex argument.

    Arguments:
        regex (re.Pattern): compiled regex used to compare against NRQL
        dashboard_id (tuple): optional tuple of dashboard ids supplied from the command-line.
        headers (dict): headers required to make http requests to New Relic
    """
    # load details of all dashboards
    dashboards = []
    page = 1
    while True:
        response = requests.get(
            'https://api.newrelic.com/v2/dashboards.json',
            headers=headers,
            params={'page': page},
        )
        response.raise_for_status()  # could be an error response
        response_data = response.json()
        if not response_data['dashboards']:
            break
        dashboards += response_data['dashboards']
        page += 1
    # Note: dashboard_id is an optional tuple of dashboard ids supplied from the command-line.
    if dashboard_id:
        dashboards = [dashboard for dashboard in dashboards if dashboard['id'] in dashboard_id]
    print(f"Searching for regex {regex.pattern} in {len(dashboards)} dashboards...")
    dashboard_ids_printed = {}
    for dashboard in dashboards:
        print('.', end='', flush=True)

        # get the dashboard details
        response = requests.get(
            f"https://api.newrelic.com/v2/dashboards/{dashboard['id']}.json",
            headers=headers,
        )
        response.raise_for_status()  # could be an error response
        response_data = response.json()

        for widget in response_data['dashboard']['widgets']:
            for data in widget['data']:

                if 'nrql' not in data:
                    continue

                nrql_query = data['nrql']
                if regex.search(nrql_query, re.IGNORECASE):

                    # Print the dashboard header for the first widget nrql that matches
                    if dashboard['id'] not in dashboard_ids_printed:
                        dashboard_ids_printed[dashboard['id']] = True
                        print('\n')
                        print(f"Found in {dashboard['id']}: {dashboard['title']}:")
                        print('')

                    # Print the widget NRQL that matches
                    print(f"- {widget['presentation']['title']}: {nrql_query}")

    if dashboard_ids_printed:
        command_line = ''
        for dashboard_id in dashboard_ids_printed.keys():
            command_line += f'--dashboard_id {dashboard_id} '
        print("\n\nRun again with found dashboards: {}".format(command_line))
    else:
        print("\n\nNo dashboards found that match.")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
