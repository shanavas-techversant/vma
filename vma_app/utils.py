import urllib3
import requests

from requests.exceptions import ConnectionError
from serializer import deserialize

SCHEMA_ROUTE = "/api/get-schema"
# TODO get from config
CLIENT_CERT = "certs/client.pem"

# for dev only
urllib3.disable_warnings()


def get_metadata_from_parent(base_url):
    try:
        resp = requests.get(base_url + SCHEMA_ROUTE, cert=CLIENT_CERT, verify=False)
        schema = resp.json()
        return deserialize(schema["schema"])
    except ConnectionError as e:
        raise RuntimeError(f"Could not reach parent at {base_url}")
