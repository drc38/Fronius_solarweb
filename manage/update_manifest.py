"""Update the manifest file."""

# https://github.com/hacs/integration/blob/main/manage/update_manifest.py
import json
import os
import sys


def update_manifest() -> None:
    """Update the manifest file."""
    version = "0.0.0"
    for index, value in enumerate(sys.argv):
        if value in ["--version", "-V"]:
            version = sys.argv[index + 1]

    with open(
        f"{os.getcwd()}/custom_components/solarweb/manifest.json"
    ) as manifestfile:
        manifest = json.load(manifestfile)

    manifest["version"] = version

    with open(
        f"{os.getcwd()}/custom_components/solarweb/manifest.json", "w"
    ) as manifestfile:
        manifestfile.write(json.dumps(manifest, indent=4, sort_keys=False))


update_manifest()
