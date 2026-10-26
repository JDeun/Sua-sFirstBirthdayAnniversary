# 수아의 첫돌: 완성곡 기준 전체 성장영상 만들기

> **현행 오프닝:** 현재 얼굴 → 출생으로 **역순 매치컷(0–8초)** → 실제 탄생 영상 및 선택적 현장음(8–12초) → 무음 타이틀(12–15초) → 완성곡 처음부터 **순방향 본편(15초~)**. [연출 명세](OPENING_MATCHCUT.md).

## 확정된 연출 원칙

- 최종 음악 후보는 「네가 빛날 우주」 듀엣 버전 (2).mp3입니다. 사용자 음원은 **GitHub에 업로드하지 않습니다**.
- MP3 길이: FFprobe 기준 **215.04초**. 30fps에서 **6,452프레임**.
- 기본 콜드 오픈: 0~8초 승인된 얼굴 사진 역순 매치컷 (**음악 없음**) → 8~12초 실제 탄생 영상(현장음 선택) → 12~15초 무음 타이틀 → 15초에 완성곡의 첫 샘플(0:00) 재생.
- 영상 목표 길이는 15초 + 215.04초 ≈ **3분 50초**. 음악의 BPM, 피치 또는 가사를 편집하지 않습니다.
- 노래 시작부터는 출생 → 엄마·아빠와의 순간 → 월령별 성장 → 가족의 기도와 첫돌까지 시간순 전개.
- 가족 사진·음원·렌더는 모두 개인 로컬 저장소에서만 사용합니다.

## 준비와 렌더링

1. `sua-matchcut`으로 수동 승인된 사진을 **현재→출생 역순**으로 구성해 `data/opening-props.json` 생성.
2. 탄생 영상 소스를 지정하고 `sua-cold-open --props data/opening-props.json --title-at 12 --song-start 15`로 최신 타이밍을 적용합니다. 탄생 영상 및 현장음 연결은 생성된 props를 확인하세요.
3. [예시](../examples/approved-story.example.json)를 참고해 `data/approved-story.json`을 만듭니다. 실제 **사용자 승인** 미디어 경로를 출생부터 최근 순서로 입력합니다. 경로는 JSON 파일 위치를 기준으로 합니다.
4. `ffprobe` 설치 확인: macOS에서는 `brew install ffmpeg`.
5. 아래 CLI를 사용해 음원과 사진의 **사본만** 준비합니다.

~~~bash
python -m pip install -e .
sua-film --approved data/approved-story.json \
  --opening-props data/opening-props.json \
  --song "/개인/음악/네가 빛날 우주 (2).mp3" \
  --public-dir video/public \
  --props data/film-props.json \
  --end-card-seconds 4

cd video
npm install
npm run dev
npx remotion render src/index.ts BirthdayFilm out/sua-first-birthday.mp4 \
  --props=../data/film-props.json --codec=h264
~~~

- `sua-film`은 MP3 및 동영상을 FFprobe로 검사하고 총 프레임을 계산합니다.
- `weight`는 각 승인 샷의 화면 체류 시간에 반영할 **상대 가중치**입니다. 실제 시간은 전체 음원에 맞춰 자동 배분됩니다.
- 영상인 경우 `start_seconds`로 원본에서 재생을 시작할 지점을 지정합니다. 배정된 길이보다 원본 비디오가 짧으면 오류로 종료합니다.
- 사진은 부드러운 Ken Burns 줌, 비디오는 원본 소리를 사용하지 않고 **완성곡 단일 오디오**만 사용합니다.
- `video/public/media/music`·`video/public/media/story`의 사본은 SHA-256 이름으로 생성되며 기존 사본을 임의로 덮어쓰지 않습니다.
- 실제 사진이나 음악이 없는 경우 Remotion 기본 예제는 **합성 데모**를 표시합니다. 이는 수아의 실제 완성 영상이 아닙니다.

## 승인 샷 목록 예시

~~~json
{
  "shots": [
    {
      "source": "../assets/incoming/birth.jpg",
      "weight": 1.5,
      "chapter": "처음 만난 날",
      "caption": "우리의 작은 우주",
      "treatment": "cinematic"
    },
    {
      "source": "../assets/incoming/laughing.mp4",
      "weight": 1.0,
      "start_seconds": 3.2,
      "chapter": "꺄르르 웃던 하루",
      "treatment": "scrapbook"
    }
  ]
}
~~~

이 자료는 개인 경로·날짜·가족 정보가 들어갈 수 있으므로 **`data/` 아래에서만 관리**하고 외부에 공유하지 않습니다.

## 최종 품질 검수

- 첫 8초는 음악이 없고, 8~12초에는 선택된 탄생 영상 현장음만, 12~15초에는 무음 타이틀, **15초부터 완성곡의 0초**가 재생되어야 합니다.
- 초고속 성장 매치컷의 얼굴 정렬, 타인 얼굴 포함 여부, 빠른 깜빡임과 시각적 피로를 검수합니다.
- 월령 날짜를 확인하고, 원본 영상 클립이 조기에 끝나거나 검은 화면이 나타나지 않는지 검수합니다.
- 행사장 규격 1920×1080/30fps H.264/AAC MP4를 직접 상영해 확인합니다.
- 재생속도와 음정을 그대로 유지하며 영상 전환으로 후렴의 감정적 변화를 만듭니다.

## 구현 경계

이번 구현은 **승인 사진/영상 목록 + 완성곡 길이 기반의 본편 컴포지션**까지 포함합니다.
실제 가족 사진의 선정, 장면별 가사 타임코드, 수동 편집 UI, 실영상 검수는 다음 작업입니다. 외부 AI로 가족 얼굴을 생성하거나 수정하지 않습니다.


## Codex가 편집 결정을 직접 작성하는 방식 (권장)

`weight` 기반의 자동 시간 배분은 사진 수가 적을 때 **러프컷 미리보기**로만 사용합니다. 최종 편집에서는 Codex가 실제 음악을 듣고 가사의 구간·감정과 맞는 사진을 고른 후, **정확한 컷 시점**을 아래처럼 기록하는 편이 좋습니다.

~~~json
{
  "shots": [
    {
      "source": "../assets/incoming/first-hold.jpg",
      "cut_at_seconds": 0,
      "chapter": "처음 만난 날",
      "treatment": "cinematic"
    },
    {
      "source": "../assets/incoming/sleeping.jpg",
      "cut_at_seconds": 12.5,
      "chapter": "아빠가 바라본 아침"
    },
    {
      "source": "../assets/incoming/laughing.mp4",
      "cut_at_seconds": 28,
      "start_seconds": 2.5,
      "chapter": "꺄르르 웃던 순간"
    }
  ]
}
~~~

**위 시점은 실제 노래에서 채보한 시간이 아닌 형식 예시입니다.** 곡별 가사 시작 시점은 오디오를 직접 확인해 적어야 합니다.

- `cut_at_seconds`는 영상 전체 0초가 아니라 **완성곡 시작 0초**를 기준으로 합니다. 영상에는 앞의 15초 콜드 오픈이 자동으로 더해집니다.
- 첫 샷은 반드시 `cut_at_seconds: 0`, 나머지는 시간순으로 적어야 합니다.
- 최종 엔딩 카드 시작 전까지 자동으로 각 샷의 길이가 산출됩니다. 잘못 정렬되었거나 1초보다 짧은 샷은 오류입니다.
- 정확한 컷 편집을 하려면 **모든 샷에** `cut_at_seconds`를 적습니다. 일부만 지정하는 혼합 모드는 허용하지 않습니다.
- 음악과 가사의 의미를 사진에 연결하는 **결정은 Codex/편집자가** 하고, 코드가 촬영일을 추정하여 마음대로 중요한 장면을 고르지 않습니다.
- 편집 에이전트의 출력은 사용자가 언제든 텍스트만으로 손볼 수 있는 **작은 JSON EDL**입니다. 별도 전용 웹앱을 만들 필요가 없습니다.

## 로컬 음악 분석과 컷 후보 연결

먼저 개인 음원을 16비트 PCM WAV로 준비합니다. 예: `ffmpeg -i "네가 빛날 우주 (2).mp3" -ar 48000 -ac 2 -c:a pcm_s16le data/song-analysis.wav`. 원본은 변경하지 않습니다.

~~~bash
sua-music-analyze data/song-analysis.wav --output data/music-landmarks.json \\
  --min-gap-seconds 2 --sensitivity 1.6
sua-music-cuts --approved data/approved-story.json \\
  --landmarks data/music-landmarks.json --story-seconds 211.04 \\
  --min-shot-seconds 3 --output data/approved-with-cuts.json
~~~

**주의:** `211.04`는 215.04초 음원에서 4초 엔딩 카드를 제외한 **예시 값**입니다. 실제 `story-seconds`는 FFprobe로 측정한 곡 길이에서 엔딩 카드 길이를 뺀 값으로 지정합니다. 이 분석은 RMS 음량 증가 지점만 제안하며 **정확한 박자·후렴·가사 구간을 자동으로 판별하지 않습니다**. `data/music-landmarks.json`을 검토하고 필요하면 수동 수정한 뒤 컷을 확정하세요.

~~~bash
sua-film --approved data/approved-with-cuts.json \\
  --opening-props data/opening-props.json \\
  --song "/개인/음악/네가 빛날 우주 (2).mp3" \\
  --public-dir video/public --props data/film-props.json --end-card-seconds 4
cd video
npx remotion render src/index.ts BirthdayFilm out/sua-first-birthday.mp4 \\
  --props=../data/film-props.json --codec=h264
cd ..
python scripts/check_final_render.py video/out/sua-first-birthday.mp4 \\
  --expected-frames 6902 --fps 30
~~~

위 `6902`프레임은 곡 길이 215.04초를 30fps로 올림한 6452프레임과 15초 오프닝 450프레임의 합인 **예시**입니다. 실제 생성된 props의 총 프레임에 맞춰 조정해야 합니다. `--black-detect` 옵션은 의도적인 암전 연출도 오류로 표시할 수 있으므로, 검사 결과를 직접 확인한 뒤 사용합니다.
