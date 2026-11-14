# 얼굴 매치컷 모듈

얼굴 매치컷은 성장영상의 오프닝과 분리된 기능이다. 얼굴 검출·정렬은 로컬 Python 라이브러리, 컷 계산·재생은 공용 Remotion 모듈로 나눈다. 다른 템플릿에서도 이 두 부분을 가져다 쓸 수 있다. 현재 영상의 음악·자막·테두리·등장 위치는 템플릿 쪽에서 관리한다.

| 경로 | 책임 |
| --- | --- |
| `tools/face_matchcut/` | YuNet 후보 검출, 눈 좌표 기반 유사변환, 원본 픽셀 정렬 |
| `tools/align_faces.py` | 단일 사진의 후보 확인과 명시적 얼굴 선택 |
| `tools/build_matchcut.py` | 검토한 눈 좌표·원본 해시를 받아 정렬 사진과 재생 목록 생성 |
| `renderer/src/modules/face-matchcut/` | 독립 타입, 정수 프레임 계획, 가이드와 재생기 |
| `renderer/src/FaceMatchcut.tsx` | 현재 프로젝트의 목록·개인 문구를 공용 재생기에 연결하는 어댑터 |
| `renderer/src/narrative/NarrativeOpening.tsx` | 심장소리·초음파·타이틀·탄생 장면과 연결 |

## 독립 미리보기

```sh
npm ci --prefix renderer
npm run matchcut:dev --prefix renderer
```

`FaceMatchcutDemo`는 코드로 그린 도형12장을 사용한다. 개인 runtime·사진·영상·음원·가사·테마를 읽지 않는다. 30fps에서 초당6장으로 재생하며, Studio props에서 `rate`, `reverse`, `guide`를 바꿀 수 있다. 도형 데모는 재생과 프레임 경계를 확인하는 예제이며 실제 얼굴 검출 정확도의 증거는 아니다.

## 다른 템플릿에 연결

공용 재생기 폴더를 다른 Remotion 프로젝트의 소스로 복사하고, 그 프로젝트가 준비한 목록을 넘긴다. 파일명·날짜·생일·곡 제목을 모듈에 하드코딩하지 않는다. 별도의 npm 배포 패키지를 설치하는 구조는 아니다.

```tsx
import {Sequence} from 'remotion';
import {FaceMatchcut, getMatchcutDuration} from './modules/face-matchcut';

const photos = [
  {id: 'photo-a', asset: 'matchcut/aligned-a.png'},
  {id: 'photo-b', asset: 'matchcut/aligned-b.png'},
];
const fps = 30;
const duration = getMatchcutDuration(photos.length, 15, fps);

export const Opening = () => <Sequence from={60} durationInFrames={duration}>
  <FaceMatchcut photos={photos} rate={15} guide={false} />
</Sequence>;
```

고정된 길이에 사진을 모두 넣으려면 `rate` 대신 `durationInFrames`를 사용한다. 두 옵션을 동시에 주거나 사진보다 프레임이 적으면 오류로 처리한다. 사진은 기본적으로 전달한 순서대로 재생하며, `reverse`와 `excludedIds`로 순서·제외를 지정할 수 있다. 공용 모듈이 촬영일을 추정하거나 역순을 강제하지 않는다.

기본 자산 경로는 해당 프로젝트의 `public/` 기준이다. 정렬 결과 폴더를 그 아래 `matchcut/`에 연결했다면 목록의 `asset`에도 `matchcut/` 접두어를 붙인다. 다른 자산 해석이 필요하면 `resolveAsset` 함수를 넘긴다. 캔버스와 fps는 부모 Composition을 따른다.

## 정렬 도구

Python 모듈은 프로젝트 runtime에 의존하지 않으며 NumPy·Pillow·OpenCV로 실제 픽셀을 변환한다. YuNet은 후보 검출에만 필요하다. 모델 경로와 해시는 기존 [모델 안내](../models/README.md)를 따른다.

```sh
python3.11 tools/align_faces.py --source ../media/photos/portrait.jpg --output ../private/face-candidates.json
python3.11 tools/build_matchcut.py --help
```

일괄 입력은 `version`, `canvas`, `photos`를 가진 별도 비공개 JSON이다. `source_directory`는 설정 파일 기준 원본 폴더이며, 사진의 `source`는 그 폴더 안의 상대 경로다. 이처럼 원본을 설정 파일 옆으로 복사할 필요 없이 외부 미디어 폴더를 지정할 수 있다.

```json
{
  "version": 1,
  "source_directory": "../media/photos",
  "canvas": {"width": 1920, "height": 1080,
    "target_eyes": [[850, 430], [1070, 430]]},
  "photos": [{"id": "photo-a", "source": "portrait.jpg",
    "source_sha256": "<원본 파일의 SHA256>",
    "eyes": [[180, 220], [300, 220]]}]
}
```

```sh
python3.11 tools/build_matchcut.py --config ../private/approved-faces.json --output-directory ../work/matchcut
```

출력 폴더의 부모는 미리 준비하고, 새 출력 폴더를 지정한다. 기존 출력은 덮어쓰지 않는다. 원본 해시·중복·좌표·경로를 확인한 뒤 `photo-000001.png`부터 순서대로 만들고 `manifest.json`에 상대 자산 목록과 정렬 근거를 기록한다. 위 JSON의 해시·좌표는 사용자의 실제 승인 데이터로 채운다.

일괄 정렬은 대상 얼굴과 방향을 확인한 두 눈 좌표와 원본 SHA256을 입력으로 받는다. 좌표는 EXIF 방향을 적용한 이미지의 픽셀 좌표다. 가이드에는 정렬 목표점의 픽셀 좌표를 캔버스 크기로 나눈0~1 좌표를 설정한다. 눈 좌표를 같은 순서로 짝지어 회전·이동·배율을 맞추고, 원본 RGB를 재생성하지 않는다.

입력 순서를 유지한 결과 목록은 `{id, asset, captured_at?}`를 공용 재생기에 전달한다. 원본 경로·얼굴 주석·개인 목록·정렬 사진·검토 화면은 저장소 밖에 둔다. 자동 후보 검출은 사람의 신원 확인을 하지 않으므로 대상 선택을 생략하지 않는다.

## 검증

```sh
npm run test:matchcut --prefix renderer
python3.11 -B tools/run_tests.py
```

프레임 계획은 정수 경계·끝 프레임·빈 목록·역순·제외·입력 불변성·비정수 컷 간격·사진 수 초과를 검사한다. 기존 개인 오프닝은274장·548프레임의 ID·자산·모든 컷 경계가 분리 전과 같은지 로컬에서 대조했다. 개인 목록은 이 문서나 테스트에 넣지 않는다.

CI는 도형 데모의 첫 컷 경계를 가로지르는4~6프레임을 실제 브라우저로 렌더한다. 현재 영상의 전후 픽셀 비교·연속 시청·청취를 완료했다고 주장하지 않는다. 동기화와 최종 시청 범위는 [검수 안내](validation.md)에 있다.
