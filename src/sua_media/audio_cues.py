"""로컬 오디오에서 트랜지언트 후보를 찾고, 사람이 정한 음악 마커를 프레임으로 변환합니다.

트랜지언트(어택)는 '벌스 시작'이나 '타이틀 임팩트'와 동의어가 아닙니다.
구조적 구간 경계는 귀로 확인해 --title-impact, --verse-start로 입력합니다.
"""
from __future__ import annotations

import argparse
from array import array
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import wave


FPS = 30
OPENING_FRAMES = 18 * FPS
WINDOW_MS = 20


def _read_mono_pcm(path: Path) -> tuple[int, list[float]]:
    """PCM 16비트 모노 WAV를 20ms RMS 윈도우로 요약합니다."""
    with wave.open(str(path), "rb") as audio:
        channels, width, rate = audio.getnchannels(), audio.getsampwidth(), audio.getframerate()
        if channels != 1 or width != 2 or rate < 8000:
            raise ValueError("16비트 모노 PCM WAV가 필요합니다 (일반 파일은 FFmpeg로 변환).")
        window = max(1, round(rate * WINDOW_MS / 1000))
        powers: list[float] = []
        while True:
            raw = audio.readframes(window)
            if not raw:
                break
            samples = array("h")
            samples.frombytes(raw)
            if sys.byteorder != "little":
                samples.byteswap()
            if not samples:
                break
            # 실제 스트리밍 오디오 기준 정규화
            power = math.sqrt(sum(x * x for x in samples) / len(samples)) / 32768
            powers.append(power)
    return rate, powers


def _decode_audio(path: Path, temp: Path) -> Path:
    """외부 업로드 없이 로컬 FFmpeg로 모든 입력을 16kHz mono WAV로 정규화."""
    if not path.is_file():
        raise FileNotFoundError(path)
    executable = shutil.which("ffmpeg")
    if not executable:
        raise RuntimeError("FFmpeg가 필요합니다: macOS에서 brew install ffmpeg")
    cmd = [
        executable, "-nostdin", "-v", "error", "-y", "-i", str(path),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        "-t", "900", str(temp),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("오디오 디코딩 실패: " + (exc.stderr or "")[-800:]) from exc
    return temp


def onset_candidates(powers: list[float], limit: int = 15,
                     min_spacing_sec: float = 0.18) -> list[dict]:
    """이전 윈도우 대비 RMS 상승으로 어택 후보를 찾아 점수 순위로 반환.

    BPM 검출·곡 구조 인식이 아닌 단순 오디오 이벤트 탐지입니다.
    """
    if limit <= 0 or len(powers) < 5:
        return []
    attacks = []
    for idx in range(4, len(powers)):
        baseline = sum(powers[idx - 4:idx]) / 4
        novelty = max(0.0, powers[idx] - baseline)
        if novelty > 0.015:
            attacks.append((idx, novelty))
    attacks.sort(key=lambda item: (-item[1], item[0]))
    used: list[int] = []
    for idx, _ in attacks:
        if all(abs(idx - prev) * WINDOW_MS / 1000 >= min_spacing_sec for prev in used):
            used.append(idx)
            if len(used) >= limit:
                break
    scores = dict(attacks)
    return [
        {"time_sec": round(idx * WINDOW_MS / 1000, 3),
         "frame": round(idx * WINDOW_MS / 1000 * FPS),
         "attack_score": round(scores[idx], 5)}
        for idx in sorted(used)
    ]


def validate_markers(title_sec: float, verse_sec: float,
                     fps: int = FPS, opening_frames: int = OPENING_FRAMES) -> dict:
    if (not math.isfinite(title_sec) or not math.isfinite(verse_sec) or
            title_sec <= 0 or verse_sec <= title_sec):
        raise ValueError("0 < 타이틀 임팩트 < 벌스 시작이 되도록 입력해야 합니다.")
    impact = round(title_sec * fps)
    verse = round(verse_sec * fps)
    if not (2 <= impact < verse < opening_frames):
        raise ValueError("프레임 변환 후 유효한 시작·타이틀·벌스 구간이 필요합니다 (18초 데모).")
    if verse - impact < 15:
        raise ValueError("타이틀을 읽을 시간을 최소 0.5초 이상 확보해야 합니다.")
    return {"matchcutEndFrame": impact, "verseStartFrame": verse}


def analyse_audio(path: Path, title_sec: float | None = None,
                  verse_sec: float | None = None) -> dict:
    if (title_sec is None) != (verse_sec is None):
        raise ValueError("--title-impact와 --verse-start는 함께 지정해야 합니다.")
    with tempfile.TemporaryDirectory(prefix="sua-audio-") as dirname:
        decoded = _decode_audio(path, Path(dirname) / "track.wav")
        rate, powers = _read_mono_pcm(decoded)
    result = {
        "schema_version": 1,
        "source_name": path.name,  # 절대 경로나 내부 개인정보는 보고서에 기록하지 않음
        "duration_estimate_sec": round(len(powers) * WINDOW_MS / 1000, 3),
        "sample_rate": rate,
        "onset_candidates": onset_candidates(powers),
        "review_required": True,
        "note": "어택 후보만 자동 추출합니다. 벌스/코러스/임팩트 의미 판정은 사용자가 확정해야 합니다.",
        "selected_markers": None,
    }
    if title_sec is not None and verse_sec is not None:
        if verse_sec > result["duration_estimate_sec"]:
            raise ValueError("음원 길이보다 벌스 시작 시점이 늦습니다.")
        result["selected_markers"] = validate_markers(title_sec, verse_sec)
    return result


def merge_props(props_path: Path, markers: dict,
                music_relative: str | None = None) -> None:
    """원래 imagePaths를 보존하고 시간 설정만 갱신합니다."""
    props = json.loads(props_path.read_text(encoding="utf-8"))
    if not isinstance(props, dict) or not isinstance(props.get("imagePaths"), list):
        raise ValueError("sua-matchcut이 생성한 props JSON이 필요합니다.")
    if music_relative is not None:
        if (not music_relative.startswith("media/music/") or
                ".." in Path(music_relative).parts or "\\" in music_relative or
                music_relative.endswith("/")):
            raise ValueError("--music-relative은 video/public/media/music 내부의 상대 경로만 허용합니다.")
        props["musicPath"] = music_relative
    props["timing"] = markers
    props_path.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Suno 등 로컬 오디오 어택 후보/편집 마커 분석")
    parser.add_argument("audio", type=Path, help="로컬 음원 (MP3, WAV 등)")
    parser.add_argument("--out", type=Path, default=Path("data/audio-cues.json"))
    parser.add_argument("--title-impact", type=float, default=None,
                        help="타이틀 임팩트 초 (귀로 검토한 값)")
    parser.add_argument("--verse-start", type=float, default=None,
                        help="벌스 시작 초 (귀로 검토한 값)")
    parser.add_argument("--props", type=Path, default=None,
                        help="기존 data/opening-props.json (승인 마커가 있을 때만 수정)")
    parser.add_argument("--music-relative", default=None,
                        help="video/public 기준 경로: media/music/intro.wav")
    args = parser.parse_args()
    result = analyse_audio(args.audio, args.title_impact, args.verse_start)
    if args.props is not None and result["selected_markers"] is None:
        parser.error("--props 사용 시 --title-impact와 --verse-start가 필요합니다.")
    if args.music_relative is not None and args.props is None:
        parser.error("--music-relative은 --props와 함께 사용해야 합니다.")
    if args.props is not None:
        merge_props(args.props, result["selected_markers"], args.music_relative)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"오디오 어택 후보 {len(result['onset_candidates'])}개 기록: {args.out}")
    if result["selected_markers"] is None:
        print("편집 시점 미확정: --title-impact / --verse-start로 직접 확인한 초를 입력하세요.")


if __name__ == "__main__":
    main()
