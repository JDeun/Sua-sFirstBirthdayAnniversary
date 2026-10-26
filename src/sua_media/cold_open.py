"""음원 분석 없이 콜드 오픈 컷/타이틀/완성곡 시작 시점을 설정합니다."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


FPS = 30
DEMO_FRAMES = 21 * FPS


def valid_local_media(value: str) -> str:
    """Remotion video/public/media 아래에만 허용합니다."""
    if not value or not value.startswith("media/") or "\\" in value:
        raise ValueError("미디어 파일은 video/public/media/ 상대 경로여야 합니다.")
    parts = Path(value).parts
    if ".." in parts or "." in parts or any(not part for part in parts):
        raise ValueError("상위 디렉터리 이동을 허용하지 않습니다.")
    if value.endswith("/"):
        raise ValueError("파일 이름을 지정해야 합니다.")
    return value


def cold_open_markers(title_at: float, song_start: float, birth_at: float = 8.0,
                      fps: int = FPS, demo_frames: int = DEMO_FRAMES) -> dict[str, int]:
    """콜드 오픈 비디오 타임라인만 설정. 실제 곡의 벌스 위치와 무관합니다."""
    if not all(math.isfinite(x) for x in (title_at, song_start, birth_at)):
        raise ValueError("유한한 시간 값을 입력하세요.")
    if not 0 < birth_at < title_at < song_start:
        raise ValueError("0 < 타이틀 시점 < 완성곡 시작 시점이어야 합니다.")
    birth_frame = round(birth_at * fps)
    title_frame = round(title_at * fps)
    song_frame = round(song_start * fps)
    if title_frame < 2 or song_frame >= demo_frames:
        raise ValueError("현재 21초 미리보기 안에서 설정하세요.")
    if song_frame - title_frame < 15:
        raise ValueError("타이틀은 최소 0.5초 이상 표시해야 합니다.")
    return {"matchcutEndFrame": birth_frame, "birthEndFrame": title_frame, "songStartFrame": song_frame}


def configure_cold_open(props_path: Path, title_at: float, song_start: float,
                        music_path: str | None = None,
                        montage_sfx: str | None = None,
                        title_sfx: str | None = None,
                        birth_at: float = 8.0, birth_video: str | None = None,
                        birth_source_start: float = 0.0, birth_audio: bool = False) -> dict:
    """기존 승인 사진 목록을 유지하면서 비디오 마커와 선택적 로컬 효과음을 수정."""
    original = json.loads(props_path.read_text(encoding="utf-8"))
    if not isinstance(original, dict) or not isinstance(original.get("imagePaths"), list):
        raise ValueError("sua-matchcut에서 생성한 opening-props.json이 필요합니다.")
    # 모든 입력 검증이 끝난 뒤 하나의 파일을 작성합니다.
    markers = cold_open_markers(title_at, song_start, birth_at)
    music = valid_local_media(music_path) if music_path is not None else original.get("musicPath", "")
    if montage_sfx is None and title_sfx is None:
        effects = original.get("soundEffects", {})
    else:
        effects = dict(original.get("soundEffects", {}))
        if montage_sfx is not None:
            effects["montagePath"] = valid_local_media(montage_sfx)
        if title_sfx is not None:
            effects["titleImpactPath"] = valid_local_media(title_sfx)
    updated = dict(original)
    updated["timing"] = markers
    updated["musicPath"] = music
    updated["soundEffects"] = effects
    if birth_video is not None:
        if not math.isfinite(birth_source_start) or birth_source_start < 0:
            raise ValueError("탄생 영상 시작 시점은 0 이상의 유한한 값이어야 합니다.")
        if not birth_video.lower().endswith((".mp4", ".mov", ".m4v")):
            raise ValueError("탄생 영상은 mp4/mov/m4v 형식이어야 합니다.")
        updated["birthClip"] = {"path": valid_local_media(birth_video), "sourceStartFrame": round(birth_source_start * FPS), "withAudio": bool(birth_audio)}
    props_path.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="무음/효과음 콜드 오픈과 Suno 완성곡 시작 시점을 편집")
    parser.add_argument("--props", type=Path, default=Path("data/opening-props.json"))
    parser.add_argument("--title-at", type=float, default=12.0,
                        help="탄생 영상 종료·타이틀 등장 시점(초)")
    parser.add_argument("--song-start", type=float, default=15.0,
                        help="Suno 완성곡의 0:00 재생 시작 시점(초)")
    parser.add_argument("--music", default=None,
                        help="선택: video/public 기준 media/music/song.wav")
    parser.add_argument("--montage-sfx", default=None,
                        help="선택: video/public 기준 media/sfx/montage.wav")
    parser.add_argument("--title-sfx", default=None,
                        help="선택: video/public 기준 media/sfx/title-hit.wav")
    parser.add_argument("--birth-at", type=float, default=8.0)
    parser.add_argument("--birth-video", default=None, help="로컬 video/public/media/... mp4/mov")
    parser.add_argument("--birth-source-start", type=float, default=0.0)
    parser.add_argument("--birth-audio", action="store_true")
    args = parser.parse_args()
    result = configure_cold_open(
        args.props, args.title_at, args.song_start,
        args.music, args.montage_sfx, args.title_sfx,
        args.birth_at, args.birth_video, args.birth_source_start, args.birth_audio,
    )
    print(f"콜드 오픈: 매치컷 {result['timing']['matchcutEndFrame']}프레임 종료, "
          f"완성곡 {result['timing']['songStartFrame']}프레임 시작. "
          f"기존 사진 순서 보존. {args.props}")


if __name__ == "__main__":
    main()
