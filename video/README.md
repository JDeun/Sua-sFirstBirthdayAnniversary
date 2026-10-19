# Remotion 미리보기 및 오프닝 편집

현재 저장소는 **개인정보가 없는 합성 그래픽**으로 제작한 데모를 제공합니다.

| 컴포지션 ID | 분량 | 목적 |
|---|---:|---|
| `OpeningSequence` | 18초 | **초고속 매치컷 → 타이틀 → 벌스 느낌의 첫 장면** |
| `CinematicPreview` | 24초 | 감성 다큐멘터리·에디토리얼 |
| `ScrapbookPreview` | 24초 | 종이/사진 카드 콜라주 |
| `VarietyPreview` | 24초 | 강렬한 예능형 타이포그래피 |
| `BirthdayPreview` | 20초 | 초기 타이틀 플레이스홀더 |

~~~bash
cd video
npm install
npm run dev
~~~

Remotion Studio에서 `OpeningSequence`를 선택하세요. 실제 사진이 없는 경우 48개의 **가상 도형 얼굴**을 보여주며, 아이를 생성형 AI로 합성하지 않습니다. 다음 명령으로 로컬 프리뷰를 렌더링할 수 있습니다.

~~~bash
npx remotion render src/index.ts OpeningSequence out/opening-demo.mp4
~~~

### 실제 사진으로 재생하는 방법

먼저 저장소 루트에서 `sua-face-align`의 출력물을 사람이 확인한 다음, `data/approved-matchcut.json`에 **출생부터 현재까지** 승인 사진을 나열하고 실행합니다.

~~~bash
sua-matchcut --approved data/approved-matchcut.json
cd video
npx remotion render src/index.ts OpeningSequence out/opening.mp4 --props=../data/opening-props.json
~~~

음악 파일을 넣었다면 프로젝트 루트에서 아래처럼 생성합니다.

~~~bash
sua-matchcut --approved data/approved-matchcut.json --music media/music/intro.wav
~~~

`video/public/media/music/intro.wav`는 로컬 파일이어야 하며 GitHub에서 무시됩니다. Suno 등으로 사용자가 직접 제작한 음악 파일을 사용합니다. 마커를 자동으로 읽지는 못하므로 실제 음악에 맞춰 `src/opening/timing.ts`의 상수를 수정하세요.

정확한 연출: [매치컷 오프닝](../docs/OPENING_MATCHCUT.md) · [Suno 음악 가이드](../docs/MUSIC_BRIEF.md) · [전체 스토리보드](../docs/TEMPLATE_SPEC.md).

최종 4분짜리 실제 성장영상, 음악 비트 검출, 사진 검토 UI는 아직 구현 중인 개발 과제입니다.
