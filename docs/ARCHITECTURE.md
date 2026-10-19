# Architecture and planned phases

## Data flow
Trusted family contributors -> private shared Google Drive folder -> local Drive desktop cache OR read-only Drive API downloader -> immutable local media -> JSON inventory -> human review -> optional geometric match-cut frames -> Remotion composition -> local H.264/AAC export.

## Phase 0: Safety and repeatability (this PR)
- Code-only public repository; privacy-oriented .gitignore.
- Source-file preservation and cryptographic exact duplicate detection.
- Timestamp precedence (embedded > filename > unknown), no destructive cleanup.
- Fully local CLI and opt-in Drive downloader.
- Optional face-alignment pipeline and Remotion preview scaffold.

## Phase 1: Curation
- Generate contact sheets (images) and representative frames (videos).
- Create a local-only review app to select/skip media, fix date buckets, and mark important moments.
- Link Drive provenance metadata to media manifest after sync; do not confuse Drive modifiedTime with capture time.
- Add regression fixtures for timezone conversions, duplicate HEIC/JPEG exports, downloaded file names, and video transcodes.

## Phase 2: Editing
- Define stable JSON storyboard schema with ordered segments, duration, captions, transitions, and audio.
- Integrate approved media with Remotion, handling aspect ratio and mixed HDR/SDR.
- Build a face-aligned match-cut segment from manually confirmed photos.
- Add typography system and licensed BGM; render and inspect frame samples.

## Phase 3: Quality
- Automated black/silent frame checks, duration, audio loudness, dropped media detection, and visual inspection report.
- Validate 1080p/30fps H.264/AAC MP4 on actual venue hardware.
- Avoid pushing private footage or screenshots to CI artifacts.

## Remaining design risks
- Google Drive desktop streaming may be a placeholder until made available offline.
- Metadata may be stripped by KakaoTalk, exported images, or transcoding.
- YuNet can mis-detect infant/side-profile faces and select the wrong face when multiple are present.
- A perceptual hash is only a review hint; no automated deletion.
- Mixed phone HDR and portrait video require a tested SDR normalization/crop strategy.
