#!/usr/bin/env python3
"""Build a tiny, silent geometry-only fixture; every date and label is fictional."""
import argparse
from pathlib import Path

from filmtools.paths import write_json

KEY_GROUPS = (("FaceMatchcut", 1, 2), ("Greeting", 3, 3), ("NarrativeFilmDraft", 4, 7),
              ("narrative.MemorySound", 8, 8), ("narrative.NarrativeMedia", 9, 10),
              ("narrative.NarrativeOpening", 11, 19), ("narrative.VerseTypography", 20, 32),
              ("performance.ChorusPerformance", 33, 35), ("performance.faith-graphics", 36, 37),
              ("performance.faith-scenes", 38, 44), ("performance.full-timing", 45, 52),
              ("performance.portrait", 53, 54), ("performance.scenes", 55, 70))
CUE_IDS = ("star", "princess", "universe", "tremor", "shelter", "star-repeat",
           "princess-repeat", "gift", "love", "prayer")


def svg(color):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="640" height="800" viewBox="0 0 640 800">'
            f'<rect width="640" height="800" fill="{color}"/>'
            '<circle cx="320" cy="270" r="140" fill="#e9bd91"/>'
            '<circle cx="270" cy="250" r="12" fill="#343747"/>'
            '<circle cx="370" cy="250" r="12" fill="#343747"/>'
            '<path d="M275 320 Q320 350 365 320" fill="none" stroke="#735951" stroke-width="8"/>'
            '<path d="M130 800V580Q130 430 320 430Q510 430 510 580V800" fill="#768baf"/>'
            '<path d="M20 760L100 650L180 760Z" fill="#d6c2e7"/></svg>\n')


def layout():
    return {"family": "contact-print", "media": {"x": 1040, "y": 90, "width": 720, "height": 900},
            "words": {"x": 140, "y": 300, "width": 780, "height": 400}, "radius": 0,
            "mat": 0, "tilt": 0, "align": "left", "typeSize": 100, "shade": "cream",
            "typeface": "sans", "inset": 0}


def cue(key, text, first, last):
    normalized = ''.join(c for c in text if c.isalnum())
    return {"id": key, "text": text, "start_frame": first, "end_frame": last,
            "start_seconds": first / 30, "end_seconds": last / 30,
            "words": [{"text": text, "start_frame": first, "end_frame": last,
                       "start_seconds": first / 30, "end_seconds": last / 30,
                       "char_start": 0, "char_end": len(normalized)}], "accent_beat_frames": []}


def runtime():
    assets, shots = {}, []
    for i, key in enumerate(("scene-a", "scene-b")):
        original = f"media/{key}.svg"
        assets[key] = {"asset": f"demo/{key}.svg", "original": original, "kind": "photo",
                       "dimensions": [640, 800], "framing": "context", "preserveContext": True,
                       "face": [.5, .34], "head": [.5, .12]}
        shots.append({"id": key, "usage": "baseline", "chapter": i, "kind": "photo",
                      "canonical_original_source": original, "captured_at": f"2000-01-0{i+1}T00:00:00Z",
                      "date_basis": {"status": "fictional_demo_timestamp"},
                      "song_start_frame": i * 60, "song_end_frame": (i + 1) * 60,
                      "duration_in_frames": 60, "caption": "A new chapter" if i == 0 else "Keep growing",
                      "captionCues": [], "lyricOwned": False, "frameLayout": layout()})
    outro = {"fps": 30, "status": "synthetic_demo", "review_status": "synthetic",
             "lines": [cue("closing", "Final chapter", 90, 120)], "final_line_id": "closing"}
    opening = {"mode": "none", "ultrasound_frames": 0, "matchcut_frames": 0,
               "matchcut_mode": "full", "title_start_frame": 0, "birth_start_frame": 0,
               "duration_in_frames": 0, "heartbeat": {"enabled": False}}
    plan = {"schema_version": "1.0", "status": "ready", "revision": "synthetic-demo", "fps": 30,
            "render_directory": "demo", "main_duration_in_frames": 120, "total_frames": 120,
            "opening": opening, "choruses": [], "shots": shots, "assets": assets,
            "outro_alignment": outro, "rhythm": {"beat_frames": [], "tempo_bpm": 0, "source": "none"},
            "memory_audio": {"enabled": False, "shot_id": "scene-a", "asset": "", "source_gain": 0,
                             "source_window_frames": [0, 60], "source_fade_frames": 4}}
    full = [cue(key, "Demo", i * 6, (i + 1) * 6) for i, key in enumerate(CUE_IDS)]
    chorus = {"status": "auto_aligned_review_required", "review_status": "not_reviewed",
              "song_asset": "", "fps": 30, "method": "synthetic fixture; no audio alignment",
              "occurrences": [{"id": "demo", "song_start_frame": 0, "song_end_frame": 30,
                               "cues": full[:5], "full_cues": full, "full_end_frame": 60,
                               "full_lyric_lines": ["Demo"] * 8}]}
    strings = {f"{module}.{i:03}": "Demo" for module, first, last in KEY_GROUPS for i in range(first, last + 1)}
    copy = {"strings": strings, "assets": {"heartbeat": "", "prenatal": "", "birth": ""}, "song_asset": None,
            "opening": {"birth_trim_before": 0}}
    return {"narrative-edit.json": plan, "narrative-media.json": {"schema_version": "1.0", "status": "ready",
            "fps": 30, "assets": assets}, "media-exclusions.json": {"excluded_stems": []},
            "chorus-alignment.json": chorus, "outro-alignment.json": outro,
            "copy.json": copy, "stopmotion.json": [], "matchcut.json": []}


def build(destination):
    destination = Path(destination)
    for name, payload in runtime().items():
        write_json(destination / "runtime" / name, payload)
    for key, color in (("scene-a", "#f4ede5"), ("scene-b", "#e4ebf1")):
        for directory in (destination / "assets/demo", destination / "sources"):
            directory.mkdir(parents=True, exist_ok=True)
            (directory / (key + ".svg")).write_text(svg(color), encoding="utf-8")
    write_json(destination / "project.json", {"runtime_directory": "runtime", "asset_directory": "assets",
               "media_directory": "sources", "output_directory": "output", "staging_mode": "copy"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=Path(__file__).resolve().parents[1] / "examples/demo")
    args = parser.parse_args()
    build(args.destination)


if __name__ == "__main__":
    main()
