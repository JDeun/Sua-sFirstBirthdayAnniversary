"""One-command local-only production: approved EDL -> Remotion -> QA report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from .film import FPS, prepare_film


def produce(*, approved: Path, opening_props: Path, song: Path, public_dir: Path,
            props: Path, output: Path, report: Path, video_dir: Path,
            end_card_seconds: float = 4, normalize_media: bool = False,
            scale: float = 1.0) -> dict:
    if not 0 < scale <= 1:
        raise ValueError("scale must be greater than 0 and at most 1")
    video_dir = video_dir.resolve()
    if not (video_dir / "src" / "index.ts").is_file():
        raise ValueError("video_dir must contain src/index.ts")
    if public_dir.resolve() != (video_dir / "public").resolve():
        raise ValueError("public_dir must be the Remotion project's public directory")
    output = output.resolve()
    report = report.resolve()
    if len({output, report, props.resolve()}) != 3:
        raise ValueError("output, report, and props paths must differ")
    if props.resolve() in {approved.resolve(), opening_props.resolve(), song.resolve()} or report in {approved.resolve(), opening_props.resolve(), song.resolve()} or output in {approved.resolve(), opening_props.resolve(), song.resolve()}:
        raise ValueError("production outputs must not overwrite source inputs")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing render: {output}")
    if report.exists():
        raise FileExistsError(f"Refusing to overwrite existing QA report: {report}")
    if props.exists():
        raise FileExistsError(f"Refusing to overwrite existing film props: {props}")
    if output.suffix.lower() != ".mp4":
        raise ValueError("output must be an .mp4 file")
    data = prepare_film(approved, opening_props, song, public_dir, props,
                        end_card_seconds, normalize_media)
    expected_frames = data["opening"]["timing"]["songStartFrame"] + data["songDurationFrames"]
    output.parent.mkdir(parents=True, exist_ok=True)
    command = ["npx", "--no-install", "remotion", "render", "src/index.ts",
               "BirthdayFilm", str(output), f"--props={props.resolve()}",
               "--codec=h264", f"--scale={scale}"]
    try:
        subprocess.run(command, cwd=video_dir, check=True)
        checker = Path(__file__).resolve().parents[2] / "scripts" / "check_final_render.py"
        if not checker.is_file():
            raise FileNotFoundError(f"Missing QA checker: {checker}")
        report.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, str(checker), str(output),
                        "--expected-frames", str(expected_frames), "--fps", str(FPS),
                        "--report", str(report)], check=True)
    except Exception:
        if output.exists():
            output.unlink()
        raise
    qa = json.loads(report.read_text(encoding="utf-8"))
    if qa.get("status") != "pass":
        output.unlink(missing_ok=True)
        raise RuntimeError(f"Final QA did not pass; see diagnostic report: {report}")
    return {"output": str(output), "report": str(report), "expected_frames": expected_frames,
            "qa": qa}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and verify a private birthday film locally")
    parser.add_argument("--approved", type=Path, required=True)
    parser.add_argument("--opening-props", type=Path, required=True)
    parser.add_argument("--song", type=Path, required=True)
    parser.add_argument("--video-dir", type=Path, default=Path("video"))
    parser.add_argument("--public-dir", type=Path, default=Path("video/public"))
    parser.add_argument("--props", type=Path, default=Path("data/film-props.json"))
    parser.add_argument("--output", type=Path, default=Path("video/out/sua-first-birthday.mp4"))
    parser.add_argument("--report", type=Path, default=Path("data/final-qa.json"))
    parser.add_argument("--end-card-seconds", type=float, default=4)
    parser.add_argument("--normalize-media", action="store_true")
    parser.add_argument("--scale", type=float, default=1.0)
    args = parser.parse_args()
    print(json.dumps(produce(**vars(args)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
