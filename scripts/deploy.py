#!/usr/bin/env python3

import logging

import deploy_harbor
import deploy_rep
import deploy_xuml
from auth import fetch_new_token
from deploy_rep import load_deployments, save_deployments

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger("deploy")


def main():

    log.info("Starting deployment pipeline...")

    deployments = load_deployments()

    if not deployments:
        log.info("Nothing to deploy.")
        return

    token = fetch_new_token()

    deployments = deploy_rep.run(deployments, token)
    deployments = deploy_harbor.run(deployments, token)
    deployments = deploy_xuml.run(deployments, token)

    save_deployments(deployments)

    log.info("Deployment pipeline completed.")


if __name__ == "__main__":
    main()