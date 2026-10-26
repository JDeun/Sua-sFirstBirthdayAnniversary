# 수아의 첫돌 성장영상 제작 프로젝트

> **2026-10-26 오프닝 연출 변경:** 최종 목표는 **현재 얼굴 → 출생 시점으로 역순 매치컷(0–8초) → 실제 탄생 동영상(8–12초) → 타이틀(12–15초) → 완성곡 0초부터 순방향 본편(15초~)**입니다. 기존 README 아래의 9/12초 실행 예시와 18초 데모는 **아직 변경 전 구현**입니다. 코드/테스트 동기화 작업은 남아 있습니다. 상세: [오프닝 변경 명세](docs/OPENING_MATCHCUT.md).

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
| **무음/효과음 얼굴 매치컷 → 타이틀 → Suno 완성곡 시작** | 18초 Remotion 데모 구현 |
| 시네마틱 / 스크랩북 / 예능형 프리뷰 | 24초 데모 3종 구현 |
| 사진 검토 UI·4분 완성본·음악 비트 분석 | 추후 개발 |

## 먼저 볼 문서

- [제작 방향과 4분짜리 스토리보드](docs/TEMPLATE_SPEC.md)
- [초고속 얼굴 매치컷 오프닝 설계](docs/OPENING_MATCHCUT.md)
- [Suno 직접 제작 음악 작업 가이드](docs/MUSIC_BRIEF.md)
- [awesome-ai-motion 활용 검토](docs/MOTION_LIBRARY.md)
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

- **OpeningSequence:** 0~9초 수십 장 매치컷 가속 → 9~12초 타이틀 → 12초부터 Suno 완성곡을 0초부터 재생하며 본편 시작. 기본 48장 가상 그래픽 데모.
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

## Suno 웹에서 곡 완성 → 콜드 오픈 후 재생

**Suno에 영상용 라이저나 프리코러스를 강제로 만들 필요가 없습니다.**
영상 첫 9초는 수십 장 얼굴 정렬 매치컷(무음 또는 선택 효과음), 다음 3초는 타이틀이고,
그 뒤에 **Suno 완성곡을 파일 0초부터** 재생합니다. 실제 음악을 받기 전까지는 데모만 볼 수 있습니다.

~~~bash
# 준비: 로컬에만 video/public/media/music/suno-final.wav 파일 보관
sua-matchcut --approved data/approved-matchcut.json
sua-cold-open --props data/opening-props.json \
  --title-at 9 --song-start 12 \
  --music media/music/suno-final.wav

cd video
npx remotion render src/index.ts OpeningSequence out/opening.mp4 \
  --props=../data/opening-props.json
~~~

선택적 효과음: `--montage-sfx media/sfx/montage.wav`, `--title-sfx media/sfx/title.wav`.
효과음은 각 입력 파일을 로컬 `video/public/media/sfx/`에 두어야 합니다.
`sua-audio-cues`는 곡의 어택 분석 보조 도구로 남겨두며, 콜드 오픈에는 필수가 아닙니다.
더 자세한 설명은 [콜드 오픈 명세](docs/OPENING_MATCHCUT.md)와 [Suno 웹 제작 가이드](docs/MUSIC_BRIEF.md)를 참고하세요.

## awesome-ai-motion 스킬 활용

<https://github.com/gongnyang/awesome-ai-motion>은 Remotion을 대체하는 도구가 아니라 모션 효과의 선택·매개변수·주의사항을 참고하는 가이드입니다. [활용 분석 및 Codex 스킬 연결 절차](docs/MOTION_LIBRARY.md)를 확인하세요. 원본 코드를 자동으로 복제하거나 개인 영상을 외부 서비스에 전송하지 않습니다.

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


## 4단계 — 확정 듀엣곡으로 전체 성장영상 렌더링 (구현 중)

앞의 `OpeningSequence`는 18초 *프리뷰*입니다. 새 `BirthdayFilm`은 승인된 전체 사진/영상 샷과 최종 MP3 길이를 기준으로 전체 타임라인을 생성합니다.

- 최종 기준 음원: `네가 빛날 우주 (2).mp3` (사용자가 선택한 듀엣 버전, 215.04초)
- 무음/효과음 매치컷 9초 → 타이틀 3초 → **Suno 완성곡 0초부터 단 한 번 재생**
- 약 **3분 47초** 영상. 음악의 멜로디·피치·템포·가사는 변경하지 않음
- 사용자 승인한 사진·동영상만 로컬에서 해시 기반 사본으로 준비, 기존 원본은 불변
- `data/approved-story.json`의 순서·가중치에 따라 장면 길이를 곡에 맞춰 자동 배분
- **가족의 실제 미디어를 고르고 검수하는 작업은 아직 남음**

실행 절차, FFprobe 설치, 승인 JSON 형식 및 렌더링 명령은 [전체 영상 제작 가이드](docs/FULL_FILM.md)를 확인하세요.
