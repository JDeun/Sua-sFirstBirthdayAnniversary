"""Build private, user-approved film props without publishing or changing originals.

Story order is explicitly approved. All media copies live below video/public/media,
which is ignored by Git. No face detection, external APIs, or inferred dates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

from .normalize import normalize

FPS = 30
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v"}
AUDIO_SUFFIXES = {".mp3", ".wav", ".m4a", ".aac"}


def probe_duration_seconds(path: Path) -> float:
    """FFprobe duration in seconds. Caller handles rounding to whole film frames."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, check=True, timeout=30,
        )
        duration = float(result.stdout.strip())
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        raise ValueError(f"FFprobe로 길이를 읽을 수 없습니다: {path.name}") from exc
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"유효하지 않은 미디어 길이: {path.name}")
    return duration


def allocate_frames(weights: list[float], total: int, minimum: int = FPS) -> list[int]:
    """Exact sum; chronological order preserved; at least one second per shot."""
    if not weights or not all(math.isfinite(w) and w > 0 for w in weights):
        raise ValueError("최소 한 장의 승인 샷과 양수 weight가 필요합니다.")
    if total < len(weights) * minimum:
        raise ValueError("음원 길이에 비해 승인 샷이 너무 많습니다.")
    pool = total - len(weights) * minimum
    raw = [pool * w / sum(weights) for w in weights]
    floors = [math.floor(value) for value in raw]
    left = pool - sum(floors)
    order = sorted(range(len(weights)), key=lambda i: (-(raw[i] - floors[i]), i))
    for i in order[:left]:
        floors[i] += 1
    return [n + minimum for n in floors]


def _source_path(name: str, base: Path) -> Path:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("shot.source는 파일 경로 문자열이어야 합니다.")
    path = Path(name).expanduser()
    path = (path if path.is_absolute() else base / path).resolve()
    if not path.is_file():
        raise ValueError(f"승인한 미디어를 찾을 수 없습니다: {name}")
    return path


def _media_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        return "image"
    if suffix in VIDEO_SUFFIXES:
        return "video"
    raise ValueError(f"지원하지 않는 사진/동영상 형식: {path.name}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy_private(path: Path, public_dir: Path, folder: str) -> str:
    """Hashed copies avoid same-name collisions; never overwrite an existing asset."""
    digest = _sha256(path)
    filename = f"{digest}{path.suffix.lower()}"
    dest = public_dir / "media" / folder / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(path, dest)
    elif _sha256(dest) != digest:
        raise ValueError(f"로컬 캐시의 파일이 손상되었습니다: {dest}")
    return "media/" + folder + "/" + filename


def _optional_text(value: object, name: str, max_length: int) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str) or len(value) > max_length:
        raise ValueError(f"{name}은 최대 {max_length}글자 문자열이어야 합니다.")
    return value


def prepare_film(
    approved_path: Path,
    opening_props_path: Path,
    song_path: Path,
    public_dir: Path,
    props_path: Path,
    end_card_seconds: float = 4.0,
    normalize_media: bool = False,
) -> dict:
    """Build a film whose song plays once from t=0, after the silent cold open.

    Validate every input, duration, and video clip before copying or writing.
    """
    approval = json.loads(approved_path.read_text(encoding="utf-8"))
    opening = json.loads(opening_props_path.read_text(encoding="utf-8"))
    if not isinstance(approval, dict) or not isinstance(approval.get("shots"), list):
        raise ValueError('승인 파일에는 "shots" 배열이 필요합니다.')
    entries = approval["shots"]
    if not entries:
        raise ValueError("본편에 사용할 사진이나 동영상을 한 개 이상 승인해 주세요.")
    if not isinstance(opening, dict) or not isinstance(opening.get("imagePaths"), list):
        raise ValueError("먼저 sua-matchcut으로 opening-props.json을 만드세요.")
    marker = opening.get("timing") or {}
    matchcut_end = marker.get("matchcutEndFrame", 240)
    song_start = marker.get("songStartFrame", marker.get("verseStartFrame", 450))
    birth_end = marker.get("birthEndFrame", matchcut_end + 120)
    if not (isinstance(matchcut_end, int) and isinstance(birth_end, int) and isinstance(song_start, int) and
            matchcut_end >= 2 and matchcut_end < birth_end and birth_end + 15 <= song_start < 630):
        raise ValueError("콜드 오픈 마커가 유효하지 않습니다.")
    song_path = song_path.expanduser().resolve()
    if not song_path.is_file() or song_path.suffix.lower() not in AUDIO_SUFFIXES:
        raise ValueError("로컬의 유효한 음악 파일(mp3/wav/m4a/aac)을 지정하세요.")
    song_frames = math.ceil(probe_duration_seconds(song_path) * FPS)
    if not math.isfinite(end_card_seconds) or not 1 <= end_card_seconds <= 10:
        raise ValueError("엔딩 카드는 1~10초로 설정하세요.")
    end_frames = round(end_card_seconds * FPS)
    story_frames = song_frames - end_frames
    if story_frames < len(entries) * FPS:
        raise ValueError("음악 길이에 비해 샷 수가 많거나 엔딩이 너무 깁니다.")

    validated = []
    weights = []
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise ValueError(f"샷 {index}: 객체 형식이 아닙니다.")
        src = _source_path(item.get("source"), approved_path.parent)
        kind = _media_kind(src)
        weight = item.get("weight", 1)
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or weight <= 0:
            raise ValueError(f"샷 {index}: weight는 양수여야 합니다.")
        chapter = _optional_text(item.get("chapter"), "chapter", 70)
        caption = _optional_text(item.get("caption"), "caption", 140)
        treatment = item.get("treatment", "cinematic")
        if treatment not in ("cinematic", "scrapbook", "variety"):
            raise ValueError(f"샷 {index}: treatment가 잘못되었습니다.")
        start = item.get("start_seconds", 0)
        if isinstance(start, bool) or not isinstance(start, (int, float)) or not math.isfinite(start) or start < 0:
            raise ValueError(f"샷 {index}: start_seconds가 잘못되었습니다.")
        if kind == "image" and start != 0:
            raise ValueError(f"샷 {index}: 사진에는 start_seconds를 사용할 수 없습니다.")
        validated.append((src, kind, chapter, caption, treatment, start))
        weights.append(weight)

    # Two authoring modes:
    # - weight: automatic rough-cut preview, no editing expertise needed
    # - cut_at_seconds: exact lyric/beat-aligned cuts chosen by the editing agent,
    #   reviewed by the family; times are relative to Suno song 0:00.
    marked = ["cut_at_seconds" in item for item in entries]
    if any(marked):
        if not all(marked):
            raise ValueError("정확한 컷 모드에서는 모든 샷에 cut_at_seconds가 필요합니다.")
        starts: list[int] = []
        for i, item in enumerate(entries):
            cut = item["cut_at_seconds"]
            if isinstance(cut, bool) or not isinstance(cut, (int, float)) or not math.isfinite(cut) or cut < 0:
                raise ValueError(f"샷 {i}: cut_at_seconds는 0 이상의 숫자여야 합니다.")
            starts.append(round(cut * FPS))
        if starts[0] != 0:
            raise ValueError("첫 번째 샷은 노래 시작인 cut_at_seconds=0이어야 합니다.")
        durations = [
            end - start for start, end in zip(starts, starts[1:] + [story_frames])
        ]
        if any(n < FPS for n in durations):
            raise ValueError("컷 시점은 오름차순이어야 하고, 각 샷은 최소 1초여야 합니다.")
    else:
        durations = allocate_frames(weights, story_frames)
    for i, ((src, kind, _, _, _, start), frames) in enumerate(zip(validated, durations)):
        if kind == "video" and start + frames / FPS > probe_duration_seconds(src) + 0.033:
            raise ValueError(f"샷 {i}: 동영상 길이가 할당된 {frames / FPS:.1f}초보다 짧습니다. weight를 줄이거나 다른 샷을 추가하세요.")

    # The opening birth clip is not part of the story shot allocation. Validate
    # its locally staged file before producing the final props file.
    public_dir = public_dir.resolve()
    birth_clip = opening.get("birthClip")
    if birth_clip is not None:
        if not isinstance(birth_clip, dict):
            raise ValueError("탄생 영상 설정은 객체여야 합니다.")
        relative = birth_clip.get("path")
        offset = birth_clip.get("sourceStartFrame", 0)
        if (not isinstance(relative, str) or not relative.startswith("media/") or
                "\\" in relative or any(part in (".", "..") for part in Path(relative).parts) or
                Path(relative).suffix.lower() not in VIDEO_SUFFIXES):
            raise ValueError("탄생 영상 경로는 public/media 내부의 동영상이어야 합니다.")
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            raise ValueError("탄생 영상 시작 프레임은 0 이상의 정수여야 합니다.")
        candidate = (public_dir / relative).resolve()
        if not candidate.is_relative_to((public_dir / "media").resolve()) or not candidate.is_file():
            raise ValueError("탄생 영상 파일이 로컬 public/media에 없습니다.")
        required = (birth_end - matchcut_end) / FPS
        if offset / FPS + required > probe_duration_seconds(candidate) + 0.033:
            raise ValueError("탄생 영상 길이가 할당된 구간보다 짧습니다.")
    if not normalize_media:
        heic = [src.name for src, kind, *_ in validated if kind == "image" and src.suffix.lower() in {".heic", ".heif"}]
        if heic:
            raise ValueError("HEIC/HEIF 사진은 --normalize-media 옵션이 필요합니다: " + ", ".join(heic))
    # All input validation precedes private asset conversion. The normalized
    # files are local derivatives; source originals are never modified.
    if normalize_media:
        normalized_dir = public_dir / "media" / ".normalized-cache"
        validated = [
            (normalize(src, normalized_dir), kind, chapter, caption, treatment, start)
            for src, kind, chapter, caption, treatment, start in validated
        ]
        song_path = normalize(song_path, normalized_dir)
    shots = []
    elapsed = 0
    for (src, kind, chapter, caption, treatment, start), frames in zip(validated, durations):
        path = _copy_private(src, public_dir, "story")
        shot = {
            "kind": kind, "path": path, "startFrame": elapsed,
            "durationFrames": frames, "treatment": treatment,
        }
        if chapter:
            shot["chapter"] = chapter
        if caption:
            shot["caption"] = caption
        if kind == "video":
            shot["sourceStartFrame"] = round(start * FPS)
        shots.append(shot)
        elapsed += frames
    assert elapsed == story_frames
    song_local = _copy_private(song_path, public_dir, "music")
    opening = dict(opening)
    opening["musicPath"] = song_local
    opening["timing"] = {"matchcutEndFrame": matchcut_end, "birthEndFrame": birth_end, "songStartFrame": song_start}
    props = {"opening": opening, "songDurationFrames": song_frames,
             "endCardFrames": end_frames, "shots": shots}
    props_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = props_path.with_name(props_path.name + ".tmp")
    temporary.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(props_path)
    return props


def main() -> None:
    parser = argparse.ArgumentParser(description="승인한 로컬 사진·영상과 Suno 완성곡으로 본편 타임라인 생성")
    parser.add_argument("--approved", type=Path, default=Path("data/approved-story.json"))
    parser.add_argument("--opening-props", type=Path, default=Path("data/opening-props.json"))
    parser.add_argument("--song", type=Path, required=True, help="로컬 최종 MP3/WAV 경로")
    parser.add_argument("--public-dir", type=Path, default=Path("video/public"))
    parser.add_argument("--props", type=Path, default=Path("data/film-props.json"))
    parser.add_argument("--end-card-seconds", type=float, default=4)
    parser.add_argument("--normalize-media", action="store_true",
                        help="원본을 보존하고 편집용 PNG/MP4/WAV 사본을 생성")
    args = parser.parse_args()
    result = prepare_film(args.approved, args.opening_props, args.song,
                          args.public_dir, args.props, args.end_card_seconds, args.normalize_media)
    total = result["opening"]["timing"]["songStartFrame"] + result["songDurationFrames"]
    print(f"완성곡 0초부터 재생 · 본편 {len(result['shots'])}샷 · 전체 {total}프레임 "
          f"({total / FPS:.2f}초) · {args.props}")


if __name__ == "__main__":
    main()
