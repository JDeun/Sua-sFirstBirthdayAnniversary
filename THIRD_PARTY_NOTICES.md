# 외부 구성 요소

저장소 소유자가 작성한 코드와 문서의 권리 방침은 루트 `LICENSE`에 있다. 아래 외부 구성 요소에는 각각 원래 라이선스가 적용된다.

| 구성 요소 | 사용 범위 | 출처·라이선스 확인 |
| --- | --- | --- |
| YuNet 2023mar | 얼굴·눈 검출용 고정 ONNX | [공식 모델](https://github.com/opencv/opencv_zoo/tree/48b10fa505aeb51fbd127fc60a5c660040e823b7/models/face_detection_yunet), `models/yunet/LICENSE` |
| Whisper small | 선택적 로컬 가사 정렬, 가중치는 별도 다운로드 | [공식 저장소](https://github.com/openai/whisper), `models/whisper/LICENSE` |
| Remotion와 React | 프레임 렌더링·장면 구성 | 설치된 각 패키지의 `LICENSE`와 [Remotion 라이선스 안내](https://www.remotion.dev/license) |
| FFmpeg·FFprobe | 로컬 미디어 분석·변환·검사 | 실제 설치한 바이너리의 빌드 옵션과 라이선스 |
| OpenCV·NumPy·Pillow·SciPy·librosa·stable-ts·PyTorch | 선택한 로컬 분석·정렬·마스킹 도구 | 설치된 각 패키지의 라이선스 |

Node.js 의존성의 정확한 버전은 `renderer/package-lock.json`으로 고정한다. Python 기본·선택 의존성은 requirements 파일에 구분한다. 다운로드한 제3자 가중치나 라이브러리의 저작권을 프로젝트 소유자의 저작권으로 표시하지 않는다.
