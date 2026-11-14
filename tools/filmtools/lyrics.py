"""Convert local word estimates to explicit cues; ambiguous text is rejected."""
import hashlib
import unicodedata

from .checks import frame, number


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFC", text).casefold() if c.isalnum())


def provenance(audio_hash, text, model_hash, language):
    return {"song_sha256": audio_hash, "lyrics_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "model_sha256": model_hash, "language": language}


def indexed_words(segment):
    words, cursor, previous = [], 0, -1
    for row in segment.get("words", []):
        text = normalize(row["word"])
        if not text:
            continue
        first = number(row["start"], "word start", minimum=0)
        last = number(row["end"], "word end", minimum=0)
        if first < previous or last <= first:
            raise ValueError("Word timestamps must be positive and nonoverlapping")
        words.append({"text": text, "start_seconds": first, "end_seconds": last,
                      "char_start": cursor, "char_end": cursor + len(text)})
        cursor += len(text)
        previous = last
    if "".join(w["text"] for w in words) != normalize(segment["text"]):
        raise ValueError("Timed word coverage differs from supplied text")
    return words


def phrase_cue(segment, spec, beats, fps):
    text, needle = segment["text"], normalize(spec["text"])
    if not needle:
        raise ValueError("Cue text must contain letters or numbers")
    if normalize(text).count(needle) != 1 and "char_start" not in spec:
        raise ValueError("Repeated/missing cue text requires an explicit normalized char_start")
    position = spec.get("char_start", normalize(text).find(needle))
    end = position + len(needle)
    if position < 0 or normalize(text)[position:end] != needle:
        raise ValueError("Cue text not found at specified position")
    words = [w for w in indexed_words(segment) if w["char_end"] > position and w["char_start"] < end]
    if not words or words[0]["char_start"] != position or words[-1]["char_end"] != end:
        raise ValueError("Cue boundaries must coincide with estimated word boundaries")
    timed = [{**w, "char_start": w["char_start"] - position, "char_end": w["char_end"] - position,
              "start_frame": frame(w["start_seconds"], fps), "end_frame": frame(w["end_seconds"], fps)}
             for w in words]
    if any(w["end_frame"] <= w["start_frame"] for w in timed):
        raise ValueError("A word estimate is shorter than the output frame grid")
    accents = sorted({frame(b, fps) for b in beats if timed[0]["start_frame"] <= frame(b, fps) <
                      timed[-1]["end_frame"] and any(abs(b - w["start_seconds"]) <= .12 for w in timed)})
    return {"id": spec["id"], "text": spec["text"], "words": timed,
            "start_seconds": words[0]["start_seconds"], "end_seconds": words[-1]["end_seconds"],
            "start_frame": timed[0]["start_frame"], "end_frame": timed[-1]["end_frame"],
            "accent_beat_frames": accents}


def occurrences(native, groups, beats, fps):
    result = []
    for group in groups:
        cues = [phrase_cue(native["segments"][s["segment_index"]], s, beats, fps) for s in group["phrases"]]
        if not cues or any(a["end_frame"] > b["start_frame"] for a, b in zip(cues, cues[1:])):
            raise ValueError("Cue group is empty or has overlapping estimates")
        result.append({"id": group["id"], "song_start_frame": cues[0]["start_frame"],
                       "song_end_frame": cues[-1]["end_frame"], "cues": cues,
                       "full_end_frame": cues[-1]["end_frame"], "full_cues": cues,
                       "full_lyric_lines": [c["text"] for c in cues]})
    return result
