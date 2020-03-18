from passlib.hash import argon2
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


def generate_argon2_hash(password, rounds=4):
    """
    Calculates an Argon2 password hash.

    Args:
        param1: password
        param2: number of rounds

    Returns:
        Argon2 password hash.
    """
    # Calculate new salt, a hash
    # h = argon2.hash(password)
    # Generate it with an explicit number of rounds (default 4)
    # print('Calculating Argon2 password hash with {}'.format(str(rounds)))
    hashed = argon2.using(rounds=rounds).hash(password)
    return hashed


def check_argon2_hash(password, hashed):
    """
    Verifies a password with its Argon2 password hash.

    Args:
        param1: password
        param2: argon2 password hash

    Returns:
        True for success, False otherwise
    """
    # Verify the password
    return argon2.verify(password, hashed)
