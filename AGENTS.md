# Codex 작업 지침 — 수아 첫돌 성장영상

## 목표

Google Drive에서 모은 사진·영상으로 **전문 업체 수준의 성장영상**을 로컬에서 제작합니다. 일관된 디자인과 스토리텔링을 지키면서 원본·개인정보를 보호합니다. **모든 사용자용 안내·설계 문서는 한국어를 기본 언어로 작성합니다.** 파일 경로·명령·라이브러리 이름은 원어를 유지합니다.

## 이번에 확정된 연출 방향

- **첫 장면은 초고속 Face-aligned Match Cut**입니다. 출생부터 첫돌까지 정면/유사 구도의 사진 수십 장을 기하학적으로 정렬하고 시간순으로 짧게 교체합니다.
- 컷 속도가 서서히 빨라져 프리코러스 같은 에너지 상승을 만듭니다.
- 빠른 성장 몽타주 이후 음악 악센트에 맞춰 짧은 **타이틀 카드**로 전환합니다.
- **벌스가 시작되면** 조용하고 감성적인 성장 본편을 시작합니다. 지금의 9초 매치컷 / 3초 타이틀 / 12초 벌스 진입은 **음악 없는 임시값**입니다.
- 음악은 사용자가 Suno 등의 도구로 직접 만듭니다. 오디오 샘플이나 음악을 저장소에 올리지 않습니다.
- 최종 4분 스토리보드는 [docs/TEMPLATE_SPEC.md](docs/TEMPLATE_SPEC.md) 기준으로 갱신합니다.

## 절대 지킬 안전 규칙

1. 원본 사진·영상을 삭제, 이동, 덮어쓰기, 이름 바꾸기 하지 않습니다.
2. 개인 이미지·영상·OAuth 토큰·Drive 인덱스·미리보기·매니페스트·음악·최종 MP4를 GitHub에 푸시하지 않습니다.
3. 가족 미디어를 외부 AI/API에 명시적 동의 없이 업로드하지 않습니다.
4. 날짜가 불확실하면 추정임을 명시합니다. 카카오톡의 날짜는 전달일일 수 있습니다.
5. 시각적으로 비슷한 이미지를 자동 삭제하지 않습니다.
6. 얼굴 정렬은 **기하학적 변환**만 사용하고 얼굴 생성·변형은 하지 않습니다.
7. 아기 얼굴 검출 실패·잘못된 대상 선택·얼굴 잘림 등을 사용자 검토 대상으로 지정합니다.
8. 사용자가 음악을 주기 전에는 임의 음원을 넣지 않습니다. 유료/무료 Suno 라이선스를 확인합니다.

## 주요 파일

- `src/sua_media/catalog.py`: 날짜 추정, 해시, 중복/유사 후보
- `src/sua_media/drive.py`: Drive OAuth 읽기 전용 다운로드
- `src/sua_media/faces.py`: OpenCV YuNet 기하학적 얼굴 정렬
- `src/sua_media/matchcut.py`: 사람이 승인한 프레임만 Remotion용으로 복사
- `video/src/opening/`: 가속 매치컷·타이틀·벌스 시작 예제
- `video/src/templates/`: 시네마틱/스크랩북/예능형 스타일 데모
- `docs/OPENING_MATCHCUT.md`: 오프닝 상세 타임라인
- `docs/MUSIC_BRIEF.md`: 음악 제작 및 큐 마커
- `docs/MOTION_LIBRARY.md`: awesome-ai-motion의 Remotion 적용 범위·출처·라이선스
- `src/sua_media/audio_cues.py`: 로컬 오디오 어택 후보, 사용자 확정 마커 프레임화

## 구현 순서

1. 로컬로 내려받은 Google Drive 폴더 분석: `sua-media 경로 --out data/manifest.json`
2. 정확한 출생일·월령별 자료와 중요 사진을 검토
3. YuNet으로 얼굴 정렬 후 실패/다인물 사진 제외 또는 수동 보정
4. `data/approved-matchcut.json`에 **출생부터 현재 순서로** 승인 사진 나열
5. `sua-matchcut`으로 로컬 이미지 및 `data/opening-props.json` 작성
6. `cd video && npm run dev`로 `OpeningSequence` 미리보기
7. Suno 오디오를 로컬 `sua-audio-cues`로 분석하여 트랜지언트 **후보**만 추출. 벌스/타이틀 마커는 귀로 확인해 `--title-impact`, `--verse-start`로 승인하고 `opening-props.json` 타이밍을 갱신 (자동 구간 추정값을 확정 사실처럼 취급하지 않음)
8. 전체 4분짜리 성장영상의 편집기·스토리보드와 연동
9. `python -m unittest discover -s tests -v`, `cd video && npm run typecheck`, Remotion 번들 검사 실행

## 모션 가이드 연동

`awesome-ai-motion` 원본 저장소의 `SKILL.md`와 관련 효과 카드를 **선택적으로** 읽고, 의도·파라미터·과용 주의사항을 Remotion에 맞게 별도 재구현합니다. 스킬 설치는 사용자 로컬 Codex 환경에 별도로 해야 합니다. 특히 원본 GSAP 타임라인과 Remotion frame 시계의 혼용 및 제3자 라이선스를 검증해야 합니다.

## 검수 목표

1920×1080, 30fps, 안전 여백 5%, 깨끗한 한국어 텍스트, H.264/AAC MP4.
초고속 사진은 **광과민성을 유발할 수 있는 번쩍임이 반복되지 않도록** 과도한 플래시 효과를 금지합니다.
원본 사진의 비율·얼굴 위치를 확인하고 음악 레벨 및 컷 전환이 정확한지 검수합니다.
개인 미디어를 공개 CI에 사용하지 않습니다.
