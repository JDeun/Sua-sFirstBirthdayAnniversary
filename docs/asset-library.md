# 모션 에셋 사용법

배경의 별·궤도와 왕관·선물상자는 사진에서 잘라낸 이미지가 아니라 SVG와 CSS로 그린 코드다. `renderer/src/assets/`에서 독립적으로 재사용한다. 기존 본편의 도형·등장 시각은 유지하며, 추가 에셋을 본편에 자동 삽입하지 않는다.

## 준비된 종류

| ID | 에셋 | 움직임 |
| --- | --- | --- |
| `star` | 별과 하단 별 장식 | 한 번 펼쳐지는 별 |
| `crown` | 왕관 | 선이 차례로 그려짐 |
| `gift` | 선물상자 | 뚜껑이 열리고 앞면이 내려감 |
| `universe` | 별·원형 빛·우주 궤도 | 느린 궤도 이동 |
| `heart` | 하트 윤곽 | 작은 크기 변화 |
| `moon` | 초승달 | 부드럽게 등장 |
| `planet` | 고리가 있는 행성 | 느린 고리 회전 |
| `shooting-star` | 별똥별 | 꼬리를 남기며 한 번 이동 |
| `cloud` | 구름 | 부드럽게 등장 |
| `castle` | 작은 성 | 부드럽게 등장 |
| `balloons` | 풍선 | 한 번 떠오른 뒤 정지 |

원본은 코드로 보관한다. 배경이나 글자가 들어간 완성 장면을 에셋으로 굳히지 않아 크기와 레이어 순서를 계속 편집할 수 있다. 색상 기본값은 본편과 같은 `renderer/src/theme.ts`를 사용한다.

## 개인 자료 없이 미리보기

`renderer/src/asset-index.ts`는 개인 runtime·사진·영상·음원·가사를 읽지 않는 별도 진입점이다. 새로 받은 저장소에서도 모델 설치나 미디어 스테이징 없이 렌더러 의존성만 설치하면 볼 수 있다.

```sh
npm ci --prefix renderer
npm run assets:dev --prefix renderer
```

Studio에서 `AssetCatalog`는 11종 목록이고, `Asset-star`, `Asset-crown`처럼 시작하는 항목은 개별 에셋이다. 모두 1920×1080, 30fps, 3초로 등록돼 있다. 브라우저가 준비된 환경에서는 렌더러 폴더에서 다음과 같이 출력한다.

```sh
npx remotion still src/asset-index.ts AssetCatalog ../.cache/assets-preview.png --frame=45
npx remotion render src/asset-index.ts AssetCatalog ../.cache/assets-preview.mp4
```

개별 항목은 배경색을 넣지 않은 레이어다. 다른 편집기에 옮길 때는 정지 이미지와 알파 채널을 지원하는 영상 형식을 구분해서 출력한다. 일반 H.264 MP4를 투명 영상으로 취급하지 않는다.

## 장면에 사용하기

```tsx
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {MotionAsset} from './assets';

export const Decoration = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <MotionAsset id="moon" frame={frame * 30 / fps}
    x={500} y={-200} scale={0.35} rotation={-12} opacity={0.6} />;
};
```

`frame`은 등장 순간이 0인 로컬 시계이며, 30fps 기준으로 받는다. `Sequence` 안에서는 `useCurrentFrame()`이 이미 해당 시퀀스의 로컬 시계다. 다른 fps에서는 위와 같이 환산한다. `x`, `y`는 전체 1920×1080 레이어의 이동량이고, 회전과 배율의 기준점은 화면 중앙이다. 음절·박자에 맞춘 실제 시작 시각은 장면 편집 데이터에서 정한다. 에셋이 음악을 추측하거나 자동으로 반복하지 않는다.

세밀한 위치·색·크기는 `StarBloom`, `DrawnCrown`, `CelestialSticker` 등의 개별 컴포넌트로 지정한다. 해당 props 타입은 `assets/index.ts`에서 내보낸다. 원래 본편은 개별 컴포넌트를 사용해 기존 배치를 보존한다.

선물상자는 `GiftBoxBack` → `GiftBoxLid` → 실제 인물 → `GiftBoxFront` 순서로 합성한다. 라이브러리의 `gift` 미리보기에는 인물이 없다. 얼굴 정렬·마스크·등장 시각·음원 동기화는 개인 편집 데이터에 남긴다.

## 추가와 검수

새 종류는 `stickers.tsx` 또는 별도 파일에 추가하고, `library.tsx`의 ID·이름·렌더 분기에 연결한다. 무작위 상태와 실시간 시계 대신 전달받은 프레임으로 그린다. 반복은 필요한 장면에서만 명시한다. 아이의 얼굴과 행동을 가리는 장식은 피한다.

기존 12개 도형은 분리 전후 6개 시점씩, 72개 SVG 출력이 같은지 비교했다. 자동 CI는 도형 예제와 에셋 목록을 각각 3프레임 렌더한다. 이 검사는 연속 동작이나 미적 완성도에 대한 사람의 검수를 대신하지 않는다. 코드와 새 도형의 권리 방침은 루트 `LICENSE`를 따른다.
