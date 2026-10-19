# Remotion 미리보기 및 오프닝 편집

현재 저장소는 **개인정보가 없는 합성 그래픽**으로 제작한 데모를 제공합니다.

| 컴포지션 ID | 분량 | 목적 |
|---|---:|---|
| `OpeningSequence` | 18초 | **초고속 매치컷 → 타이틀 → 완성곡의 0초가 시작되는 첫 장면** |
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

완성된 Suno 음악이 없다면 무음 데모를 유지할 수 있습니다. 음악 파일이 준비되면 아래처럼 설정합니다.

~~~bash
sua-cold-open --props data/opening-props.json --title-at 9 --song-start 12 \
  --music media/music/suno-final.wav
~~~

`video/public/media/music/intro.wav`는 로컬 파일이어야 하며 GitHub에서 무시됩니다. Suno 등으로 사용자가 직접 제작한 음악 파일을 사용합니다.

~~~bash
# 저장소 루트에서, 선택적으로 별도 효과음 지정
sua-cold-open --props data/opening-props.json --title-at 9 --song-start 12 \
  --music media/music/suno-final.wav \
  --montage-sfx media/sfx/montage.wav --title-sfx media/sfx/title.wav
~~~

효과음은 생략 가능하며 **매치컷 도중 Suno 음악은 재생하지 않습니다.**
`song-start`는 완성곡의 파일 0초 시작 프레임이지 곡 내부 벌스의 시간표가 아닙니다.
`sua-audio-cues`는 곡 전반의 편집 분석에 선택적으로 사용하며 콜드 오픈 설정에는 필요하지 않습니다.

정확한 연출: [매치컷 오프닝](../docs/OPENING_MATCHCUT.md) · [Suno 음악 가이드](../docs/MUSIC_BRIEF.md) · [전체 스토리보드](../docs/TEMPLATE_SPEC.md).

최종 4분짜리 실제 성장영상, 음악 비트 검출, 사진 검토 UI는 아직 구현 중인 개발 과제입니다.
