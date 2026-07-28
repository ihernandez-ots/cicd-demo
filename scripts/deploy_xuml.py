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

XUML_URL = os.environ["XUML_URL"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger("deploy_xuml")


def load_deployments():
    with open("output/deployment_list.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_deployments(deployments):
    with open("output/deployment_list.json", "w", encoding="utf-8") as f:
        json.dump(deployments, f, indent=4)


def get_xuml_image(docker_image: str) -> str:
    return docker_image.split("/pas/", 1)[1]


def deploy_xuml(deployment, token):

    image_name = Path(deployment["filename"]).stem.lower()

    payload = {
        "image": get_xuml_image(deployment["docker_image"]),
        "name": image_name,
        "hostname": image_name,
        "labels": {},
        "recreateIfExists": True
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    log.info("Deploying xUML %s", image_name)

    response = requests.post(
        XUML_URL,
        headers=headers,
        json=payload,
        verify=VERIFY_SSL,
        timeout=300
    )

    try:
        response.raise_for_status()
    except requests.HTTPError:
        log.error(response.text)
        raise

    try:
        result = response.json()
    except ValueError:
        result = {"raw_response": response.text}

    deployment["xuml_response"] = result
    deployment["status"] = "XUML_DEPLOYED"

    log.info("xUML deployment completed for %s", image_name)
    

def run(deployments, token):

    for deployment in deployments:

        try:

            if deployment["status"] != "HARBOR_DEPLOYED":
                continue

            deploy_xuml(deployment, token)

        except Exception as e:

            deployment["status"] = "FAILED"

            deployment["error"] = str(e)

            log.exception("xUML deployment failed")

    save_deployments(deployments)

    return deployments


def main():

    deployments = load_deployments()

    token = fetch_new_token()

    for deployment in deployments:

        try:

            if deployment["status"] != "HARBOR_DEPLOYED":
                continue

            deploy_xuml(deployment, token)

        except Exception as e:

            deployment["status"] = "FAILED"

            deployment["error"] = str(e)

            log.exception("xUML deployment failed")

    save_deployments(deployments)


if __name__ == "__main__":
    main()