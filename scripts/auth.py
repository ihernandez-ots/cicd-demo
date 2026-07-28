#!/usr/bin/env python3
"""

1. Define .env variables

2. Execute
set -a
source .env
set +a

python migrate_services.py fetch-list           # prefetch services
python migrate_services.py export               # export all services from list
python migrate_services.py export --resume      # resume export
python migrate_services.py import               # import all services from exports folder
python migrate_services.py import --resume      # resume import
"""

import logging
import os
from pathlib import Path

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# CONFIG GET ACCESS TOKEN

KEYCLOAK_TOKEN_URL = os.environ.get(
    "KEYCLOAK_TOKEN_URL",
    "https://k8s.onetoolapps.com/pas/keycloak/realms/PAS/protocol/openid-connect/token",
)
TARGET_KEYCLOAK_USERNAME = os.environ["TARGET_KEYCLOAK_USERNAME"]
TARGET_KEYCLOAK_PASSWORD = os.environ["TARGET_KEYCLOAK_PASSWORD"]
TARGET_KEYCLOAK_CLIENT_ID = os.environ.get("TARGET_KEYCLOAK_CLIENT_ID", "tokengen")
TARGET_KEYCLOAK_CLIENT_SECRET = os.environ["TARGET_KEYCLOAK_CLIENT_SECRET"]

# CONFIG FILE STORAGE URL

FILE_STORAGE_URL = os.environ.get(
    "FILE_STORAGE_URL",
    "https://k8s.onetoolapps.com/pas/api/file-storage/files/sandbox_vvallejo",
)

VERIFY_SSL = os.environ.get("VERIFY_SSL", "false").lower() == "true" #curl -k

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("migrate")


# GET ACCESS TOKEN

def _fetch_token(token_url: str, username: str, password: str, client_id: str, client_secret: str) -> str:
    """Token fetch"""
    data = [
        ("username", username),
        ("password", password),
        ("client_id", client_id),
        ("grant_type", "password"),
        ("client_secret", client_secret),
    ]
    resp = requests.post(
        token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=data,
        verify=VERIFY_SSL,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def fetch_new_token() -> str:
    return _fetch_token(
        KEYCLOAK_TOKEN_URL,
        TARGET_KEYCLOAK_USERNAME,
        TARGET_KEYCLOAK_PASSWORD,
        TARGET_KEYCLOAK_CLIENT_ID,
        TARGET_KEYCLOAK_CLIENT_SECRET,
    )

def main():
    
    token = fetch_new_token()


def cmd_fetch_list(args):

    log.info("Fetching Keycloak token for the list call...")
    token = fetch_new_token()

    log.info("Fetching service list from %s (this happens ONCE)", FILE_STORAGE_URL)
    resp = requests.post(
        FILE_STORAGE_URL,
        headers={"accept": "application/json", "Authorization": f"Bearer {token}"},
        verify=VERIFY_SSL,
        timeout=60,
    )
    resp.raise_for_status()
    payload = resp.json()



if __name__ == "__main__":

    main()

