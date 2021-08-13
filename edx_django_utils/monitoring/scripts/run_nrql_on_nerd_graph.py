import requests
import json
import os


def run_nrql_query(query, api_key, account_id):
    """More details on this can be found at: https://developer.newrelic.com/collect-data/get-started-nerdgraph-api-explorer/"""
    graphql_url = 'https://api.newrelic.com/graphql'
    headers = {'Content-Type': 'application/json', 'API-Key': api_key}
    graphql_query = f"""{{
   actor {{
      account(id: {account_id}) {{
         nrql(query: "{query}") {{
            results
         }}
      }}
   }}
}}"""
    post_data = {'query': graphql_query.replace('\n','')}
    response = requests.post(url=graphql_url,  headers = headers, json=post_data)
    json_return = json.loads(response.content)
    try:
        query_results = json_return['data']['actor']['account']['nrql']['results']
    except:
        raise ValueError(f'NRQL response is not parsable correctly, response content: {response.content}')
    return query_results

if __name__ == '__main__':
    api_key = os.environ['NEW_RELIC_API_KEY']
    new_relic_account_id = os.environ["NEW_RELIC_ACCOUNT_ID"]
    sample_query = "SELECT count(*) from Transaction since 2 day ago"
    print(run_nrql_query(sample_query, api_key, new_relic_account_id))
