"""Explicitly approved aligned photo frames -> local Remotion input props.

No source file is deleted or overwritten; only requested aligned PNGs are copied.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil


def prepare_matchcut(report_path: Path, approved_path: Path, media_dir: Path,
                     props_path: Path, music_path: str = "") -> dict:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    approval = json.loads(approved_path.read_text(encoding="utf-8"))
    names = approval.get("approved_outputs")
    if not isinstance(names, list) or not names or not all(isinstance(n, str) for n in names):
        raise ValueError('승인 파일에는 비어 있지 않은 "approved_outputs" 문자열 배열이 필요합니다.')
    if len(names) != len(set(names)):
        raise ValueError("동일한 프레임을 중복 승인할 수 없습니다.")
    indexed = {
        item["output"]: item for item in report["items"]
        if item.get("status") == "aligned" and item.get("output")
    }
    dates = [indexed[name].get('captured_at') for name in names if name in indexed]
    if len(dates) == len(names) and all(isinstance(d, str) and d for d in dates):
        if dates != sorted(dates, reverse=True):
            raise ValueError('역순 매치컷은 최근 → 출생 촬영일 내림차순으로 승인해야 합니다.')
    candidates: list[Path] = []
    for name in names:
        if Path(name).name != name or name not in indexed:
            raise ValueError(f"보고서에 없거나 유효하지 않은 승인 프레임: {name}")
        original = (report_path.parent / name).resolve()
        if original.parent != report_path.parent.resolve() or not original.is_file():
            raise ValueError(f"승인 프레임 파일을 찾을 수 없습니다: {name}")
        candidates.append(original)

    media_dir.mkdir(parents=True, exist_ok=True)
    result_paths: list[str] = []
    for original in candidates:
        destination = media_dir / original.name
        shutil.copy2(original, destination)
        # Remotion's staticFile paths are relative to video/public.
        result_paths.append("media/matchcut/" + original.name)

    props = {"imagePaths": result_paths, "musicPath": music_path}
    props_path.parent.mkdir(parents=True, exist_ok=True)
    props_path.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")
    return props


def main() -> None:
    parser = argparse.ArgumentParser(description="최근 → 출생 역순으로 승인한 얼굴 정렬 사진을 로컬 프리뷰에 반영")
    parser.add_argument("--report", type=Path, default=Path("output/faces/report.json"))
    parser.add_argument("--approved", type=Path, default=Path("data/approved-matchcut.json"))
    parser.add_argument("--public-dir", type=Path, default=Path("video/public/media/matchcut"))
    parser.add_argument("--props", type=Path, default=Path("data/opening-props.json"))
    parser.add_argument("--music", default="", help="선택: video/public에 상대적인 오디오 경로")
    args = parser.parse_args()
    result = prepare_matchcut(args.report, args.approved, args.public_dir, args.props, args.music)
    print(f"승인 사진 {len(result['imagePaths'])}장 준비 완료: {args.props}")


if __name__ == "__main__":
    main()
