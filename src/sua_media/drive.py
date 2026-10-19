"""Read-only Google Drive recursive media importer; no Drive mutations."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
from typing import Any

DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
FOLDER_MIME = "application/vnd.google-apps.folder"


def safe_component(value: str) -> str:
    """Prevent names from escaping the download directory."""
    stripped = re.sub(r"[\x00-\x1f/\\]+", "_", value).strip(" .")
    return stripped[:160] if stripped and stripped not in {".", ".."} else "untitled"


def drive_id(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{5,}", value):
        raise ValueError("Expected a Google Drive folder/file ID, not a shared URL.")
    return value


def authenticate(credentials_path: Path, token_path: Path):
    """OAuth is interactive only on first run; tokens never go into git."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as error:
        raise RuntimeError("Install Drive support: pip install -e '.[drive]'") from error

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), [DRIVE_SCOPE])
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not credentials_path.exists():
            raise FileNotFoundError("OAuth desktop client credentials JSON was not found.")
        creds = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path), [DRIVE_SCOPE]
        ).run_local_server(port=0)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    try:
        os.chmod(token_path, 0o600)
    except OSError:
        pass
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def list_children(service, folder: str) -> list[dict[str, Any]]:
    folder = drive_id(folder)
    page = None
    found: list[dict[str, Any]] = []
    while True:
        reply = service.files().list(
            q=f"'{folder}' in parents and trashed = false",
            fields="nextPageToken,files(id,name,mimeType,size,md5Checksum,createdTime,modifiedTime)",
            pageSize=1000,
            pageToken=page,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        found.extend(reply.get("files", []))
        page = reply.get("nextPageToken")
        if not page:
            break
    return sorted(found, key=lambda f: (f.get("name", ""), f["id"]))


def collect_media(service, root_folder: str) -> list[tuple[dict[str, Any], tuple[str, ...]]]:
    """Traverse one shared folder; prevent cycles and skip non-media docs."""
    queued = [(drive_id(root_folder), ())]
    seen_folders: set[str] = set()
    files: list[tuple[dict[str, Any], tuple[str, ...]]] = []
    while queued:
        folder_id, parts = queued.pop(0)
        if folder_id in seen_folders:
            continue
        seen_folders.add(folder_id)
        for info in list_children(service, folder_id):
            kind = info.get("mimeType", "")
            if kind == FOLDER_MIME:
                queued.append((drive_id(info["id"]), parts + (safe_component(info["name"]),)))
            elif kind.startswith(("image/", "video/")):
                files.append((info, parts))
    return files


def download_folder(service, folder_id: str, dest: Path, index_path: Path) -> dict[str, Any]:
    try:
        from googleapiclient.http import MediaIoBaseDownload
    except ImportError as error:
        raise RuntimeError("Install Drive support: pip install -e '.[drive]'") from error

    dest = dest.expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    for info, parts in collect_media(service, folder_id):
        safe_id = drive_id(info["id"])
        name = safe_component(info.get("name", "unnamed"))
        target = dest.joinpath(*parts, safe_id + "__" + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        status = "cached"
        if not target.is_file() or (info.get("size") and target.stat().st_size != int(info["size"])):
            status = "downloaded"
            temp = target.with_name(target.name + ".partial")
            try:
                with temp.open("wb") as stream:
                    request = service.files().get_media(fileId=safe_id, supportsAllDrives=True)
                    downloader = MediaIoBaseDownload(stream, request)
                    done = False
                    while not done:
                        _, done = downloader.next_chunk()
                os.replace(temp, target)
            finally:
                temp.unlink(missing_ok=True)
        entries.append({
            "drive_file_id": safe_id, "original_name": info.get("name"),
            "mime_type": info.get("mimeType"), "drive_created_time": info.get("createdTime"),
            "drive_modified_time": info.get("modifiedTime"),
            "local_path": str(target), "download_status": status,
            "md5_from_drive": info.get("md5Checksum"),
        })
    result = {"schema_version": 1, "folder_id": folder_id,
              "downloaded_at": datetime.now().astimezone().isoformat(), "files": entries}
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Download media from a shared Drive folder, read-only.")
    parser.add_argument("folder_id", type=drive_id, help="Folder ID from Google Drive URL")
    parser.add_argument("--credentials", type=Path, default=Path("credentials.json"))
    parser.add_argument("--token", type=Path, default=Path(".secrets/drive-token.json"))
    parser.add_argument("--out", type=Path, default=Path("assets/incoming/drive"))
    parser.add_argument("--index", type=Path, default=Path("data/drive-index.json"))
    args = parser.parse_args()
    result = download_folder(authenticate(args.credentials, args.token),
                             args.folder_id, args.out, args.index)
    print(f"Collected {len(result['files'])} photos/videos. Local index: {args.index}")
    print("Note: Drive created/modified timestamps are provenance, not camera capture time.")


if __name__ == "__main__":
    main()
