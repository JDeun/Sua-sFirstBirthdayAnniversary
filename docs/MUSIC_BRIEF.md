# Suno 웹 제작 가이드: 완성곡은 콜드 오픈과 분리

## 확정 원칙

**Suno에서는 오프닝 라이저/프리코러스/타이틀 효과음을 만들지 않습니다.**
90년대 컨템퍼러리 R&B/팝 소울 곡을 독립된 **완성곡**으로 제작합니다.
뮤직비디오식 초고속 매치컷 8~10초는 별도로 무음 또는 효과음만 편집하고,
2~3초의 타이틀 이후 Suno 파일을 **처음부터** 재생합니다.

음원 자체의 인트로가 4초, 10초 등으로 다르더라도 노래는 0초부터 시작합니다.
생성된 노래의 벌스 시작 시점을 임의로 12초에 맞추려 할 필요가 없습니다.

## 음악 스타일 권장

- 90s contemporary R&B / gospel-influenced pop soul / warm family love ballad
- 80~86 BPM 전후, 4/4, 느슨한 스윙
- Rhodes, 따뜻한 베이스, 드럼, 어쿠스틱 피아노, 절제된 스트링, 다층 가스펠 백킹
- 섬세한 벌스 → 풍성한 후렴 → 영적인 감사가 담긴 브리지 → 마지막 후렴의 화음 확장
- 특정 가수의 목소리, 기존 곡의 후렴/멜로디를 복제하지 않습니다.

### 웹 사용

1. <https://suno.com/create> 접속 → **Custom** 선택
2. **Lyrics**에 본인이 확정한 원곡 가사 전체, **Styles**에 악기·시대감·장르, **Title**에 곡명 입력
3. 모델은 이용 가능한 경우 **v6** 우선, 무료라면 **v6-mini**. `Instrumental`은 끕니다.
4. **Exclude**에 trap hi-hats, EDM drop, heavy autotune 등 원하지 않는 요소를 기록
5. 결과의 발음·음절·멜로디·보컬 질감을 확인하고 좋은 버전을 고릅니다.
6. 곡을 로컬로 내려받아 `video/public/media/music/suno-final.wav` 등에 저장합니다.

현재 공식 도움말(2026-09)은 v6/v6-wild/v6-mini 지원과 별도의 다운로드 할당량을 명시합니다.
- https://help.suno.com/en/articles/13924801
- https://help.suno.com/en/articles/2415873
- https://help.suno.com/en/articles/3161921
- https://help.suno.com/en/articles/13926209

곡 전체 길이와 4분 성장영상은 원본 실제 길이에 맞춰 후속 조정합니다.
Suno의 MP3/WAV로 저장할 수 있는지는 계정 플랜/다운로드 정책을 확인하세요.

## 로컬 영상 연결

~~~bash
sua-cold-open --props data/opening-props.json \
  --title-at 9 --song-start 12 \
  --music media/music/suno-final.wav
~~~

음악 자체의 드럼 어택이나 후렴을 자세히 파악하려면 `sua-audio-cues`가 보조적으로 쓸 수 있으나,
**곡 분석이 콜드 오픈에 필수는 아닙니다.**
이전 `sua-audio-cues --title-impact --verse-start` 방식은 **콜드 오픈 설정 용도로 사용하지 않습니다.**

## 권리·개인정보

- 공개 저장소에는 가사 초안·개인 음악을 자동 업로드하지 않습니다.
- Suno의 무료/유료 계정별 이용/다운로드 정책 및 상영/온라인 게시의 조건을 확인합니다.
- 계정의 생성물은 기본적으로 Link Only로 관리하고, 가족의 실명/민감한 에피소드 공개를 지양합니다.
- 공식 약관: https://help.suno.com/en/articles/9601601 · https://help.suno.com/en/articles/9601665
