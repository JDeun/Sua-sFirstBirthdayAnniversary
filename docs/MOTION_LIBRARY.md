# awesome-ai-motion 활용 평가 (2026-10-19)

원본: https://github.com/gongnyang/awesome-ai-motion

## 실제 확인

- 한국어 가이드: https://github.com/gongnyang/awesome-ai-motion/blob/main/README.ko.md
- Codex용 에이전트 스킬: https://github.com/gongnyang/awesome-ai-motion/blob/main/SKILL.md
- 모션 미리보기 웹사이트: https://gongnyang.github.io/awesome-ai-motion/
- README/SKILL의 공개 카탈로그 설명: 모션 효과 637개, 렌더 완료 클립 128개, 레시피 11개, 루트 7개. 숫자는 해당 리포지토리 설명을 참고한 것이며, 우리 프로젝트에서 전수 실행 검증한 값은 아닙니다.
- 저장소 LICENSE는 MIT이나 lib/·각 효과 카드에서 출처·제3자 라이선스를 별도 확인하라고 명시합니다.

## 기술적 결론

**Remotion을 기본 타임라인·렌더링 엔진으로 유지**하며 awesome-ai-motion은 에이전트가 목적에 맞는 움직임을 선정하는 참고 자료로 씁니다.

기본 예제는 HTML·GSAP·Playwright 중심이므로 Remotion/React 타임라인과 라이프사이클이 동일하지 않습니다. 영상 전체를 이 도구로 대체하거나 637개 소스를 통째로 가져올 필요가 없습니다.

| 장면 | 후보 카드 | 사용할 원리 | 도입 방식 |
|---|---|---|---|
| 출생→현재 초고속 얼굴 매치컷 | [morph-match-cut](https://github.com/gongnyang/awesome-ai-motion/tree/main/effects/morph-match-cut) | **중심/크기 일치 + 한 프레임 하드컷**. 아이 얼굴 자체를 모핑하지 않음 | 기존 OpenCV 정렬 + Remotion 하드컷 유지 |
| 강한 악센트 이후 타이틀 | [mask-reveal](https://github.com/gongnyang/awesome-ai-motion/tree/main/effects/mask-reveal) | 마스킹한 한 줄을 위로 올리고 완성 상태 홀드 | 원리만 재구현, 원본 에셋/JS 복사 금지 |
| 다정한 성장 사진 | [ken-burns](https://github.com/gongnyang/awesome-ai-motion/tree/main/effects/ken-burns) | 약한 1.05–1.12배 크롭/완만한 패닝 | 실제 미디어 연결 시 컴포넌트화 |
| 특별한 월령/챕터 | [kinetic-type-sweep](https://github.com/gongnyang/awesome-ai-motion/tree/main/effects/kinetic-type-sweep) | 큰 제목의 이동과 명확한 정지 | 짧은 구간만 이용, 과용 방지 |
| 타이틀 연출 조합 | [title-opener 레시피](https://github.com/gongnyang/awesome-ai-motion/tree/main/recipes/title-opener) | 진입, 전달, 정지 시간 확보 | 필요시 스토리보드 구성 참고 |

**주의:** 아기 얼굴은 형태 보간/생성형 모핑으로 변형하지 않습니다. 빠른 매치컷은 반복 플래시와 과도한 노출 변화 없이 구현하고 광과민성 위험을 검토합니다.

## Codex에서 스킬 사용하는 방법 (선택)

기존 Remotion Skills와 병행 사용할 수 있습니다. Mac 터미널에서:

~~~bash
git clone https://github.com/gongnyang/awesome-ai-motion.git ~/Dev/awesome-ai-motion
mkdir -p ~/.codex/skills
ln -s ~/Dev/awesome-ai-motion ~/.codex/skills/awesome-ai-motion
~~~

작업 전에 원본 SKILL.md와 효과별 README.md를 확인하십시오. 이미 동일한 링크/디렉터리가 있으면 덮어쓰지 않습니다. 이 절차는 **사용자의 Mac에서 직접 설치**하는 것이며 GitHub 작업만으로 로컬 Codex에 스킬이 설치되지는 않습니다.

권장 에이전트 순서:
1. 이번 장면의 감정적 목적을 정의
2. 결정표에서 두세 효과 후보 선택
3. 실제 효과 카드를 읽고 파라미터·과용 주의 분석
4. 기법을 Remotion 컴포넌트로 **별도 구현**
5. 0%, 50%, 100% 시점 프레임 캡처·검수
6. 외부 예제 코드·이미지·폰트 등을 직접 도입할 때 개별 라이선스 확인

## 채택하지 않는 것

- 전체 라이브러리 Git submodule로 추가: 과다한 파일·예제·외부 리소스·라이선스 검토 부담
- GSAP 런타임을 전체 Remotion 장면에 무조건 투입: 프레임 단위 렌더/seek 호환 리스크
- 예제의 morph 컷을 영아 얼굴 간 자동 합성에 적용: 개인정보·왜곡 우려
- 원본 클립·GIF를 가져다 완성 영상에 삽입: 디자인/저작권 통일성 훼손

참고 경로는 문서화하되 실제 편집 결과는 **수아의 사진에 맞춰 독자 제작**합니다.
