#!/usr/bin/env python3

import json
import logging
import os
from pathlib import Path

import requests
import urllib3
from auth import fetch_new_token
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

if os.environ.get("VERIFY_SSL", "false").lower() != "true":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERIFY_SSL = os.environ.get("VERIFY_SSL", "false").lower() == "true"

HARBOR_URL = os.environ["HARBOR_URL"]
FILE_STORAGE_NAMESPACE = os.environ["FILE_STORAGE_NAMESPACE"]
RUNTIME_VERSION = os.environ["RUNTIME_VERSION"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("deploy_harbor")


def load_deployments():
    with open("output/deployment_list.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_deployments(deployments):
    with open("output/deployment_list.json", "w", encoding="utf-8") as f:
        json.dump(deployments, f, indent=4)


def deploy_harbor(deployment, token):

    image_name = Path(deployment["filename"]).stem

    payload = {

        "imageName": image_name,

        "imageTag": deployment["version"],

        "imageType": "xuml-service",

        "options": {

            "source": {

                "fileId": deployment["file_id"],

                "profileName": FILE_STORAGE_NAMESPACE

            },

            "runtimeVersion": RUNTIME_VERSION

        }

    }

    headers = {

        "Authorization": f"Bearer {token}",

        "Content-Type": "application/json",

        "Accept": "application/json"

    }

    log.info(
        "Building Docker image %s:%s",
        image_name,
        deployment["version"]
    )

    response = requests.post(

        HARBOR_URL,

        headers=headers,

        json=payload,

        verify=VERIFY_SSL,

        timeout=600

    )

    try:

        response.raise_for_status()

    except requests.HTTPError:

        log.error(response.text)

        raise

    result = response.json()

    deployment["docker_image"] = result["name"]
    deployment["docker_image_id"] = result["image"]["id"]
    deployment["harbor_response"] = result
    deployment["status"] = "HARBOR_DEPLOYED"

    log.info(
        "Docker image created: %s",
        deployment["docker_image"]
    )

    return deployment

def run(deployments, token):

    for deployment in deployments:
        try:
            if deployment.get("status") != "REP_UPLOADED":
                log.info(
                    "Skipping %s because status is %s",
                    deployment.get("filename", deployment.get("name")),
                    deployment.get("status"),
                )
                continue

            deploy_harbor(deployment, token)

        except Exception as e:
            deployment["status"] = "FAILED"
            deployment["error"] = str(e)
            log.exception("Failed Harbor deployment for %s", deployment.get("filename"))

    save_deployments(deployments)
    log.info("Harbor deployment phase completed.")
    return deployments


def main():
    deployments = load_deployments()

    if not deployments:
        log.info("Nothing to deploy.")
        return

    token = fetch_new_token()

    for deployment in deployments:
        try:
            if deployment.get("status") != "REP_UPLOADED":
                log.info(
                    "Skipping %s because status is %s",
                    deployment.get("filename", deployment.get("name")),
                    deployment.get("status"),
                )
                continue

            deploy_harbor(deployment, token)

        except Exception as e:
            deployment["status"] = "FAILED"
            deployment["error"] = str(e)
            log.exception("Failed Harbor deployment for %s", deployment.get("filename"))

    save_deployments(deployments)
    log.info("Harbor deployment phase completed.")


if __name__ == "__main__":
    main()