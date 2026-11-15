# 이야기 자막

외부 `narrative-edit.json`의 선택 배열 `story_captions`로 여러 사진에 걸쳐 읽는 문장을 지정한다. `StoryNarration`은 개별 사진 `Sequence` 밖에 있으므로 컷 전환 때 문장이나 등장 시계를 초기화하지 않는다.

## 시계와 보호 구간

`start_frame` 포함, `end_frame` 제외인 본편 노래의 전역 프레임 구간을 사용한다. 오프닝 길이는 포함하지 않는다. 전체 영상에서의 위치는 `opening.duration_in_frames + start_frame`이다. 한 문장이 여러 컷을 덮도록 길이를 정할 수 있다.

문구는 모든 `choruses` 구간과 겹치면 안 된다. `narrative-edit.outro_alignment.lines`에서 `final_line_id`와 일치하는 줄의 시작부터 본편 끝까지도 서사 문구를 넣지 않는다. 해당 줄이 없으면 본편 끝이 상한이다. 후렴의 타이포그래피와 `OutroLyrics`의 동기화는 기존 경로를 유지한다.

필드를 생략하면 기존 `caption`·`captionCues`·이벤트 문구를 사용한다. 배열을 제공하면 이 컷별 표시를 끄고 전역 문구만 표시한다. 따라서 `[]`와 문구 사이의 빈 구간에는 컷별 문구로 되돌아가지 않는다.

## 구조와 배치

구조는 [runtime.schema.json](../schemas/runtime.schema.json)의 `$defs.storyCaption`, 타입은 [runtime-types.ts](../renderer/src/narrative/runtime-types.ts)의 `StoryNarrationCue`에 있다.

| 필드 | 조건·표시 |
| --- | --- |
| `id` | 필수, 공백뿐이 아닌 고유 문자열 |
| `text` | 필수, 빈 줄 없는 1~2줄; 줄바꿈은 `\n` |
| `start_frame`, `end_frame` | 필수, 0 이상 정수 시작과 그보다 큰 정수 끝; 시간순·중복 구간 금지 |
| `placement` | 선택, 기본 `bottom`; `left`·`right`도 허용 |
| `label`, `date_label` | 선택 문자열; `date_label`은 `label`이 있을 때 함께 표시 |
| `size` | 선택, 유한한 양수; 영역 폭과 배치별 최대 크기 안에서 자동 축소 |

`bottom`은 하단 중앙 카드, `left`·`right`는 각 측면의 텍스트 영역이다. 기준 화면은 1920×1080이며 최대 글자 크기는 하단 62, 측면 78이다. 화면 밖으로 나가는 문구는 렌더러 검증에서 거부한다. 미디어 회피를 자동으로 수행하는 것은 챕터 선화이므로, 문구 배치는 덮는 모든 사진·영상에서 확인한다.

다음은 필드만 보인 일반 예시다. 30fps에서 본편 첫 4초 동안 유지되며 중간 사진 컷에도 문장은 남는다. 실제 편집표의 후렴·아웃트로와 겹치지 않는 구간으로 조정한다.

```json
{
  "story_captions": [
    {
      "id": "chapter-intro",
      "text": "두 장의 사진,\n하나의 이야기",
      "start_frame": 0,
      "end_frame": 120,
      "placement": "bottom",
      "label": "새 장면"
    }
  ]
}
```

## 검증

템플릿 루트에서 다음을 실행한다. 경로는 일반 예시다.

```sh
python3.11 tools/validate_project.py --runtime-directory ../private/runtime
python3.11 tools/prepare_project.py --config ../private/project.json --check
npm run test:story --prefix renderer
```

Python 검증은 ID·문구 줄 수·정수 시각·순서·겹침·보호 구간·배치·크기·라벨을 검사한다. `prepare_project.py --check`는 실제 자산 연결도 검사한다. 렌더러의 [story-captions.ts](../renderer/src/narrative/story-captions.ts)는 같은 시간 조건과 화면 경계를 검사하며, `test:story`는 컷을 넘는 유지·종료 경계·보호 구간·배치 계산을 브라우저 없이 확인한다.

이 검사는 실제 브라우저 렌더나 연속 시청·청취를 입증하지 않는다. 브라우저를 실행할 수 있는 환경에서 [검수 안내](validation.md)에 따라 확인한다.
