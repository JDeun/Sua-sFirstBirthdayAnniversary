# 음악 제작 가이드: 오프닝 매치컷 + 수아 첫돌 성장영상

음악은 사용자가 **Suno 등으로 직접 제작**하며, 저장소에는 음악 원본을 넣지 않습니다.

## 원하는 감정 곡선

```text
시간(임시)       0s               9s       12s                 본편
음악          점층 상승 >>>>>>  [IMPACT]   벌스 (감성·따뜻함) >>> 후반 코러스
화면          얼굴 가속 매치컷     타이틀     탄생·가족 이야기
감정          기대감·집중        전환/해소  다정함과 몰입
```

- **0~9초:** 짧은 스타카토·리듬 층 추가·음역/강약 상승; 사진 전환이 점진적으로 빨라지도록
- **9초:** 강렬하지만 날카롭지 않은 단발성 악센트/임팩트. 타이틀 화면 전환
- **9~12초:** 잔향과 짧은 공간. 타이틀을 읽을 수 있도록
- **12초 이후:** 따뜻한 벌스 시작. 이 지점부터 성장 본편이 진행되도록 음악 구성
- **중·후반:** 가사/멜로디의 정서적 절정, 가족의 목소리가 나올 때는 음악을 덕킹할 수 있어야 함
- **종결:** 여운이 남는 엔딩

**중요:** Suno에 초를 숫자로 입력한다고 정확히 그 시점에 벌스가 시작되는 것은 보장되지 않습니다. 필요하면 제작한 음악을 DAW에서 인트로/악센트/벌스 단위로 편집하여 마커를 맞춥니다.

## Suno 시도용 콘셉트 문구 (영문)

> Heartfelt cinematic indie-pop song for a baby's first birthday film. Begin with a 9-second instrumental rhythmic build, gradually accelerating tension and layering percussion. Add one strong uplifting impact for a title card, then a brief breathing space. Let a warm and intimate verse enter around the 12-second mark with gentle vocals. Evolve into an emotionally uplifting chorus. Soft piano, acoustic guitar, organic percussion, delicate strings, modern polished production. No abrupt silence, no harsh flashes or aggressive sound effects.

편곡이 원하는 대로 나오지 않으면 Suno에서 **인트로 라이저/임팩트용 별도 짧은 파일**을 만들거나 DAW에서 타이밍을 수동 편집하는 편이 정확합니다. 인트로와 본편의 키·템포·음향적 질감이 이질적이지 않도록 주의하세요.

## 오디오 파일 준비

- 최종 파일 권장: WAV 44.1kHz 또는 48kHz 스테레오(가능하면 무손실), 없으면 고품질 MP3
- 로컬 저장 위치: `video/public/media/music/intro.wav` 또는 로컬 전용 경로
- 실제 최종 음악의 마커 기록(시간은 예시이고 아직 확정되지 않음):

~~~json
{
  "fps": 30,
  "music_file": "media/music/intro.wav",
  "markers": {
    "matchcut_start_sec": 0,
    "title_impact_sec": 9,
    "verse_start_sec": 12
  },
  "status": "draft_unverified"
}
~~~

위 JSON은 **설계 예시**입니다. 현재 Remotion 코드는 음악을 자동 분석하지 않으며 `video/src/opening/timing.ts`의 상수를 편집해 타이밍을 맞추는 구조입니다. 나중에는 이 마커를 읽고 자동 렌더링하도록 개선할 예정입니다.

## Suno 이용 권리 확인

Suno 공식 문서 기준(2026-10 조사):

- Basic 무료 플랜에서 만든 곡은 **개인적·비상업적 이용**만 허용합니다.
- Pro/Premier 유료 구독 **중 생성한 곡**에는 상업적 이용 권한이 부여됩니다. 구독 이전 무료 생성곡이 구독만으로 소급 허가되는 것은 아닙니다.
- 플랫폼이 제공하는 이용 권한과 **저작권 보호 여부는 별개**입니다.
- 돌잔치 행사장에서의 재생, 가족 공유, 소셜미디어/유튜브 게시, 수익화는 이용 조건과 제3자 권리(특히 기존 음원·가사·샘플)를 각각 확인해야 합니다.
- 라이선스 변경 가능성이 있으니 제작·상영·업로드 시 최신 약관을 다시 확인하세요.

공식 출처:
- https://help.suno.com/en/articles/9601601
- https://help.suno.com/en/articles/9601665
- https://help.suno.com/en/articles/2425729
- https://help.suno.com/en/articles/2746945
