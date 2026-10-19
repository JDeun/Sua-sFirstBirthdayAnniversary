# 디자인 시스템 및 4분 스토리보드 — v0.1

공개 상품 설명 기반 벤치마크: [MARKET_RESEARCH_2026-10.md](MARKET_RESEARCH_2026-10.md)

## 스타일 프리셋

| 프리셋 ID | 용도 | 기본 색상 | 전환 | 움직임 | 권장 사용 |
|---|---|---|---|---|---|
| `cinematic` | 서사 중심 본편 | 아이보리·차콜·세피아 | 컷/소프트 디졸브 | 미세 줌/패닝 | 70~80% |
| `scrapbook` | 월령별 스냅 모음 | 크림·살구·세이지 | 종이 카드 슬라이드 | 약한 회전/바운스 | 15~25% |
| `variety` | 짧은 유머/인트로 | 코발트·버터·코랄 | 리듬 컷/팝 | 탄성 있는 입장 | 5~10% |

색과 레이아웃·효과는 업체 고유 자산을 복제하지 않고 자체 제작.
동영상 내 글꼴은 실제 배포 가능한 한글 글꼴과 라이선스를 나중에 확정하며, 프리뷰는 시스템 대체 글꼴을 사용.

## 목표 편집안: 04:00 / 30fps = 7200 frames

| Timecode | Sec | Frames | Scene | Required assets | Direction |
|---|---:|---:|---|---|---|
| 00:00–00:15 | 15 | 450 | Hook/Title | best video 1, title | Variety에서 Cinematic으로 차분하게 전환 |
| 00:15–00:45 | 30 | 900 | Arrival | birth photos 6–10 | 첫 만남, 짧은 자막, 천천히 밀어주는 움직임 |
| 00:45–01:30 | 45 | 1350 | 1~3 months | photos 12–18 + video 1–2 | 첫 표정과 초기 변화 |
| 01:30–02:05 | 35 | 1050 | 4~6 months | photos 10–14 + video 1–2 | 월령 카드/스크랩북 |
| 02:05–02:45 | 40 | 1200 | 7~9 months | photos 10–16 + video 1–2 | 가족과 놀이, 활동 컷 |
| 02:45–03:25 | 40 | 1200 | 10~12 months | photos 10–16 + video 2–3 | 활발한 변화와 현장감 |
| 03:25–03:40 | 15 | 450 | Face-aligned match cut | selected faces 20–50 | 눈 중심/크기 안정화, 0.2~0.6s 선별 컷, 사람 검토 |
| 03:40–03:55 | 15 | 450 | Parents' message | best family photo/video | 음악 아래 간결한 감사·축복 텍스트 |
| 03:55–04:00 | 5 | 150 | End card | title + approved photo | 아이 이름, 첫돌 축하, 여운 |
| **Total** | **240** | **7200** | | | |

위 각 칸의 원본 개수는 **초기 편집 예산**이지 업체 데이터나 필수 제출 조건이 아님.
원본이 적으면 장면 길이·레이아웃을 변경한다. 4분을 맞추기 위해 같은 사진을 과도하게 반복하지 않는다.

## Frame-based editing contract

- 프로젝트 구성은 `storyboard.json`을 단일 진실 원천으로 사용. 단위는 초가 아닌 **정수 프레임**.
- 레이어는 `assetId`/source trim / cropMode / startFrame / durationFrames / transition / text / audioGain로 구성.
- 템플릿은 사진 수가 아니라 **섹션 구성/간격/모션**을 결정한다.
- 음악 교체 시 비트/전환 마커를 다시 분석하여 샷 길이를 리타이밍한다(후속 기능).
- 사진 원본을 바꾸지 않고 transform metadata(x/y/scale/rotation)만 저장.
- 매치컷은 **얼굴 생성·모핑 없이** 위치·각도 정렬 + 빠른 하드컷으로 구성.
- 미검증 날짜는 월령 확정 문구 사용 금지; 중립 자막 또는 확인 플래그.

## QA 기준

- 1920×1080 / 30fps / H.264/AAC, 로컬 MP4. 행사장 요구에 맞춰 조정.
- 인물이 잘리지 않는 크롭(특히 9:16 폰 영상), 여백/백그라운드 재구성.
- 텍스트 세이프 영역: 일반적으로 프레임 가장자리 최소 5% 안쪽.
- 사용자 자막 검수: 이름, 출생일, 월령, 가족 호칭, 개인정보.
- 검은/중복 프레임, 영상 끊김, BGM 과증폭, 원본 자연음 크기 검수.
- 음악·폰트·삽화·샘플 영상의 라이선스는 별도 확인.
- 모든 실제 사진/소리/최종 MP4는 로컬만 보관하며 공개 GitHub나 CI에 업로드하지 않음.

## Ready-made preview

`cd video && npm install && npm run dev`

Remotion Studio에서 `CinematicPreview`, `ScrapbookPreview`, `VarietyPreview`를 선택해 **실제 아기 미디어를 사용하지 않는 24초짜리 디자인 데모**를 비교할 수 있다. 실제 4분 편집본이 아님. 프리셋 토큰과 모션 비교용.

~~~bash
cd video
npx remotion render src/index.ts CinematicPreview out/cinematic-demo.mp4
npx remotion render src/index.ts ScrapbookPreview out/scrapbook-demo.mp4
npx remotion render src/index.ts VarietyPreview out/variety-demo.mp4
~~~
