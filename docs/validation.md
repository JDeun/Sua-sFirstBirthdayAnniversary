# 검사와 제작 완료의 범위

공개 저장소는 개인 미디어가 없는 상태로 검사한다. 실제 제작물은 별도의 개인 설정·runtime·자산으로 확인한다. 검사 결과를 완성 영상의 연속 시청이나 청취와 혼동하지 않는다.

| 검사 | 확인하는 내용 |
| --- | --- |
| `scripts/audit_public.py` | 공개 파일 허용 목록, 개인 파일명·로컬 경로·가사 유입, 등록 모델 해시 |
| `scripts/setup_models.py` | 사용 모델의 크기와 SHA256 |
| `python -m unittest discover -s tests -v` | 인코딩·파일명·링크 등 공개 경계의 회귀 검사 |
| `python -B tools/run_tests.py` | 미디어 정렬·날짜·중복·프로젝트 스테이징 등의 검사 |
| `tools/prepare_project.py --config … --check` | 외부 프로젝트 데이터와 실제 사용 자산의 연결 |
| `npm run typecheck --prefix renderer` | 렌더러와 에셋의 타입 검사 |
| `npm run test:matchcut --prefix renderer` | 공용 매치컷의 경계·속도·제외·독립 의존성 검사 |
| `npm run preflight --prefix renderer` | 연결된 프로젝트의 구성·자산 참조·배치와 새 번들 생성 |
| GitHub CI의 렌더 | 도형 본편·코드 에셋 목록·독립 매치컷 경계의 실제 브라우저 렌더 |

개인 설정을 바꿔 준비할 때는 [도구 안내](../tools/README.md), 독립 에셋은 [에셋 안내](asset-library.md), 얼굴 매치컷은 [모듈 안내](face-matchcut.md)를 따른다. 외부 설정 파일을 사용하는 헤드리스 검사의 옵션은 `node renderer/scripts/verify-headless.mjs --help`에서 확인한다.

시간순 검사는 원본 날짜의 정밀도와 가족이 확인한 기념일을 함께 사용한다. 촬영 시각을 모르는 두 구간이 겹치면 검토 대상으로 남기며, 시간순을 입증했다고 표시하지 않는다.

최종 전달 전에는 실제 출력 영상을 처음부터 끝까지 보면서 동작의 연속성·컷 전환·가사 시각·원음과 노래의 음량·피부톤·누끼 경계·영상 끝·의도하지 않은 빈 프레임을 확인한다. 마지막에 들어갈 원본을 아직 받지 않았다면 그 상태도 별도로 기록한다. 개인 검수 결과와 대표 화면은 공개 저장소에 넣지 않는다.
