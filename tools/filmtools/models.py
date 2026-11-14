"""Verify a local model against the shared registry; deliberately no downloader."""
from pathlib import Path

from .paths import read_json, sha256, within


def registered_model(registry, model_id, directory=None):
    spec = next(row for row in read_json(registry)["models"] if row["id"] == model_id)
    path = within(directory or Path(registry).parent, spec["filename"])
    if path.stat().st_size != spec["size_bytes"] or sha256(path) != spec["sha256"]:
        raise ValueError("Local model does not match its registry size and SHA-256")
    return path
