#!/usr/bin/python

import os
import time
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup

# from dotenv import load_dotenv

DOCUMENTATION = '''
---

'''

result = dict(message='')
__FILE = Path(__file__)
BASE_URL = 'https://energia.eon-hungaria.hu/W1000/'
ACCOUNT_URL = f'{BASE_URL}Account/Login'
PROFILE_DATA_URL = f'{BASE_URL}ProfileData/ProfileData'


def get_verificationtoken(content):
    try:
        token = content.find('input', {'name': '__RequestVerificationToken'})
        return token.get('value')
    except Exception as ex:
        raise Exception(
            f"Unable to get verification token from the following content: {content}")


def main():
    # load_dotenv()
    eon_username = os.getenv('EON_USER')
    eon_password = os.getenv('EON_PASSWORD')

    session = requests.Session()
    response = session.get(ACCOUNT_URL, verify=True)
    if response.status_code != 200:
        raise Exception(
            f"Failed to get access token, HTTP status code={response.status_code}")

    index_content = BeautifulSoup(response.content, "html.parser")

    print(f"Obtain a verification token")
    request_verification_token = get_verificationtoken(index_content)

    body_data = {
        "UserName": eon_username,
        "Password": eon_password,
        "__RequestVerificationToken": request_verification_token
    }

    header = {"Content-Type": "application/x-www-form-urlencoded"}
    print(f"Login into E.ON portal")
    response = session.post(ACCOUNT_URL, data=body_data,
                            headers=header, verify=True)
    if response.status_code != 200:
        raise Exception(
            f"Failed to login, HTTP status code={response.status_code}")

    reportId = os.getenv('EON_REPORT_ID')
    since = os.getenv('SINCE')
    until = os.getenv('UNTIL')
    hyphen = os.getenv('EON_HYPHEN')

    if not since:
        since = (datetime.now() + timedelta(days=-1)).strftime('%Y-%m-%d')
    if not until:
        until = (datetime.now() + timedelta(days=-0)).strftime('%Y-%m-%d')

    params = {
        "page": 1,
        "perPage": 2,
        "reportId": reportId,
        "since": since,
        "until": until,
        "-": hyphen
    }

    print(f"Retrieve data from E.ON")
    data_response = session.get(PROFILE_DATA_URL, params=params)
    if data_response.status_code != 200:
        raise Exception(
            f"Failed to retrieve data, HTTP status code={data_response.status_code}")
    json_eon_response = data_response.json()

    print(json_eon_response)

    data = json.dumps({
        "import_time": json_eon_response[0]['data'][0]['time'],
        "import_value": json_eon_response[0]['data'][0]['value'],
        "export_time": json_eon_response[1]['data'][0]['time'],
        "export_value": json_eon_response[1]['data'][0]['value']
    })

    
    messages = []
    mqtt_msg = {
        'topic': mqtt_topic,
        'payload': data,
        'retain': True
    }
    messages.append(mqtt_msg)
    messages.append({'topic': f'{mqtt_topic}/availability',
                    'payload': 'Online', 'retain': True})

    mqtt_client = get_mqtt_client()
    mqtt_client.publish_multiple(messages)
    log(messages)


if __name__ == '__main__':
    main()
