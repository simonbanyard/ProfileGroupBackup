import base64
import hashlib
import hmac
import os
import time
import uuid

import requests
from dotenv import load_dotenv

# Load API secret from a local .env file
load_dotenv()

# Setup account details
# BASE_URL: Replace xx with the region the account is hosted in
# Keys are obtained from your Mimecast account, see
# https://community.mimecast.com/s/article/Managing-API-Applications-505230018
base_url = "https://eu-api.mimecast.com"
access_key = os.getenv("ACCESS_KEY")
secret_key = os.getenv("SECRET_KEY")
app_id = os.getenv("APP_ID")
app_key = os.getenv("APP_KEY")

# Generate UUID based on RFC4122 and Date/Time based on RFC1123/2822
request_id = str(uuid.uuid4())
hdr_date = time.strftime("%a, %d %b %Y %H:%M:%S %z")


def auth(uri):
    """Generates Authorization Signature - see
    https://www.mimecast.com/tech-connect/documentation/api-overview/authorization/

    Args:
        uri (String): The endpoint URI

    Returns:
        Authorization signature as a string
    """
    # Generate Authorization
    data_to_sign = f"{hdr_date}:{request_id}:{uri}:{app_key}"
    hmac_sha1 = hmac.new(
        base64.b64decode(secret_key),
        data_to_sign.encode("utf-8"),
        digestmod=hashlib.sha1,
    ).digest()
    sig = base64.b64encode(hmac_sha1).rstrip()

    return f"MC {access_key}:{str(sig.decode())}"


def send_request(uri, body):
    """
    Sends a POST request to a selected Mimecast endpoint

    Args:
        uri (String): The endpoint URI
        body (Dict): A dictionary of the fields required - see the endpoint
        documentation for the specific endpoint.
        https://www.mimecast.com/tech-connect/documentation/

    Returns:
        JSON response from the provided endpoint
    """
    try:
        response = requests.post(
            url=base_url + uri,
            headers={
                "Authorization": auth(uri),
                "x-mc-app-id": app_id,
                "x-mc-date": hdr_date,
                "x-mc-req-id": request_id,
                "Content-Type": "application/json",
            },
            json=body,
        )
        response.raise_for_status()
        print(f"Endpoint: {uri}")
        print(f"HTTP Response: {response.status_code}, Success!")
        return response.json()

    except requests.HTTPError as err_h:
        return f"HTTP Error: {err_h}"
    except requests.exceptions.ConnectionError as err_c:
        print("Error Connecting:", err_c)
    except requests.exceptions.Timeout as err_t:
        print("Timeout Error:", err_t)
    except requests.exceptions.RequestException as err:
        print("Error:", err)
