#!/usr/bin/env python3

import json
import logging
import os
from pathlib import Path

import requests
import urllib3
from auth import fetch_new_token
from dotenv import load_dotenv

# -------------------------------------------------
# Environment
# -------------------------------------------------

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

if os.environ.get("VERIFY_SSL", "false").lower() != "true":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERIFY_SSL = os.environ.get("VERIFY_SSL", "false").lower() == "true"

FILE_STORAGE_BASE_URL = os.environ["FILE_STORAGE_BASE_URL"]
FILE_STORAGE_NAMESPACE = os.environ["FILE_STORAGE_NAMESPACE"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger("deploy")


# -------------------------------------------------
# Load deployment list
# -------------------------------------------------

def load_deployments():

    with open(
        "output/deployment_list.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_deployments(deployments):

    with open(
        "output/deployment_list.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            deployments,
            f,
            indent=4
        )


# -------------------------------------------------
# Upload REP
# -------------------------------------------------

def upload_rep(deployment, token):

    url = f"{FILE_STORAGE_BASE_URL}/{FILE_STORAGE_NAMESPACE}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    filename = deployment["filename"]

    path = Path(deployment["path"])

    log.info("Uploading %s", filename)

    with open(path, "rb") as fp:

        response = requests.post(
            url,
            headers=headers,
            data={
                "name": filename
            },
            files={
                filename: (
                    filename,
                    fp,
                    "application/octet-stream"
                )
            },
            verify=VERIFY_SSL,
            timeout=300
        )

    response.raise_for_status()

    payload = response.json()

    if not payload:
        raise Exception("File Storage returned an empty response.")

    deployment["file_id"] = payload[0]["fileId"]

    deployment["status"] = "REP_UPLOADED"

    log.info(
        "Uploaded %s -> %s",
        filename,
        deployment["file_id"]
    )
    


# -------------------------------------------------
# Main
# -------------------------------------------------

def run(deployments, token):

    for deployment in deployments:

        try:

            upload_rep(
                deployment,
                token
            )

        except Exception as e:

            deployment["status"] = "FAILED"

            deployment["error"] = str(e)

            log.exception(
                "Failed uploading %s",
                deployment["filename"]
            )

    save_deployments(deployments)

    log.info("REP upload phase completed.")

    return deployments

def main():

    deployments = load_deployments()

    if not deployments:
        log.info("Nothing to deploy.")
        return

    token = fetch_new_token()

    for deployment in deployments:

        try:

            upload_rep(
                deployment,
                token
            )

        except Exception as e:

            deployment["status"] = "FAILED"

            deployment["error"] = str(e)

            log.exception(
                "Failed uploading %s",
                deployment["filename"]
            )

    save_deployments(deployments)

    log.info("REP upload phase completed.")


if __name__ == "__main__":

    main()