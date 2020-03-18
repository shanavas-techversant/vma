import requests

from requests.exceptions import ConnectionError
from serializer import deserialize
from constants import SCHEMA_ROUTE, CLIENT_CERT


def get_metadata_from_parent(base_url, config):
    client_cert = config[CLIENT_CERT]
    try:
        resp = requests.get(base_url + SCHEMA_ROUTE, cert=client_cert, verify=False)
        schema = resp.json()
        return deserialize(schema["schema"])
    except ConnectionError as e:
        raise RuntimeError(f"Could not reach parent at {base_url}")
