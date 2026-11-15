# 외부 구성 요소

저장소 소유자가 작성한 코드와 문서의 권리 방침은 루트 `LICENSE`에 있다. 아래 외부 구성 요소에는 각각 원래 라이선스가 적용된다.

| 구성 요소 | 사용 범위 | 출처·라이선스 확인 |
| --- | --- | --- |
| YuNet 2023mar | 얼굴·눈 검출용 고정 ONNX | [공식 모델](https://github.com/opencv/opencv_zoo/tree/48b10fa505aeb51fbd127fc60a5c660040e823b7/models/face_detection_yunet), `models/yunet/LICENSE` |
| Whisper small | 선택적 로컬 가사 정렬, 가중치는 별도 다운로드 | [공식 저장소](https://github.com/openai/whisper), `models/whisper/LICENSE` |
| Remotion와 React | 프레임 렌더링·장면 구성 | 설치된 각 패키지의 `LICENSE`와 [Remotion 라이선스 안내](https://www.remotion.dev/license) |
| FFmpeg·FFprobe | 로컬 미디어 분석·변환·검사 | 실제 설치한 바이너리의 빌드 옵션과 라이선스 |
| OpenCV·NumPy·Pillow·SciPy·librosa·stable-ts·PyTorch | 선택한 로컬 분석·정렬·마스킹 도구 | 설치된 각 패키지의 라이선스 |
| HandForge | 사용자 요청 손글씨 타이틀의 선택적 로컬 사전 렌더 | [고정 커밋 `d4f7d1926028d6484d9889b42589f04e2bf5c861`](https://github.com/gongnyang/handforge/tree/d4f7d1926028d6484d9889b42589f04e2bf5c861), [MIT 래퍼와 예외](https://github.com/gongnyang/handforge/blob/d4f7d1926028d6484d9889b42589f04e2bf5c861/LICENSE) |
| storyboard-ai | HandForge가 호출하는 손 드로잉 엔진; 격리된 LOCAL 제작 환경에서만 사용, 템플릿에 미포함 | [원본 엔진·GPL-3.0](https://github.com/yogendra-yatnalkar/storyboard-ai) |
| awesome-ai-motion | 사용자 요청에 따른 모션 가이드 참고; 렌더 엔진으로 사용하지 않음 | [고정 커밋 `1e3c249073c61b42ceb556d7800f628d565d9312`](https://github.com/gongnyang/awesome-ai-motion/tree/1e3c249073c61b42ceb556d7800f628d565d9312), [MIT·별도 구성 요소 안내](https://github.com/gongnyang/awesome-ai-motion/blob/1e3c249073c61b42ceb556d7800f628d565d9312/LICENSE) |
| Nanum Pen Script | 로컬 제작 타이틀 영상에만 사용; 본편 공통 폰트로 적용하지 않음 | [Google Fonts·SIL OFL-1.1](https://github.com/google/fonts/blob/main/ofl/nanumpenscript/OFL.txt) |

Node.js 의존성의 정확한 버전은 `renderer/package-lock.json`으로 고정한다. Python 기본·선택 의존성은 requirements 파일에 구분한다. 다운로드한 제3자 가중치나 라이브러리의 저작권을 프로젝트 소유자의 저작권으로 표시하지 않는다.

HandForge의 MIT는 래퍼 코드에 적용되며, 하위 storyboard-ai 엔진의 GPL-3.0이나 별도 미디어의 권리를 대체하지 않는다. 래퍼·GPL 엔진·외부 샘플 미디어·폰트 바이너리·개인 타이틀 영상은 공개 템플릿에 번들하지 않는다. 렌더러는 선택 항목 `copy.assets.greeting`으로 사전 제작한 영상을 읽는다.

챕터 선화 `renderer/src/assets/StoryDoodles.tsx`는 직접 작성한 프레임 기반 SVG다. awesome-ai-motion의 모션 가이드를 참고했으며 외부 실행 코드나 참조 영상을 포함하지 않는다.
