# 얼굴 검출·정렬 라이브러리

프로젝트 설정·가사·테마·Remotion 없이 사용하는 Python 패키지다. 이 폴더를 Python import 경로에 두면 다른 제작 도구에서도 쓸 수 있다. NumPy·Pillow·OpenCV는 함수 호출 시 필요하며, `import face_matchcut`만으로 모델을 내려받지 않는다.

```python
from PIL import Image, ImageOps
from face_matchcut import align_image

with Image.open("portrait.jpg") as source:
    image = ImageOps.exif_transpose(source).convert("RGB")

aligned, evidence = align_image(
    image,
    eyes=[[180, 220], [300, 220]],
    target_eyes=[[850, 430], [1070, 430]],
    size=(1920, 1080),
)
aligned.save("aligned.png")
```

좌표는 방향을 바르게 세운 RGB 이미지의 픽셀 기준이며, 대상 얼굴·방향과 눈 좌표를 먼저 검토한다. 두 눈의 순서는 목표점과 대응해야 한다. 결과는 원본 픽셀의 회전·배율·이동과 경계 블렌딩으로 구성한다.

공개 API는 `similarity`, `align_image`, `detect`, `rotation`, `restore`, `overlap`이다. `detect(image, model_path)`는 YuNet 후보만 반환하며 사람을 자동 선택하지 않는다. 모델은 호출자가 명시한 로컬 경로에서 읽는다. 출처·라이선스는 [모델 안내](../../models/README.md)에 있다.

검토한 주석을 여러 사진에 적용하는 명령은 상위 `tools/build_matchcut.py`, 단일 사진 후보 확인은 `tools/align_faces.py`다. 이 CLI들은 경로·해시·EXIF·출력을 연결하는 어댑터이며, 패키지 자체는 `filmtools`에 의존하지 않는다.

직접 작성한 코드와 문서는 저장소 소유자의 `All rights reserved` 방침을 따른다. 외부 라이브러리와 YuNet 모델은 각각의 원래 라이선스를 유지한다.
