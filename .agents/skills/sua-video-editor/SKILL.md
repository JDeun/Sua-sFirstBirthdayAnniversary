---
name: sua-video-editor
description: Direct Sua's local first-birthday music video with the approved duet song and private photos. Use for lyrics-aware scene selection, timestamped edit decisions, and Remotion rendering. Do not publish family media.
---

# 수아 첫돌 성장영상 — Codex 편집 감독

이 스킬은 *코드를 더 만드는 것*보다 **완성곡의 정서와 실제 사진·영상을 맞추는 작업**을 우선합니다. Remotion을 렌더링 엔진으로 사용합니다.

## 실제 작업 순서

1. 저장소의 `AGENTS.md`와 `docs/FULL_FILM.md`를 읽습니다. 확정 후보는 듀엣곡 `네가 빛날 우주 (2).mp3`입니다. 원본 음악의 멜로디, 속도, 피치를 수정하지 않습니다.
2. 로컬 `data/manifest.json`과 사진·영상 폴더를 확인합니다. 파일이 없다면 합성 프리뷰만 만들고 실제 완성영상이라고 주장하지 않습니다.
3. 로컬 음원의 FFprobe 시간, 음악 파형·실제 청취로 인트로/절/프리코러스/후렴/브리지/아웃트로 **시작 시간**을 확인하여 `data/music-cues.json`에 기록합니다. 자동 분석 시각은 검수되지 않은 추정치로 표시하고 가사 구간을 추측해 단정하지 않습니다.
4. `sua-media` 중복·시간순 후보를 검토합니다. 검토용 로컬 콘택트시트/비디오 썸네일을 만든 뒤, 구도·빛·감정·아기 표정·시간순 연결을 기준으로 후보를 정리합니다. 중복 후보는 자동 삭제하지 않습니다.
5. 노랫말에 대응하는 실제 장면을 고릅니다.
   - 처음 품에 안던 날: 실제 출생 직후 아빠의 포옹 사진이 있으면 우선 검토.
   - 아침 문을 나서다가 / 엄마가 보였어: **출근하는 아빠 시점**, 잠든 엄마와 수아의 사진.
   - 꺄르르 웃던 네 얼굴: 웃는 장면, 가능하다면 실제 짧은 영상.
   - 네가 빛날 우주: 성장·희망을 보여주는 장면.
   - 주님의 사랑 안에 자라길: 실제 가족 또는 기도 장면이 있을 때만.
   - 수아야 사랑해: 가장 좋은 표정/가족사진으로 마무리.
   - 없는 장면은 AI로 지어내지 않고 유사한 실제 추억을 선택합니다.
6. 로컬 `data/approved-story.json`에 **컷 결정표(EDL)**를 작성합니다. 각 샷은 `source`, `cut_at_seconds`(완성곡 0초 기준), 선택적 `chapter`/`caption`/`treatment`를 가집니다. 첫 샷의 `cut_at_seconds`는 0, 모든 샷의 시각은 오름차순이며 최소 1초 이상 간격을 둡니다. 영상 클립 내부 시작점은 `start_seconds`를 사용합니다. 코드가 샷 배치를 임의로 정하게 두지 않습니다.
7. 가사 구간/음악 시각/선정한 로컬 사진/선정 이유/월령 확실성 표를 만들고 가족에게 검토할 수 있게 제공합니다. 실제 얼굴과 제3자의 모습 및 월령은 사용자 승인을 얻어 확정합니다.
8. 승인 후 빌드:
   - `sua-film --approved data/approved-story.json --opening-props data/opening-props.json --song "/개인/음원/네가 빛날 우주 (2).mp3" --props data/film-props.json`
   - `cd video && npx remotion render src/index.ts BirthdayFilm out/sua-birthday.mp4 --props=../data/film-props.json --codec=h264`
9. **콜드 오픈 0~9초는 음악 없이** 승인 매치컷, 9~12초 타이틀, 12초부터 완성곡 0초 시작. 본편 리듬에 맞는 컷·색·자막, 화자 시점, 엔딩과 전체 오디오 길이를 QC합니다.

## 연출·개인정보 제약

- 인물 선정과 시간순은 사진 원본·메타데이터로 검증합니다. 카카오톡 전달 시각을 촬영일로 단정하지 않습니다.
- 음악의 후렴에서는 컷·표정·구도 변화를 이용하고, 곡 자체를 억지로 편집하지 않습니다.
- 초고속 매치컷 밖에서는 플래시·스우시·과도한 전환을 사용하지 않습니다.
- Remotion 장면 효과는 필요한 것만 적용하며 영상 편집을 위한 별도 GUI나 복잡한 DB를 만들지 않습니다.
- 가족 얼굴이나 원본 영상·음원을 Adobe 등 외부 클라우드/AI에 별도 명시적 동의 없이 업로드하지 않습니다.
- 가족 사진·음원·영상·검토 타임라인은 `data/`, `video/public/media/` 및 로컬 출력에만 보관합니다. 공개 저장소에 커밋하지 않습니다.

**완성 정의**: 실사진·음원 연결, 사용자가 승인한 가사별 장면 결정표, 전체 영상 렌더, 육안·청각 검수까지 끝난 경우. 단순 코드/CI 성공은 완성이 아닙니다.
