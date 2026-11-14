#!/usr/bin/env python3
"""Validate external project inputs, then stage exactly eight runtime files and assets."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from filmtools.endpoints import check_endpoint, probe, video_info
from filmtools.paths import config_directory, read_json, sha256, unique_names, within
from filmtools.runtime import RUNTIME_FILES, load_runtime, references, validate_runtime


def directories(config_path, config):
    roots = {key: config_directory(config_path, config[key], must_exist=key != "output_directory")
             for key in ("runtime_directory", "asset_directory", "output_directory", "media_directory")}
    renderer = config.get("renderer_directory")
    roots["renderer"] = (config_directory(config_path, renderer, must_exist=False) if renderer
                         else Path(__file__).resolve().parents[1] / "renderer")
    sources = [roots[k] for k in ("runtime_directory", "asset_directory", "media_directory")]
    destinations = [roots["output_directory"], roots["renderer"]]
    if any(a == b or a.is_relative_to(b) or b.is_relative_to(a)
           for a in sources for b in destinations):
        raise ValueError("Source directories and output/renderer must not overlap")
    return roots


def original_file(media, reference):
    # Canonical IDs use a logical media/ prefix, independent of the physical root name.
    name = reference.removeprefix("media/")
    return within(media, name)


def validate_sources(roots, data):
    plan, records = data["narrative-edit.json"], data["narrative-media.json"]["assets"]
    refs = sorted(set(ref for name, value in data.items() if name != "narrative-media.json"
                      for ref in references(value)))
    unique_names(refs)
    sources = {ref: within(roots["asset_directory"], ref) for ref in refs}
    original_hashes = {}
    for asset in plan["assets"].values():
        original = original_file(roots["media_directory"], asset["original"])
        digest = sha256(original)
        if digest in original_hashes and original_hashes[digest] != asset["original"]:
            raise ValueError("Different canonical originals have duplicate content")
        original_hashes[digest] = asset["original"]
    for row in records.values():
        if row["asset"] not in sources:
            continue
        if row.get("output_sha256") and sha256(sources[row["asset"]]) != row["output_sha256"]:
            raise ValueError("Staged source hash differs from narrative-media evidence")
    checked = {}
    for shot in plan["shots"]:
        asset = plan["assets"][shot["id"]]
        if asset["kind"] != "video":
            continue
        source = sources[asset["asset"]]
        if source not in checked:
            checked[source] = video_info(probe(source, count_frames=True))
        check_endpoint(shot["duration_in_frames"], plan["fps"], checked[source],
                       asset.get("playbackRate", 1))
    return sources


def destination(root, reference):
    # Resolve parent links, but do not follow the leaf: leaf symlinks may be managed assets.
    target = root / reference
    parent = target.parent.resolve()
    if not parent.is_relative_to(root.resolve()):
        raise ValueError("Destination parent symlink escapes renderer")
    return target


def staging_plan(roots, sources):
    renderer = roots["renderer"]
    public = renderer / "public"
    generated = renderer / "src" / "generated"
    linked_runtime = generated.is_symlink() and generated.resolve() == roots["runtime_directory"]
    linked_assets = public.is_symlink() and public.resolve() == roots["asset_directory"]
    for directory, approved_link in ((public, linked_assets), (generated, linked_runtime)):
        if not approved_link and not directory.resolve().is_relative_to(renderer.resolve()):
            raise ValueError("Staging directory escapes renderer")
    jobs = [] if linked_runtime else [
        (within(roots["runtime_directory"], name), destination(generated, name), "copy")
        for name in RUNTIME_FILES]
    for ref, source in sources.items():
        if linked_assets:
            continue
        target = destination(public, ref)
        if target.exists() or target.is_symlink():
            if target.is_symlink() and target.resolve() == source:
                continue
            if target.is_file() and not target.is_symlink() and sha256(target) == sha256(source):
                continue
            raise ValueError(f"Public asset collision: {ref}")
        jobs.append((source, target, "asset"))
    if any(target.is_symlink() or (target.exists() and not target.is_file())
           for _, target, kind in jobs if kind == "copy"):
        raise ValueError("Generated runtime destinations must be regular files")
    return jobs


def commit_jobs(jobs, *, copy_assets=False):
    completed = []
    with tempfile.TemporaryDirectory(prefix="film-stage-") as scratch:
        try:
            for index, (source, target, kind) in enumerate(jobs):
                target.parent.mkdir(parents=True, exist_ok=True)
                backup = Path(scratch) / str(index)
                existed = target.exists()
                if existed:
                    shutil.copy2(target, backup)
                temporary = target.with_name(target.name + ".film-stage-tmp")
                if temporary.exists() or temporary.is_symlink():
                    raise ValueError("Temporary staging path already exists")
                try:
                    if kind == "asset" and not copy_assets:
                        try:
                            temporary.symlink_to(os.path.relpath(source, target.parent))
                        except OSError:
                            shutil.copy2(source, temporary)
                    else:
                        shutil.copy2(source, temporary)
                    os.replace(temporary, target)
                    completed.append((target, backup if existed else None))
                finally:
                    temporary.unlink(missing_ok=True)
        except BaseException:
            for target, backup in reversed(completed):
                if backup is None:
                    target.unlink(missing_ok=True)
                else:
                    shutil.copy2(backup, target)
            raise


def prepare(config_path, *, check_only=False, copy_assets=False):
    config = read_json(config_path)
    roots = directories(config_path, config)
    data = load_runtime(roots["runtime_directory"])
    report = validate_runtime(data)
    sources = validate_sources(roots, data)
    if not check_only:
        jobs = staging_plan(roots, sources)
        commit_jobs(jobs, copy_assets=copy_assets or config.get("staging_mode") == "copy")
        roots["output_directory"].mkdir(parents=True, exist_ok=True)
    return {**report, "runtime_files": len(RUNTIME_FILES), "referenced_assets": len(sources),
            "status": "validated" if check_only else "prepared"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="Validate without staging")
    parser.add_argument("--copy", action="store_true", help="Copy assets instead of symlinking")
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.config, check_only=args.check, copy_assets=args.copy)))
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
        print(f"Project input rejected: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
