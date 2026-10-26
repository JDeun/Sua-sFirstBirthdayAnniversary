"""Explicit, local-only promotion of reviewed music edit drafts.

This command records an affirmative human approval; agents must never call it
without the user's explicit approval of the specific draft.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def approve_draft(draft: Path, output: Path, *, confirmation: str) -> dict:
    if confirmation != "APPROVE":
        raise ValueError("Explicit --confirm APPROVE is required after human review")
    if draft.resolve() == output.resolve():
        raise ValueError("Approved output must differ from original draft")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite approved edits: {output}")
    source = json.loads(draft.read_text(encoding="utf-8"))
    if not isinstance(source, dict) or not isinstance(source.get("shots"), list) or not source["shots"]:
        raise ValueError("Draft must contain a nonempty shots list")
    marker = source.get("_draft_music_edit")
    if not isinstance(marker, dict) or marker.get("status") != "REVIEW_REQUIRED":
        raise ValueError("Only REVIEW_REQUIRED music drafts can be approved")
    if any(not isinstance(s, dict) or "cut_at_seconds" not in s for s in source["shots"]):
        raise ValueError("Every shot must have a reviewed cut_at_seconds")
    source["_draft_music_edit"] = {
        **marker,
        "status": "APPROVED",
        "approved_at_utc": datetime.now(timezone.utc).isoformat(),
        "approval_method": "explicit_local_cli",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as f:
        json.dump(source, f, ensure_ascii=False, indent=2)
    return source


def main() -> None:
    parser = argparse.ArgumentParser(description="Approve a personally reviewed music draft")
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--confirm", required=True, help="Must be APPROVE after human review")
    args = parser.parse_args()
    approve_draft(args.draft, args.output, confirmation=args.confirm)
    print(f"Approved edit saved: {args.output}")


if __name__ == "__main__":
    main()
