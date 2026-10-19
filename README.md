# 수아의 첫돌 성장영상 제작 프로젝트

Google Drive에 모인 가족 사진·영상을 **로컬에서 안전하게 수집하고**, 메타데이터로 시간순 정렬한 다음, 얼굴 정렬 매치컷과 Remotion 편집으로 첫돌 영상을 제작하는 프로젝트입니다.

> **중요:** 이 GitHub 저장소는 공개 상태입니다. 가족 사진·영상, Google Drive 접근 토큰, 개인 메타데이터, Suno 원음원 및 최종 렌더링 파일은 절대 GitHub에 올리지 않습니다. 원본은 수정하거나 삭제하지 않습니다.

## 현재 구현 상태

| 항목 | 상태 |
|---|---|
| Google Drive 데스크톱 동기화 폴더 읽기 | 로컬 폴더 스캔 지원 |
| Google Drive API 읽기 전용 OAuth 다운로드 | 코드 구현, 실제 계정 연결 테스트 필요 |
| 사진·영상 EXIF/QuickTime 촬영일과 파일명 추론 | 구현 |
| SHA-256 완전 중복 감지 | 구현, 자동 삭제하지 않음 |
| 사진 해시 기반 유사 장면 후보 | 구현, 사람 검토 필수 |
| 촬영일 기반 JSON 정렬 목록 | 구현 |
| OpenCV YuNet 얼굴 정렬 PNG 생성 | 구현, 실제 영아 사진 검증 필요 |
| **초고속 얼굴 매치컷 → 타이틀 → 벌스** | 18초 Remotion 데모 구현 |
| 시네마틱 / 스크랩북 / 예능형 프리뷰 | 24초 데모 3종 구현 |
| 사진 검토 UI·4분 완성본·음악 비트 분석 | 추후 개발 |

## 먼저 볼 문서

- [제작 방향과 4분짜리 스토리보드](docs/TEMPLATE_SPEC.md)
- [초고속 얼굴 매치컷 오프닝 설계](docs/OPENING_MATCHCUT.md)
- [Suno 직접 제작 음악 작업 가이드](docs/MUSIC_BRIEF.md)
- [기존 돌영상 업체와 템플릿 조사](docs/MARKET_RESEARCH_2026-10.md)
- [시스템 아키텍처와 단계별 개발 계획](docs/ARCHITECTURE.md)
- [Codex 작업 지침](AGENTS.md)
- [Remotion 영상 미리보기](video/README.md)

## Mac에서 설치

Python 3.11+, Node.js 20+, FFmpeg, ExifTool이 필요합니다.

~~~bash
brew install ffmpeg exiftool
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[images,drive,vision]"
~~~

## 1단계 — 가족 사진·영상 수집과 정렬

Google Drive에서 공유 폴더를 만들고, 가족 및 지인에게 **원본 파일을 업로드**하도록 안내합니다. Google Drive 데스크톱 앱으로 자료를 내려받고 *오프라인에서 사용 가능*하도록 준비한 뒤 다음 명령을 실행합니다.

~~~bash
sua-media "/로컬/구글드라이브/공유폴더" --out data/manifest.json
~~~

촬영 메타데이터가 없으면 파일명으로 추정합니다. 카카오톡 파일명의 날짜는 *촬영일이 아닌 저장·전달일일 수 있으므로 신뢰도를 낮게 기록*합니다. 알 수 없는 날짜는 임의로 만들지 않습니다.

중복은 원본에서 삭제하지 않고 JSON에 중복 여부와 비슷한 사진 후보를 표시합니다.

### 선택 — Google Drive API로 직접 받기

1. Google Cloud 프로젝트에서 Google Drive API를 활성화합니다.
2. OAuth 동의 화면 및 데스크톱 OAuth 클라이언트를 만든 후, 발급된 JSON을 로컬의 `credentials.json`으로 저장합니다.
3. 사용 계정에 공유 폴더 접근 권한을 부여합니다.
4. 브라우저에 보이는 폴더 ID로 아래 명령을 실행합니다.

~~~bash
sua-drive 폴더ID --credentials credentials.json \
  --token .secrets/drive-token.json \
  --out assets/incoming/drive --index data/drive-index.json
sua-media assets/incoming/drive --out data/manifest.json
~~~

읽기 전용 다운로드입니다. 원격 파일을 수정하거나 삭제하지 않습니다. Drive의 수정 시각은 실제 촬영 시각으로 간주하지 않습니다.

## 2단계 — 얼굴 정렬 매치컷 준비

[OpenCV YuNet 모델](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet)을 내려받아 `models/face_detection_yunet_2023mar.onnx`에 저장합니다.

~~~bash
sua-face-align --manifest data/manifest.json \
  --model models/face_detection_yunet_2023mar.onnx \
  --out output/faces
~~~

`output/faces/report.json`과 생성된 사진을 **사람이 검토**합니다. 원본의 아이가 아닌 다른 얼굴이 선택되거나 검출에 실패할 수 있습니다.

승인한 사진 목록을 `data/approved-matchcut.json` 파일로 만듭니다. 형식은 [예시](examples/approved-matchcut.example.json)를 참고하세요. **목록 순서가 재생 순서**이므로 출생부터 현재까지 직접 확인한 시간순으로 작성합니다.

~~~bash
sua-matchcut --report output/faces/report.json \
  --approved data/approved-matchcut.json \
  --public-dir video/public/media/matchcut \
  --props data/opening-props.json
~~~

선택한 정렬본만 **로컬** `video/public/media/matchcut` 폴더로 복사합니다. 원본은 그대로 유지합니다.

## 3단계 — 영상 프리뷰

~~~bash
cd video
npm install
npm run dev
~~~

Remotion Studio에서 다음 작품을 골라 볼 수 있습니다.

- **OpeningSequence:** 0~9초 수십 장 매치컷 가속 → 9~12초 타이틀 → 12초부터 벌스 느낌의 본편 시작. 기본 48장 가상 그래픽 데모.
- **CinematicPreview / ScrapbookPreview / VarietyPreview:** 서로 다른 디자인 24초 데모.
- **BirthdayPreview:** 초기 20초 플레이스홀더.

실제 승인 프레임을 반영하려면 저장소 루트 기준:

~~~bash
cd video
npx remotion render src/index.ts OpeningSequence out/opening.mp4 \
  --props=../data/opening-props.json
~~~

직접 만든 음악을 쓰려면 `video/public/media/music/intro.wav`에 복사한 뒤, `sua-matchcut`에 `--music media/music/intro.wav`를 추가하여 props를 다시 생성합니다. 오디오는 공개 저장소에 올리지 않습니다.

**현재 코드는 18초 오프닝 데모이며, 4분짜리 실제 완성 영상은 아닙니다.** 음악의 실제 벌스 시작 시점에 맞춰 프레임 타이밍을 조정해야 합니다.

## 개인정보·저작권·안전

- Google Drive의 공유 권한은 꼭 필요한 사람에게만 줍니다.
- GitHub에 올려야 하는 자료는 소스코드와 **합성 테스트 자료**만입니다.
- 가족의 얼굴을 외부 이미지/AI API에 자동 전송하지 않습니다.
- 원본을 삭제하거나 임의 변경하지 않으며 시각적 중복은 자동 삭제하지 않습니다.
- 음악은 직접 제작하되 이용 범위·계정 플랜·상영/게시 조건을 확인합니다.
- 최종 영상은 행사장 화면비와 재생 기기에서 직접 검수합니다.

## 테스트

~~~bash
python -m unittest discover -s tests -v
cd video
npm install
npm run typecheck
npx remotion compositions src/index.ts
~~~

문의 없이 Codex가 작업을 이어갈 수 있도록 [AGENTS.md](AGENTS.md)에 절차를 정리했습니다.
