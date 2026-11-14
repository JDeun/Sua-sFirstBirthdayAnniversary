# 도형 예제

사진·실제 영상·음악·제공받은 가사 없이 SVG 도형2개를 사용하는 무음4초 예제다. 날짜와 영문 문구는 새로 만든 가상의 값이다.

`runtime/`에는 렌더러 입력8개가 있으며 `copy.json`은 공통 문구 키70개를 채운다. 오프닝과 원음은 비활성이고 `copy.song_asset`은 null이다. 마지막 문구에는 명시적인 시각이 있다. 사용하지 않는 후렴 정렬 행은 가상의 문구로 입력 구조를 점검한다.

템플릿 루트에서 실행한다.

```sh
python3.11 -B tools/prepare_project.py --config examples/demo/project.json --check
python3.11 -B tools/prepare_project.py --config examples/demo/project.json --copy
```

다른 개인 프로젝트의 입력 링크가 연결돼 있다면 먼저 분리하거나 별도 렌더러 폴더를 지정한다. `tools/build_demo.py --destination DIR`로 별도 예제를 다시 만들 수 있다. 런타임8개를 합친 구조는 `schemas/runtime.schema.json`, 의미·경로·타이밍 검사는 준비 도구에서 확인한다.
