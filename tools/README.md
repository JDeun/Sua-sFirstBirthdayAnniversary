# 로컬 제작 도구

외부의 로컬 입력을 분석·정렬하고 렌더러에 연결한다. 원본 미디어는 변경하지 않는다. Python3.11과 FFmpeg·FFprobe를 사용한다. 수치 분석은 루트 `requirements.txt`, HEIC와 가사 정렬은 별도 선택 requirements를 사용한다.

## 프로젝트 연결

템플릿 루트에서 실행한다.

```sh
python3.11 -B tools/prepare_project.py --config examples/demo/project.json --check
python3.11 -B tools/prepare_project.py --config examples/demo/project.json --copy
python3.11 -B tools/run_tests.py
```

`--check`는 입력만 검사한다. 실제 스테이징은 대상 경로의 충돌도 확인한다. 개인 프로젝트가 이미 연결돼 있으면 다른 프로젝트를 연결하기 전에 해당 링크를 분리하거나 대상 렌더러를 별도로 지정한다. 생성 JSON은 복사하고, 자산은 기본적으로 상대 링크를 사용한다. `--copy`는 자산도 복사한다. 스테이징 도중 실패하면 바꾼 JSON을 복구하고 새 파일을 제거한다.

설정의 각 디렉터리는 설정 파일을 기준으로 해석한다. 명시한 외부 입력 디렉터리는 `..`로 형제 폴더를 선택할 수 있다. 자산 참조와 원본 식별자는 디렉터리 내부의 상대 POSIX 경로다. 원본의 논리 접두어 `media/`는 설정의 `media_directory`에 대응한다. 원본 해시로 이름만 바꾼 중복 사용도 검사한다.

런타임 입력8개는 `filmtools/runtime.py`에 정의한다. 본편 장면에는 실제 맞춤 영역을 포함한 `frameLayout`이 필요하다. 촬영일과 날짜 범위는 외부에서 확인한 사실을 전달한다. 확정된 날짜 역행과 누락은 실패한다. 날짜 정밀도가 겹치면 `chronology_review_required`로 기록하며 `chronology_proven`은 false다. 후렴 몽타주의 날짜 순서는 별도 범위로 검사한다.

## 도구와 입력

| 도구 | 기본 인자 | 기능 |
| --- | --- | --- |
| `catalog_media.py` | `--media-directory DIR --output CATALOG` | EXIF·QuickTime, 방향, 크기, 해시와 중복 후보 |
| `analyze_music.py` | `--audio AUDIO --output MAP` | 측정한 비트·온셋·RMS 에너지 |
| `align_lyrics.py` | `--audio AUDIO --lyrics TEXT --phrases SPEC --language LANG --output CUES --native-output NATIVE` | 고정된 로컬 모델을 이용한 선택적 가사 정렬 |
| `align_faces.py` | `--source PHOTO --output REPORT` | YuNet 얼굴 후보와 눈 좌표 |
| `cutout_subject.py` | `--source PHOTO --annotations JSON --output RGBA.png --report REPORT` | 외부 다각형으로 원본 RGB를 보존한 알파 마스크 |
| `tone_image.py` | `--source PHOTO --parameters JSON --output IMAGE --report REPORT` | 선형 광량 공간에서 제한된 노출·RGB·채도 보정 |
| `validate_project.py` | `--runtime-directory DIR` | 구조·연속성·날짜·원본 중복 검사 |

각 도구의 전체 옵션은 `--help`로 확인한다. `prepare_project.py --check`는 원본·자산의 존재, 해시, 실제 영상의 마지막 소스 프레임 범위도 검사한다.

얼굴 정렬은 `--face-index N --target-eyes LX LY RX RY --aligned-output IMAGE --size W H`로 대상을 명시한다. 정렬 오차는 기하학적 잔차이며 사람·주석의 정확도를 보증하지 않는다. 누끼 주석은 원본을 바르게 세운 `annotation_size` 좌표를 사용하며 전체 캔버스와 RGB를 보존한다. 주석 구조는 `schemas/cutout.schema.json`에 있다.

가사 정렬에는 `--registry`, `--model-directory`, `--from-result`, `--music-map`도 사용할 수 있다. 기존 추정값을 다시 사용해도 음원·텍스트·모델·언어 해시가 일치해야 한다. 구절 구조는 `schemas/lyric-phrases.schema.json`에 있다. 자동 시각과 측정한 비트 위상은 청취로 확인한다.

실제 출력의 끝 프레임은 다음 도구로 검사한다.

```sh
python3.11 tools/check_endpoint_frames.py --edit EDIT --manifest MANIFEST --frames-directory DIR --output REPORT
```

매니페스트에는 `canvas_size: [width, height]`와 `frames: [{shot_id, frame, image}]`가 필요하다. 이미지는 프레임 디렉터리 기준 상대 경로다. 각 본편 영상의 마지막 시점은 `opening.duration_in_frames + shot.song_end_frame - 1`이다. 근거 이미지 누락·중복을 검사하고, 화면의 평탄한 영역은 시각 검토 대상으로 표시한다. 이 신호만으로 빈 영상 여부를 확정하지 않는다.

## 설치 없이 기존 캐시 사용

기존 Python3.11/macOS 휠 캐시가 있다면 읽어서 사용할 수 있다. 변경 가능한 수치 캐시는 지정한 임시 폴더에만 쓴다.

```sh
python3.11 -B tools/cached_runtime.py --scratch-directory /tmp/film-tool-cache tools/run_tests.py
```

`--cache-directory DIR`로 기존 uv 휠 캐시를 지정할 수 있다. 모델 확인과 선택적 다운로드는 `models/README.md`와 `scripts/setup_models.py`를 따른다.

## 파일 목록

템플릿 루트 기준 경로다.


```text
examples/demo/README.md
examples/demo/assets/demo/scene-a.svg
examples/demo/assets/demo/scene-b.svg
examples/demo/project.json
examples/demo/runtime/chorus-alignment.json
examples/demo/runtime/copy.json
examples/demo/runtime/matchcut.json
examples/demo/runtime/media-exclusions.json
examples/demo/runtime/narrative-edit.json
examples/demo/runtime/narrative-media.json
examples/demo/runtime/outro-alignment.json
examples/demo/runtime/stopmotion.json
examples/demo/sources/scene-a.svg
examples/demo/sources/scene-b.svg
requirements.txt
schemas/cutout.schema.json
schemas/lyric-phrases.schema.json
schemas/project.schema.json
schemas/runtime.schema.json
tools/README.md
tools/align_faces.py
tools/align_lyrics.py
tools/analyze_music.py
tools/build_demo.py
tools/cached_runtime.py
tools/catalog_media.py
tools/check_endpoint_frames.py
tools/cutout_subject.py
tools/filmtools/__init__.py
tools/filmtools/checks.py
tools/filmtools/cutout.py
tools/filmtools/edl.py
tools/filmtools/endpoints.py
tools/filmtools/faces.py
tools/filmtools/lyrics.py
tools/filmtools/models.py
tools/filmtools/paths.py
tools/filmtools/portraits.py
tools/filmtools/runtime.py
tools/prepare_project.py
tools/requirements-alignment.txt
tools/requirements-heic.txt
tools/run_tests.py
tools/tests/test_algorithms.py
tools/tests/test_paths_and_staging.py
tools/tests/test_timeline.py
tools/tone_image.py
tools/validate_project.py
```
