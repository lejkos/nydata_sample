
import requests
import time
import sys
from pprint import pprint


def run_test():
    """
    A simple hacked together test function to check the functionality
    """
    username = 'tester'
    password = 'tester123456'

    print(f'[+] Showing proof of concept with testuser={username}')

    time.sleep(2)

    payload = {'username': username, 'password': password}
    url = 'http://localhost:5000/auth/get_token/'
    print(f'[+] Getting an access token from url={url} with username and password!')

    response = requests.post(url, json=payload)
    content = response.content
    status_code = response.status_code
    print(f'\n[+] Recceived response status_code={status_code}!')

    if status_code != 200:
        print(f'[-] Failed to retrieve access token. status_code={status_code}')
        print(f'[-] Response content: \n {content}')
        print('[!] PLEASE MAKE SURE YOU HAVE A RUNNING SERVER LOCALLY OR IN DOCKER!')
        sys.exit(1)

    token_json = response.json()
    token = token_json.get('access_token')
    print(f'\n[+] Using access token to query database. Token={token}')

    time.sleep(2)

    query = 'query{logs(dateFrom:"2000-01-01",dateTo:"2019-12-12") {hostIP verb path timestamp}}'

    print(f'\n[+] Making GraphQL query:  \n\n\t{query}\n')
    time.sleep(3)
    url = f'http://localhost:5000/graphql/?query={query}'

    graphql_response = requests.get(url, headers={'Authorization': f'Bearer {token}'})

    response_data = graphql_response.json()
    print('[+] Printing result...')

    time.sleep(3)
    pprint(response_data)


if __name__ == '__main__':
    run_test()
