"""Unique canonical originals, contiguous EDL, and conservative date ordering."""
from datetime import datetime, timezone
from pathlib import PurePosixPath

from .checks import integer
from .paths import collision_key, relative_name


def stamp(value):
    if not isinstance(value, str):
        raise ValueError("Capture date is missing; manual placement is required")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return result.replace(tzinfo=timezone.utc) if result.tzinfo is None else result.astimezone(timezone.utc)


def capture_interval(shot):
    interval = shot.get("date_basis", {}).get("sort_interval")
    if interval is not None:
        if not isinstance(interval, list) or len(interval) != 2:
            raise ValueError("Capture interval requires two dates")
        first, last = map(stamp, interval)
        if last < first:
            raise ValueError("Capture interval is reversed")
        return first, last
    when = stamp(shot.get("captured_at"))
    return when, when


def chronology(shots):
    errors, manual, previous = [], [], None
    for shot in shots:
        try:
            interval = capture_interval(shot)
        except (ValueError, TypeError):
            manual.append({"id": shot["id"], "code": "unknown_capture_time"})
            continue
        if previous is not None:
            if interval[1] < previous[0]:
                errors.append({"id": shot["id"], "code": "capture_moves_backwards"})
            elif interval[0] < previous[1] and interval != previous:
                manual.append({"id": shot["id"], "code": "overlapping_date_precision"})
        if previous is None or interval[0] >= previous[0]:
            previous = interval
    return errors, manual


def check_shots(shots, assets, total, excluded):
    end, identities, ids = 0, set(), set()
    for shot in shots:
        key = shot["id"]
        if not isinstance(key, str) or key in ids or key not in assets:
            raise ValueError("Shot IDs must be unique and have an asset")
        original = str(relative_name(shot["canonical_original_source"]))
        identity = collision_key(original)
        if identity in identities or PurePosixPath(original).stem.casefold() in excluded:
            raise ValueError("Repeated or excluded canonical original")
        if assets[key]["original"] != original or assets[key]["kind"] != shot["kind"]:
            raise ValueError("Shot and asset original/kind disagree")
        first = integer(shot["song_start_frame"], "song_start_frame")
        last = integer(shot["song_end_frame"], "song_end_frame", minimum=1)
        duration = integer(shot["duration_in_frames"], "duration_in_frames", minimum=1)
        if first != end or last - first != duration:
            raise ValueError("EDL has a gap, overlap, or inconsistent duration")
        identities.add(identity)
        ids.add(key)
        end = last
    if not shots or end != total:
        raise ValueError("EDL must cover the complete main duration")


def validate_edl(plan, exclusions):
    shots = plan["shots"]
    if not isinstance(shots, list) or not isinstance(plan["assets"], dict):
        raise ValueError("Expected shots array and assets object")
    total = integer(plan["main_duration_in_frames"], "main_duration_in_frames", minimum=1)
    excluded = {str(s).casefold() for s in exclusions["excluded_stems"]}
    check_shots(shots, plan["assets"], total, excluded)
    baseline = [s for s in shots if s.get("usage") == "baseline"]
    errors, manual = chronology(baseline)
    if errors or any(row["code"] == "unknown_capture_time" for row in manual):
        raise ValueError(f"Baseline chronology requires review: {errors + manual}")
    return {"status": "pass", "shots": len(shots), "unique_originals": len(shots),
            "chronology_proven": not manual, "chronology_review_required": manual,
            "chronology_scope": "baseline; chorus montages are separate sequences"}
