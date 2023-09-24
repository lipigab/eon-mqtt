import os
import time
import json
import requests
import paho.mqtt.publish as publish

# ... (other imports and constants) ...

def main():
    # ... (previous code) ...

    session = requests.Session()

    # Set verify=False to skip SSL certificate verification
    response = session.get(ACCOUNT_URL, verify=False)
    if response.status_code != 200:
        raise Exception(
            f"Failed to get access token, HTTP status code={response.status_code}")

    index_content = BeautifulSoup(response.content, "html.parser")

    log(f"Obtain a verification token")
    request_verification_token = get_verificationtoken(index_content)

    body_data = {
        "UserName": eon_username,
        "Password": eon_password,
        "__RequestVerificationToken": request_verification_token
    }

    header = {"Content-Type": "application/x-www-form-urlencoded"}
    log(f"Login into E.ON portal")

    # Set verify=False to skip SSL certificate verification
    response = session.post(ACCOUNT_URL, data=body_data,
                            headers=header, verify=False)
    if response.status_code != 200:
        raise Exception(
            f"Failed to login, HTTP status code={response.status_code}")

    # ... (rest of the code) ...

if __name__ == '__main__':
    main()
