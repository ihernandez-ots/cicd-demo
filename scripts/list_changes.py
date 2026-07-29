import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

rep_path = Path(".")

def discover_changed_rep_files():
    """
    Returns a list of changed .rep files in the latest commit.
    """

    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        capture_output=True,
        text=True,
        check=True
    )

    print(subprocess.run(
        ["git", "log", "--oneline", "-2"],
        capture_output=True,
        text=True
    ).stdout)

    rep_files = []

    for line in result.stdout.splitlines():

        file = Path(line.strip())

        if file.suffix.lower() == ".rep":
            rep_files.append(file)

    print("Discovered changed .rep files:", rep_files)
    return rep_files


def extract_metadata(rep_path):

    with zipfile.ZipFile(rep_path) as rep:

        xml = rep.read("modules.xml")

    root = ET.fromstring(xml)
    composite = root.find("composite")
    compilation = composite.find("compilation")

    return {
        "name": composite.attrib["name"],
        "version": composite.attrib["version"],
        "compiler": compilation.attrib.get("compiler"),
        "time": compilation.attrib.get("time")
    }


def build_deployment_list(rep_files):

    deployments = []

    for rep in rep_files:

        metadata = extract_metadata(rep)

        deployments.append({
            "path": str(rep),
            "filename": rep.name.lower(),
            "name": metadata["name"],
            "version": metadata["version"],
            "compiler": metadata["compiler"],
            "time": metadata["time"],
            "status": "PENDING",
            "file_id": None
        })

    return deployments

def save_deployments(deployments):

    Path("output").mkdir(exist_ok=True)

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

# def run():

#     rep_files = discover_changed_rep_files()

#     if not rep_files:
#         return []

#     deployments = build_deployment_list(rep_files)

#     save_deployments(deployments)

#     return deployments

def main():

    rep_files = discover_changed_rep_files()

    if not rep_files:
        print("No REP files changed.")
        return

    deployments = build_deployment_list(rep_files)
    save_deployments(deployments)

    print(f"Discovered {len(deployments)} deployment(s).")

if __name__ == "__main__":

    main()