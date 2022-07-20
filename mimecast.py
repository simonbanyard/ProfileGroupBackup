import base64
import hashlib
import hmac
import json
import time
import uuid
from configparser import ConfigParser

import requests

config = ConfigParser()
config.read("secrets.ini")

# Setup account details
# BASE_URL: Replace xx with the region the account is hosted in
# Keys are obtained from your Mimecast account, see
# https://community.mimecast.com/s/article/Managing-API-Applications-505230018
base_url = "https://eu-api.mimecast.com"
access_key = config["mimecast"]["access_key"]
secret_key = config["mimecast"]["secret_key"]
app_id = config["mimecast"]["app_id"]
app_key = config["mimecast"]["app_key"]

# Generate UUID based on RFC4122 and Date/Time based on RFC1123/2822
request_id = str(uuid.uuid4())
hdr_date = time.strftime("%a, %d %b %Y %H:%M:%S %z")


def auth(uri):
    """
    Create Authorization Signature - see
    https://www.mimecast.com/tech-connect/documentation/api-overview/authorization/
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
    """Send Request"""
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
            data=body,
        )
        response.raise_for_status()
        print(f"Endpoint: {uri}")
        print(f"HTTP Response: {response.status_code}, Success!")
        return json.loads(response.content)

    except requests.HTTPError as err_h:
        return f"HTTP Error: {err_h}"
