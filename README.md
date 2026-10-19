# Sua's First Birthday Anniversary

Privacy-first, **local-first** family media pipeline for a first-birthday film. This repository contains **code only**. Never upload family photos, videos, authentication secrets, or generated manifests to GitHub.

## What works in this scaffold

- Read photos/videos from a local directory, including a fully downloaded **Google Drive for desktop** folder.
- Read capture timestamps from ExifTool, fall back to filenames, and preserve uncertainty instead of inventing dates.
- Compute streaming SHA-256 for exact duplicates; optionally flag visually similar images with perceptual hashes. **No source files are deleted.**
- Produce a chronological JSON manifest, with undated media kept at the end for human review.
- Optionally download media recursively from a shared Drive folder with **read-only OAuth**.
- Optionally face-align selected images using OpenCV YuNet for a growth match-cut (manual review still required).
- Start a Remotion video project with an original, editable placeholder composition.

## Vendor research and original motion-template previews

Publicly documented first-birthday video references were compared in [Market Research](docs/MARKET_RESEARCH_2026-10.md), with the proposed **4-minute story plan** in [Template Spec](docs/TEMPLATE_SPEC.md).

Three original **24-second synthetic design previews** are included; none includes private family media or reproduces a commercial vendor's graphics:

- `CinematicPreview` — documentary / minimalist typography
- `ScrapbookPreview` — paper collage / polaroid styling
- `VarietyPreview` — bold captions / energetic motion

~~~bash
cd video
npm install
npm run dev
# Select any Preview composition in Remotion Studio.
npx remotion render src/index.ts CinematicPreview out/cinematic-demo.mp4
~~~

For alternative renders and details, see [video/README.md](video/README.md). These are **style explorations**, not the final edited 4-minute film.

## Requirements

Python 3.11+, Node.js 20+, FFmpeg, ExifTool (recommended), and a local disk with enough space for downloads and rendering.

On macOS:

~~~bash
brew install ffmpeg exiftool
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[images,drive,vision]"
~~~

For **local Google Drive for desktop** sync, make the shared folder/files available offline first, then analyze the downloaded path:

~~~bash
sua-media "/path/to/Google Drive/Family Birthday Uploads" --out data/manifest.json
~~~

This creates a manifest of file paths, hashes, dates, provenance, exact duplicate groups, and visual-similarity candidates. Original media are not copied, altered, renamed, or deleted. A filename-derived date is a **clue**, particularly for KakaoTalk downloads; it is not automatically the camera's capture date.

### Optional: direct read-only Drive download

1. Create a Google Cloud project, enable **Google Drive API**, configure OAuth consent and a **Desktop** OAuth client, and save the downloaded credentials as `credentials.json` **locally**.
2. Ensure the OAuth Google account has access to the shared folder.
3. Locate its folder ID in the URL.
4. Run:

~~~bash
sua-drive YOUR_FOLDER_ID --credentials credentials.json --token .secrets/drive-token.json --out assets/incoming/drive --index data/drive-index.json
sua-media assets/incoming/drive --out data/manifest.json
~~~

The sync is **download-only**, skips Google-native docs, and does not delete local or Drive files. It names downloads with the Drive file ID to avoid collisions and writes an index mapping to original names and IDs. Token and all media directories are gitignored. Google Drive OAuth may require consent-screen setup or test-user registration.

### Optional: face-aligned growth match-cut

Download the OpenCV YuNet ONNX model to `models/face_detection_yunet_2023mar.onnx` from [opencv_zoo](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet). Model files are not committed.

~~~bash
sua-face-align --manifest data/manifest.json --model models/face_detection_yunet_2023mar.onnx --out output/faces
~~~

This writes aligned PNGs and `report.json`. Photos with undetectable faces or multiple people need human review; output remains local. Face alignment transforms existing photos; it does not synthesize a new face.

### Video scaffold

~~~bash
cd video
npm install
npm run dev
# Later, after putting approved media in video/public/media:
npm run render
~~~

Video defaults to a simple 1920x1080, 30-fps placeholder. It is **not** yet an edited birthday film. The second phase adds a reviewed storyboard, scene timeline, audio, and actual media selections.

## Safety

- Keep this repository **private if possible**, even though original files are ignored; commit only code and anonymized fixtures.
- Do **not** paste private Drive folder URLs, OAuth tokens, identifying metadata, or family media into GitHub issues.
- Never run automated destructive deduplication against source files. Only exclude copies in the eventual edit decision manifest.
- AI code execution must use local paths and **must not upload media to external AI APIs**.
- Treat timestamp and facial-position inferences as provisional and verify representative outputs.

## Tests

~~~bash
python -m unittest discover -s tests -v
cd video && npm install && npm run typecheck
~~~

Project operating instructions: [AGENTS.md](AGENTS.md). Planned work is tracked in GitHub issues.
