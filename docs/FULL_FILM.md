# 수아의 첫돌: 완성곡 기준 전체 성장영상 만들기

## 확정된 연출 원칙

- 최종 음악 후보는 「네가 빛날 우주」 듀엣 버전 (2).mp3입니다. 사용자 음원은 **GitHub에 업로드하지 않습니다**.
- MP3 길이: FFprobe 기준 **215.04초**. 30fps에서 **6,452프레임**.
- 기본 콜드 오픈: 0~9초 승인된 성장 얼굴 매치컷 (**음악 없음**) → 9~12초 타이틀 → 12초에 완성곡의 첫 샘플(0:00) 재생.
- 영상 목표 길이는 12초 + 215.04초 ≈ **3분 47초**. 음악의 BPM, 피치 또는 가사를 편집하지 않습니다.
- 노래 시작부터는 출생 → 엄마·아빠와의 순간 → 월령별 성장 → 가족의 기도와 첫돌까지 시간순 전개.
- 가족 사진·음원·렌더는 모두 개인 로컬 저장소에서만 사용합니다.

## 준비와 렌더링

1. 기존 `sua-matchcut`으로 수동 승인된 사진만 콜드 오픈에 연결해 `data/opening-props.json` 생성.
2. 필요하면 `sua-cold-open --props data/opening-props.json --title-at 9 --song-start 12` 적용.
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

- 첫 9초는 음악이 전혀 들리지 않고, 12초 시점부터 완성곡의 0초가 재생되어야 합니다.
- 초고속 성장 매치컷의 얼굴 정렬, 타인 얼굴 포함 여부, 빠른 깜빡임과 시각적 피로를 검수합니다.
- 월령 날짜를 확인하고, 원본 영상 클립이 조기에 끝나거나 검은 화면이 나타나지 않는지 검수합니다.
- 행사장 규격 1920×1080/30fps H.264/AAC MP4를 직접 상영해 확인합니다.
- 재생속도와 음정을 그대로 유지하며 영상 전환으로 후렴의 감정적 변화를 만듭니다.

## 구현 경계

이번 구현은 **승인 사진/영상 목록 + 완성곡 길이 기반의 본편 컴포지션**까지 포함합니다.
실제 가족 사진의 선정, 장면별 가사 타임코드, 수동 편집 UI, 실영상 검수는 다음 작업입니다. 외부 AI로 가족 얼굴을 생성하거나 수정하지 않습니다.
