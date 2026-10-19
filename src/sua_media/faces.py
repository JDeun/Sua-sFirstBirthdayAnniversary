"""Geometric face alignment for a growth match-cut; never generates new faces."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def alignment_matrix(eyes: list[list[float]], width: int, height: int):
    """Return 2x3 similarity transform mapping eye centers to stable anchors."""
    try:
        import numpy as np
    except ImportError as error:
        raise RuntimeError("Install vision support: pip install -e '.[vision]'") from error
    ordered = sorted(eyes, key=lambda point: point[0])
    a, b = np.array(ordered[0], dtype=float), np.array(ordered[1], dtype=float)
    delta = b - a
    distance = float(np.linalg.norm(delta))
    if distance < 1:
        raise ValueError("Eye landmark separation too small")
    angle = -math.atan2(delta[1], delta[0])
    scale = (width * 0.22) / distance
    cos, sin = math.cos(angle) * scale, math.sin(angle) * scale
    rotate = np.array([[cos, -sin], [sin, cos]], dtype=float)
    target = np.array([width * 0.5, height * 0.43])
    shift = target - rotate @ ((a + b) / 2.0)
    return np.column_stack((rotate, shift))


def select_time_spread(rows: list[dict], maximum: int) -> list[dict]:
    """월별로 골고루 후보를 배분해 초반 사진만 몰리는 현상을 방지합니다.

    검출 성공/아이 본인 여부의 판정이 아니라 분석할 *후보* 추출입니다.
    """
    if maximum < 1:
        raise ValueError("--max는 1 이상이어야 합니다.")
    candidates = sorted(
        (row for row in rows if row.get("kind") == "photo"
         and row.get("captured_at") and not row.get("duplicate_of")),
        key=lambda row: (row["captured_at"], row["relative_path"]),
    )
    buckets: dict[str, list[dict]] = {}
    for row in candidates:
        key = row["captured_at"][:7]
        buckets.setdefault(key, []).append(row)
    selected: list[dict] = []
    # 매 순회에서 각 촬영 월당 1장씩 선택해 최신 시기에도 후보가 남도록 함.
    while len(selected) < maximum and any(buckets.values()):
        for month in sorted(buckets):
            if len(selected) >= maximum:
                break
            if buckets[month]:
                selected.append(buckets[month].pop(0))
    return sorted(selected, key=lambda row: (row["captured_at"], row["relative_path"]))


def face_align_manifest(manifest: Path, model: Path, out: Path, maximum: int = 80) -> dict:
    try:
        import cv2
        import numpy as np
        from PIL import Image, ImageOps
    except ImportError as error:
        raise RuntimeError("Install vision support: pip install -e '.[vision]'") from error
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass

    if not model.is_file():
        raise FileNotFoundError("Download the OpenCV YuNet ONNX model to models/ first.")
    rows = json.loads(manifest.read_text(encoding="utf-8"))["media"]
    out.mkdir(parents=True, exist_ok=True)
    report = []
    detector = cv2.FaceDetectorYN.create(str(model), "", (320, 320), 0.8, 0.3, 5000)

    selected = select_time_spread(rows, maximum)
    for index, row in enumerate(selected):
        path = Path(row["path"])
        info = {"source": row["relative_path"], "captured_at": row["captured_at"]}
        try:
            with Image.open(path) as original:
                rgb = np.asarray(ImageOps.exif_transpose(original).convert("RGB"))
            h, w = rgb.shape[:2]
            ratio = min(1, 640 / max(h, w))
            preview = cv2.resize(rgb, (max(1, round(w * ratio)), max(1, round(h * ratio))))
            small = cv2.cvtColor(preview, cv2.COLOR_RGB2BGR)
            sh, sw = small.shape[:2]
            detector.setInputSize((sw, sh))
            _, faces = detector.detect(small)
            if faces is None or len(faces) == 0:
                info["status"] = "no_face"
            else:
                # FaceDetectorYN returns bbox [0:4], right/left eye at [4:8].
                selected_face = max(faces, key=lambda f: float(f[2] * f[3]))
                eyes = [[float(selected_face[4]) / ratio, float(selected_face[5]) / ratio],
                        [float(selected_face[6]) / ratio, float(selected_face[7]) / ratio]]
                transform = alignment_matrix(eyes, 1080, 1080)
                rendered = cv2.warpAffine(
                    cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), transform, (1080, 1080),
                    flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101,
                )
                filename = f"{index:04d}_{row['sha256'][:12]}.png"
                if not cv2.imwrite(str(out / filename), rendered):
                    raise OSError("OpenCV failed to write image")
                info.update({"status": "aligned", "output": filename,
                             "face_count": len(faces), "needs_review": len(faces) != 1})
        except (OSError, ValueError, cv2.error) as error:
            info.update({"status": "failed", "reason": str(error)})
        report.append(info)

    summary = {"processed": len(report), "aligned": sum(x["status"] == "aligned" for x in report),
               "manual_review_required": True, "items": report}
    (out / "report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Align selected face photos into local PNG frames.")
    parser.add_argument("--manifest", type=Path, default=Path("data/manifest.json"))
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("output/faces"))
    parser.add_argument("--max", type=int, default=80)
    args = parser.parse_args()
    result = face_align_manifest(args.manifest, args.model, args.out, args.max)
    print(f"Aligned {result['aligned']} of {result['processed']} photos; review {args.out}/report.json")


if __name__ == "__main__":
    main()
