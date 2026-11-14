"""The eight external JSON inputs consumed by the current renderer."""
from .checks import integer, number, vector
from .edl import validate_edl
from .endpoints import check_fit
from .lyrics import normalize
from .paths import read_json, relative_name, within

RUNTIME_FILES = ("narrative-edit.json", "narrative-media.json", "media-exclusions.json",
                 "chorus-alignment.json", "outro-alignment.json", "stopmotion.json",
                 "matchcut.json", "copy.json")


def load_runtime(directory):
    return {name: read_json(within(directory, name)) for name in RUNTIME_FILES}


def references(value):
    if isinstance(value, dict):
        if isinstance(value.get("assets"), dict):
            for child in value["assets"].values():
                if isinstance(child, str) and child:
                    yield str(relative_name(child))
        for key, child in value.items():
            if key in {"asset", "poster", "song_asset"} and isinstance(child, str) and child:
                yield str(relative_name(child))
            else:
                yield from references(child)
    elif isinstance(value, list):
        for child in value:
            yield from references(child)


def validate_asset(asset):
    relative_name(asset["asset"])
    relative_name(asset["original"])
    vector(asset["dimensions"], 2, "dimensions", positive=True)
    if asset["kind"] not in {"photo", "video"}:
        raise ValueError("Asset kind must be photo or video")
    if "playbackRate" in asset:
        number(asset["playbackRate"], "playbackRate", positive=True)


def validate_cues(cues, fps):
    end = -1
    for cue in cues:
        first = integer(cue["start_frame"], "cue start")
        last = integer(cue["end_frame"], "cue end", minimum=1)
        if first < end or last <= first or not isinstance(cue["text"], str):
            raise ValueError("Cues must be ordered, nonoverlapping, and positive")
        cursor, previous, covered = 0, first, []
        for word in cue.get("words", []):
            start = integer(word["start_frame"], "word start")
            stop = integer(word["end_frame"], "word end")
            if not first <= start < stop <= last or start < previous:
                raise ValueError("Word timestamps fall outside their cue")
            covered.append(normalize(word["text"]))
            if "char_start" in word:
                if word["char_start"] != cursor or word["char_end"] != cursor + len(covered[-1]):
                    raise ValueError("Word character offsets do not match their text")
                cursor = word["char_end"]
            previous = stop
        if covered and "".join(covered) != normalize(cue["text"]):
            raise ValueError("Words do not cover their complete cue")
        if any(not first <= integer(beat, "accent beat") < last for beat in cue.get("accent_beat_frames", [])):
            raise ValueError("Accent beat falls outside its cue")
        end = last


def validate_copy(data):
    if not isinstance(data, dict) or not isinstance(data["strings"], dict):
        raise ValueError("copy.json requires a strings mapping")
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in data["strings"].items()):
        raise ValueError("Copy keys and values must be strings")
    for key in ("heartbeat", "prenatal", "birth"):
        value = data["assets"][key]
        if not isinstance(value, str):
            raise ValueError("Opening asset references must be strings")
        if value:
            relative_name(value)
    integer(data["opening"]["birth_trim_before"], "birth_trim_before")
    if data.get("song_asset") is not None:
        relative_name(data["song_asset"])


def validate_runtime(data):
    plan, staged = data["narrative-edit.json"], data["narrative-media.json"]
    fps = integer(plan["fps"], "fps", minimum=1)
    opening = integer(plan["opening"]["duration_in_frames"], "opening duration")
    if plan["total_frames"] != opening + plan["main_duration_in_frames"]:
        raise ValueError("Total frame count disagrees with opening plus main")
    if staged["status"] != "ready" or not isinstance(staged["assets"], dict):
        raise ValueError("Staged media must be ready with an assets mapping")
    if staged.get("fps", fps) != fps:
        raise ValueError("Staged media fps differs from the edit")
    result = validate_edl(plan, data["media-exclusions.json"])
    for asset in plan["assets"].values():
        validate_asset(asset)
    for shot in plan["shots"]:
        if shot.get("usage") == "baseline":
            if "frameLayout" not in shot:
                raise ValueError("Baseline shot requires an explicit frameLayout")
            check_fit(plan["assets"][shot["id"]], shot["frameLayout"])
    for name in ("chorus-alignment.json", "outro-alignment.json"):
        if data[name]["fps"] != fps:
            raise ValueError("Alignment fps differs from the edit")
    for occurrence in data["chorus-alignment.json"]["occurrences"]:
        validate_cues(occurrence.get("full_cues", occurrence["cues"]), fps)
    validate_cues(data["outro-alignment.json"]["lines"], fps)
    if any(not isinstance(data[n], list) for n in ("stopmotion.json", "matchcut.json")):
        raise ValueError("Opening sequences must be arrays")
    validate_copy(data["copy.json"])
    return result
