# 고정된 모델

`registry.json`에 모델 버전·배포 출처·파일 크기·SHA256을 기록한다.

- **YuNet 2023mar**: 실제 제작에 사용한 232,589바이트 ONNX를 포함한다. 얼굴과 두 눈의 좌표를 찾아 기하학적으로 정렬하며 얼굴을 생성하지 않는다. [공식 모델과 MIT 라이선스](https://github.com/opencv/opencv_zoo/tree/48b10fa505aeb51fbd127fc60a5c660040e823b7/models/face_detection_yunet).
- **Whisper small**: 로컬 가사 정렬에 선택적으로 사용한다. 약461MiB 가중치는 Git에 포함하지 않으며, 공식 배포 파일의 SHA256을 고정한다. [공식 저장소](https://github.com/openai/whisper). 모델·코드 라이선스는 `whisper/LICENSE`에 있다.

기본 검사는 다운로드하지 않는다.

```sh
python3 scripts/setup_models.py
```

가사 정렬이 필요할 때만 다운로드 위치를 지정한다.

```sh
python3 scripts/setup_models.py --model whisper-small --cache-dir ../work/models --download
```

모델 실행과 미디어 처리는 로컬에서 수행한다. 이름·얼굴·가사 등의 개인 자료는 모델 파일에 포함하지 않는다. 자동 정렬 결과의 얼굴·각도·가사 시점은 실제 화면과 청취로 검토한다.
