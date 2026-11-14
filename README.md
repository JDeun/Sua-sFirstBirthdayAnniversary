# 성장영상 제작 도구

실제 성장영상 제작에서 사용한 Remotion 렌더러와 로컬 도구를 프로젝트 소유자의 후속 제작에 사용할 수 있도록 정리한 템플릿이다. 원본 미디어와 개인 편집 데이터는 저장소 밖에 둔다.

코드와 문서의 권리는 저장소 소유자가 보유한다. 공개 열람은 이용·복제·수정·재배포·상업 이용 허가를 의미하지 않는다. 자세한 방침은 [LICENSE](LICENSE), 외부 모델·의존성의 별도 조건은 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 있다.

## 구성

| 경로 | 역할 |
| --- | --- |
| `renderer/` | 서사 장면, 파스텔 우주 배경, 매치컷, 키네틱 타이포그래피, 별·왕관·선물 모션 |
| `tools/` | 미디어 목록, 촬영일·중복·편집표 검증, 얼굴 정렬, 비트 분석, 로컬 가사 정렬, 누끼·톤 조정 |
| `schemas/` | 프로젝트와 편집 데이터의 구조 |
| `examples/` | 실제 인물과 음악을 사용하지 않는 도형 예제 |
| `models/` | 최종 사용 모델의 출처·라이선스·고정 SHA256 |
| `scripts/` | 모델 검증과 공개 파일 검사 |
| `docs/legacy-ideas.md` | 초기 스캐폴딩에서 남긴 제작 원칙 |

권장 로컬 배치는 다음과 같다. 개인 파일은 Git 저장소의 형제 폴더에 둔다.

```text
workspace/
  film-template/            # 이 저장소의 코드
  media/
    photos/
    videos/
    audio/
  private/
    project.json
    lyrics.md
    runtime/               # 개인 편집표·가사 시각·문구·정렬값
  work/public/             # 변환 영상·누끼·정렬 사진 등 렌더 자산
  output/                  # 영상·검사 결과
```

## 설치와 프로젝트 준비

Python3.11, Node.js, FFmpeg·FFprobe를 사용한다. 렌더러의 Node 의존성은 lockfile로 설치한다. Python 미디어 도구와 선택적인 가사 정렬 환경은 requirements 파일을 구분한다.

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci --prefix renderer
python3.11 scripts/setup_models.py
```

프로젝트 설정에는 `runtime_directory`, `asset_directory`, `output_directory`, `media_directory`를 넣는다. 이 경로는 설정 파일을 기준으로 해석한다. 미디어 원본의 식별자는 `media/photos/...`, `media/videos/...`처럼 논리 경로를 사용한다.

```json
{
  "runtime_directory": "runtime",
  "asset_directory": "../work/public",
  "output_directory": "../output",
  "media_directory": "../media"
}
```

공개 코드에는 이름·생일·가사·원본 파일 목록을 넣지 않는다. 외부 runtime에는 다음8개 파일을 준비한다.

```text
narrative-edit.json       narrative-media.json
media-exclusions.json     chorus-alignment.json
outro-alignment.json      stopmotion.json
matchcut.json             copy.json
```

검사 후 렌더러에 연결한다. 기본 스테이징은 로컬 링크를 사용하며 `--copy`로 복사할 수도 있다.

```sh
python3.11 tools/prepare_project.py --config ../private/project.json --check
python3.11 tools/prepare_project.py --config ../private/project.json
```

미리보기와 타입 검사를 실행한다.

```sh
npm run typecheck --prefix renderer
npm run dev --prefix renderer
```

실제 가족 자료 없이 도형 예제로 시작할 수 있다. 다른 개인 프로젝트가 연결돼 있으면 해당 프로젝트의 링크를 먼저 분리한다. 새로 받은 저장소에는 다음 명령을 사용한다.

```sh
python3.11 tools/prepare_project.py --config examples/demo/project.json --copy
npm run typecheck --prefix renderer
npm run preflight --prefix renderer
```

헤드리스 출력 명령은 `renderer/scripts/verify-headless.mjs --help`와 렌더러의 `verify:headless` 스크립트를 사용한다. 렌더 브라우저는 렌더러 폴더에서 `npx remotion browser ensure`로 준비한다. 자동 CI는 도형 예제의3프레임만 렌더한다.

## 제작 흐름

1. 원하는 감정선·오프닝·강조 가사·사진 사용 기준을 먼저 정한다.
2. 원본의 해시·촬영일·영상 방향을 조사하고, 가족이 확인한 기념일과 대조한다.
3. 실제 비트와 보컬 시각을 기록한다. 자동 가사 정렬은 청취로 확인한다.
4. 얼굴 매치컷은 눈·얼굴 크기·각도를 정렬하고 잘못된 대상과 방향을 검토한다.
5. 사진과 영상의 서사를 편집표에 배치한다. 준비·행동·반응이 보이도록 사용 구간을 정한다.
6. 문구·가사·타이포그래피와 실제 인물의 크기를 함께 조정한다. 맥락이 필요한 장면은 전체 인물을 보존한다.
7. 편집표를 검사하고 렌더한 뒤, 실제 화면·음량·영상 끝·연속 재생·청취를 검수한다.

각 도구의 옵션은 `python3.11 tools/<도구>.py --help`로 확인한다. 가사 정렬은 선택 환경을 설치하고 [모델 안내](models/README.md)에 따라 로컬 모델을 준비한다. 원본 노래의 속도·음정과 가사 시계를 유지한다.

## 공개 파일 검사

`.gitignore`와 별도로 파일 허용 목록을 검사한다. 원본 미디어·생성 runtime·완성 영상·로컬 절대 경로·개인 파일명·인코딩된 사진은 공개 대상에서 제외한다. 모델은 등록된 SHA256이 일치하는 파일만 허용한다.

```sh
python3.11 scripts/audit_public.py
```

로컬의 실제 가사와 고유 문구도 대조할 수 있다. 이 파일들은 검사에만 읽고 저장소에 포함하지 않는다.

```sh
python3.11 scripts/audit_public.py --lyrics-file ../private/lyrics.md
```
