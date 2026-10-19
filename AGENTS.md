# Agent instructions — Sua's First Birthday

## Mission
Produce a professional, family-approved first-birthday growth video using source media gathered through Google Drive. Preserve provenance and privacy. This is a **local-first** project.

## Absolute rules
1. Never change, move, delete, rename, or deduplicate original media in place.
2. Never push source media, previews, OAuth secrets, Drive indices, or generated manifests to GitHub.
3. Do not upload personal media to remote AI APIs/services without explicit consent.
4. Do not infer uncertain capture dates as established facts. Record source, precision, and confidence. KakaoTalk timestamps may represent forwarding or saving.
5. Do not automatically discard visually similar frames, even when perceptual hashes match.
6. Ask for human confirmation when chronology or identity is ambiguous; avoid ranking a child's face by an opaque aesthetic score.
7. Face alignment must be **geometric only** by default, not generative face alteration.
8. Never silently add third-party copyrighted music or unlicensed assets.

## Architecture
- \`src/sua_media/catalog.py\`: local scan, date inference, duplicate candidate catalog.
- \`src/sua_media/drive.py\`: **download-only** read-only OAuth Google Drive ingestion.
- \`src/sua_media/faces.py\`: optional YuNet/landmark geometric aligner for selected photos.
- \`video/\`: Remotion preview and rendering scaffold.
- \`assets/\`, \`data/\`, \`output/\`, \`.secrets/\`: local, ignored personal data.

## Local workflow
1. \`python -m pip install -e ".[images,drive,vision]"\`.
2. Prefer a fully offline-available Drive desktop folder; otherwise run \`sua-drive\` after explicit local OAuth configuration.
3. \`sua-media <downloaded-directory> --out data/manifest.json\`.
4. Inspect duplicate candidates, uncertain dates, and representative frames before selecting media.
5. Run \`sua-face-align\` on a reviewed subset; check each image manually.
6. Build a storyboard and then Remotion edit. Render a small preview before 1080p output.
7. \`python -m unittest discover -s tests -v\` and \`cd video && npm run typecheck\`.

## Codex / Remotion
Read current official Remotion Agent Skills before advanced animation work:
\`npx -y skills@latest add remotion-dev/skills -g -y\`.
Develop reusable comps for opening, age chapters, match-cut, parents' message, and ending.
Do not render user data in public CI.

## Deliverable quality
Story-led editing, 16:9 1080p, readable Korean text, consistent design, intentional audio mixing, still-image motion used sparingly, clean transitions, no stretched/cropped faces or black frames. Playback-test on the venue's equipment.
