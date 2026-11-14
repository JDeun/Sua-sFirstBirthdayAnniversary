# 공용 얼굴 매치컷 재생기

정렬된 사진을 고정된 프레임 경계에서 교체하는 Remotion 모듈이다. 이름·날짜·가사·음악·템플릿 테마·개인 JSON을 직접 읽지 않는다. 이 폴더를 다른 Remotion 프로젝트로 옮겨 사용할 수 있다. 현재 검증한 의존성은 React18.3.1과 Remotion4.0.543이다.

```tsx
import {FaceMatchcut} from './modules/face-matchcut';

const photos = [
  {id: 'photo-a', asset: 'matchcut/aligned-a.png'},
  {id: 'photo-b', asset: 'matchcut/aligned-b.png'},
];

export const Opening = () => <FaceMatchcut photos={photos} rate={15} />;
```

- `photos`: 고유한 `id`와 `asset`의 목록. `label`, `captured_at`은 선택 항목이다. 순서를 그대로 사용한다.
- `rate`: 초당 사진 수. 기본15이며 프로젝트 fps 이하여야 한다.
- `durationInFrames`: 모든 사진을 넣을 정확한 프레임 수. `rate`와 동시에 지정하지 않는다. 사진마다 최소1프레임이 필요하다.
- `reverse`, `excludedIds`: 입력을 변경하지 않고 역순·제외를 적용한다.
- `guide`: `true` 또는 정규화한 `eyes`, `center`, `radii`, `color` 객체로 안내선을 표시한다.
- `background`: 배경색. 기본 검정이다.
- `resolveAsset`: 자산 주소를 해석하는 함수. 기본은 Remotion의 `staticFile`이다.

캔버스 크기와 fps는 `useVideoConfig()`에서 받는다. 사전에 정렬한 이미지도 그 캔버스 크기로 준비한다. 음악과 시작 위치는 부모의 `Sequence`에서 지정하며 모듈 안에 넣지 않는다. 오디오를 자동으로 재생하지 않는다.

`createMatchcutPlan`은 React 없이 컷 목록과 전체 길이를 계산한다. `getMatchcutDuration`은 메타데이터 계산에, `sampleMatchcutPhotos`는 양 끝을 보존하는 균등 선별에 쓴다. 선택보다 사진이 적으면 사진을 반복해서 채우지 않는다.

얼굴 검출·눈 좌표·회전·크기 정렬은 별도의 Python `face_matchcut` 라이브러리에서 수행한다. 재생기는 정렬된 원본 픽셀만 표시한다. 사진 수와 프레임 수를 맞추고, 실제 얼굴과 방향·움직임의 연속성은 화면으로 검토한다.

직접 작성한 모듈의 권리 방침은 저장소 소유자의 `All rights reserved`다. 외부 React·Remotion에는 각각의 라이선스가 적용된다.
