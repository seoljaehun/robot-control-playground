> 승인·이력(2026-10-16): 사용자 검토 완료 후 FK Tasks부터 PR 검증까지 진행하도록 승인받았다. 현재 기능 Branch는 codex/001-forward-kinematics이다. 아래 검토 대기·첫 Commit 전·문서만 생성 등의 문구는 생성 당시 기록이며 요구사항과 설계는 그대로 유지한다.

# Implementation Plan: Forward Kinematics (FK)

**Branch**: 실제 Git `main` (첫 Commit 전) | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-forward-kinematics/spec.md`

**Status**: 사용자 Plan 검토 대기. 사용자의 이번 지시를 Constitution·Spec 검토 완료의
근거로 삼는다. 두 원본 문서의 기존 상태 표기는 수정하지 않는다.
setup-plan의 BRANCH=001-forward-kinematics는 기능 디렉터리 기반 식별자이며 Git 브랜치가 아니다.
이번 작업은 Phase 0·1 설계 문서만 생성한다. 코드·테스트·Tasks 및 Git 이력은 생성하지 않는다.

## Summary

두 관절 각도와 링크 길이로 끝점 위치를 계산하는 순수 스칼라 FK 함수를 설계한다.
해석적 기구학, 명시적 입력 검증, NumPy float64 계산과 pytest 검증을 사용한다.
시각화·IK·Jacobian·제어기는 범위 밖이다. API와 오류 정책은
[contracts/fk-api.md](contracts/fk-api.md), 결정 근거는 [research.md](research.md)에 기록한다.

## Technical Context

**Language/Version**: Python 3.11.

**Primary Dependencies**: 런타임 NumPy, 검증 pytest. 추가 수학·검증 도구는 표준 라이브러리만 사용.
Matplotlib은 상위 프로젝트 시각화 단계의 도구이며 FK의 의존성과 import에는 포함하지 않는다.
NumPy·pytest의 설치 버전은 구현 시 Python 3.11 호환성을 확인하고 실제 버전을 기록한다.
이번 계획에서는 미설치 버전을 설치·검증했다고 주장하지 않는다.

**Storage**: 계산 상태·데이터베이스 없음. 검증 보고는 기존 기능 디렉터리에 기록한다.

**Testing**: NumPy 비교 도구와 pytest; 기본 명령은 루트의 `python -m pytest`.
축 방향 기준값, Taylor 근사 및 표준 라이브러리 복소 회전으로 독립 검증한다.

**Target Platform**: Windows 10, RAM 8GB, CPU 전용. GPU·네트워크 서비스 불필요.

**Project Type**: 로컬 Python 기구학 라이브러리. CLI·웹·GUI 없음.

**Performance Goals**: 한 자세 계산은 O(1) 시간·메모리. 승인된 지연 시간 목표가 없으므로
임의 벤치마크 gate를 추가하지 않는다. 정밀도 목표는 정상 수치 조건에서 성분별 1e-9 m.

**Constraints**: 네 스칼라 실수 입력, 유한 양수 링크, 유한 각도, 유한 결과 또는 명시적 실패.
기본 사례·주기 검증에 상대 오차를 추가해 1e-9 m 기준을 완화하지 않는다.

**Scale/Scope**: 공개 함수 하나, 기구학 모듈 하나, 테스트 파일 하나.
아래 소스 트리는 향후 구현 대상이며 이번 작업에서 만들지 않는다.

## Constitution Check

*GATE: Phase 0 이전 확인 및 Phase 1 설계 후 재확인.*

| 원칙 | 설계 전 확인 | 설계 후 확인 |
|------|--------------|--------------|
| I Mathematical Correctness | 좌표계·단위·경계 조건이 Spec에 정의됨 | 아래 공식·수치 한계·독립 기준값으로 반영 |
| II SDD | 사용자 지시로 Spec 검토 완료 전제 확인 | Plan만 작성, Tasks·구현은 검토 이후 |
| III Testing & Reproducibility | pytest·기록 필수 확인 | 모든 FR/SC의 검증 경로와 명령 정의 |
| IV Minimal Architecture | 경량 라이브러리 범위 확인 | NumPy·pytest와 최소 파일만 계획 |
| V Independent Verification | B의 읽기 전용 역할 확인 | 동일 SHA 독립 계산·판정 절차 유지 |
| VI Git Traceability | main 첫 Commit 전, 원격 설정 존재 확인 | 이력 연결·기능 Branch는 구현 전 준비 gate |
| VII Human Approval | 중요 설계는 사용자 검토 대상 | 이 Plan 승인 전 Tasks·구현 금지 |

설계 문서 작성에 대한 원칙 위반 없음. 이는 구현 PASS 또는 Merge 승인이 아니다.
Git gate는 문서 작성 자체를 막지 않지만 구현 전 해결해야 한다.
사용자 변경을 보존하고 원격 main 이력을 확인·연결한 뒤 기능 Branch에서 구현한다.
자동 hook이 없으며 이번 작업에서는 Branch 생성·Fetch·Commit·Push를 수행하지 않는다.

## Project Structure

### Documentation (this feature)

```text
specs/001-forward-kinematics/
├── spec.md                       # 기존 승인 Spec, 수정 금지
├── checklists/requirements.md     # 기존 Spec 품질 검토, 수정하지 않음
├── plan.md                       # 기술 계획
├── research.md                   # Phase 0 결정·대안·근거
├── data-model.md                 # 값과 검증 규칙
├── contracts/fk-api.md            # 공개 Python 함수 계약
└── quickstart.md                 # 향후 검증 실행 안내
```

tasks.md는 Plan 승인 후 별도 명령의 산출물이며 이번에는 생성하지 않는다.
검증 결과 기록은 구현 후 이 디렉터리의 verification.md에 작성한다.
A 자체 검증과 B 독립 검증은 담당자·명령·대상 SHA를 구분해 기록한다.

### Source Code (repository root)

```text
robot_control/
├── __init__.py
└── kinematics.py
tests/
└── test_forward_kinematics.py
requirements.txt
.gitignore
```

**Structure Decision**: 루트 패키지는 `python -m pytest` 실행 시 직접 import한다.
src 레이아웃·빌드 백엔드·editable 설치·conftest 경로 주입은 필요하지 않다.
공개 경로는 `robot_control.kinematics.forward_kinematics`로 고정한다.
`__init__.py`는 비어 있어도 되며 재노출 인터페이스를 추가하지 않는다.
requirements.txt는 NumPy·pytest만 선언하고 검증 환경의 실제 버전을 보고에 기록한다.
.gitignore는 구현 단계에 Python 캐시·가상 환경 항목을 최소 작성한다.

## Complexity Tracking

정당화가 필요한 Constitution 위반 없음. 추가 프레임워크·클래스 계층·저장소 계층 없음.

## Mathematical Model & Numerical Policy

### 좌표계·공식·단위

Base는 (0, 0) m, x 오른쪽·y 위쪽·z 화면 밖의 오른손 좌표계다.
+z 기준 반시계 방향이 양의 회전이다. theta1은 기준 x축에 대한 Link 1 각도,
theta2는 Link 1에 대한 Link 2 상대 각도다. 링크는 강체이고 동역학은 고려하지 않는다.

`x = l1*cos(theta1) + l2*cos(theta1 + theta2)`

`y = l1*sin(theta1) + l2*sin(theta1 + theta2)`

theta1·theta2는 rad, l1·l2 및 x·y는 m이다.
삼각함수 인자는 rad의 수치값이며 rad는 무차원으로 취급한다.
기본 링크 (1.0, 0.8) m, 기본 자세 (0, pi/2) rad의 결과는 (1.0, 0.8) m이다.

### 실제 수치 평가

각도는 정규화하지 않는다. c1=cos(theta1), s1=sin(theta1),
c2=cos(theta2), s2=sin(theta2)를 각각 NumPy float64로 계산한다.
두 번째 링크 방향은 C=c1*c2-s1*s2, S=s1*c2+c1*s2로 계산하여
x=l1*c1+l2*C, y=l1*s1+l2*S를 평가한다.
덧셈정리는 원래 FK와 수학적으로 동치이며, theta1+theta2 자체의 overflow를 피한다.
반올림 오차가 있으므로 모든 극단값의 실수 해에 대한 동일 절대 오차를 보장하지 않는다.

입력 타입 확인 → 원래 값의 유한성 확인 → binary64 변환 → 변환 한계 확인 →
링크 양수 확인 → 삼각함수·위치 계산 → 최종 좌표 유한성 확인 순서다.
정수 유한성은 정수 성질로 판정하고 너무 큰 정수의 변환 overflow는 별도로 처리한다.
확장 정밀도 NumPy 값은 변환 전 원본 유한성을 확인한다.
유한 양수 링크가 변환 과정에서 0이 되면 입력 0으로 취급하지 않고 표현 실패로 처리한다.

계산 블록의 NumPy 오류 정책은 over=raise, invalid=raise, divide=raise, under=ignore다.
지역 `np.errstate`로 제한하고 기존 호출자의 오류 설정을 복원한다.
발생한 FloatingPointError 또는 비유한 결과는 공개 계약의 OverflowError로 변환한다.
중간 overflow도 명시적 계산 실패다. underflow로 작은 곱이 0으로 반올림되는 것은 허용한다.
입력을 절댓값·clipping·기본값으로 바꾸지 않는다. 결과를 0으로 강제 보정하지 않는다.

큰 각도는 float64의 각도 표현 간격과 삼각함수 인자 축소 오차의 영향을 받는다.
매우 큰 링크의 오차는 길이와 함께 커지며, 완전 접힘에서도 잔여값이 발생할 수 있다.
이 한계는 승인 Spec의 정상 수치 조건 제한과 일치한다.
0 또는 ±pi의 특이 자세에서 FK는 정의되며 역문제의 특이점은 실패 사유가 아니다.

## Interface & Responsibility Boundaries

문서상의 Python 서명:
`forward_kinematics(theta1: float | int | np.integer | np.floating, theta2: float | int | np.integer | np.floating, l1: float | int | np.integer | np.floating, l2: float | int | np.integer | np.floating) -> tuple[float, float]`

인자 네 개는 모두 필수이며 기본 링크값을 숨겨 두지 않는다.
Python int·float 및 NumPy 정수·실수 스칼라를 허용하며 float64로 계산한다.
지원 타입 이외의 Decimal·Fraction 등 임의 수치 객체는 자동 변환하지 않고 TypeError로 거부한다.
bool·np.bool_·복소수·문자열·None·컨테이너·모든 ndarray(0-D 포함)는 TypeError다.
NaN·±Infinity·0 이하 링크는 ValueError, 유한값 변환·계산 표현 한계는 OverflowError다.
필수 인자 누락은 Python의 TypeError로 식별된다.
메시지는 입력 오류에 인자명과 조건, 계산 오류에 실패 단계를 포함한다.
문구 전체의 일치 대신 인자명·조건·예외 클래스를 검증한다.

함수는 값 반환만 수행한다. 입력 변경, 파일 기록, 화면 표시, Matplotlib import,
난수·환경 설정의 영구 변경을 하지 않는다.
시각화는 후속 기능이 이 좌표 결과를 소비하는 책임이며 이번에는 모듈을 생성하지 않는다.

## Verification Strategy & Requirement Traceability

정상 사례는 `np.testing.assert_allclose`에 atol=1e-9, rtol=0을 명시한다.
평가 기준은 각 좌표의 절대 오차이며 norm이나 NumPy 기본 상대 오차로 대체하지 않는다.
아래는 향후 작성·실행할 검증 설계이며 이번에 테스트를 실행한 결과가 아니다.

| 검증 그룹 | 사례·독립 기준 | 연결 |
|-----------|---------------|------|
| T1 기준 자세 | Spec A1–A6 값 전부, 축 방향 길이 합·기하학적 기준값 직접 사용 | US1, FR-001–002, SC-001 |
| T2 값 검증 | l1/l2 각각 0, -0.0, -1; 네 입력 각각 NaN, +inf, -inf | US2.1–2, FR-003, SC-002 |
| T3 타입·누락 | 네 입력 각각 문자열, complex, bool, np.bool_, None, list, tuple, 0-D·1-D ndarray; 인자 누락 | US2.3, FR-004, SC-002 |
| T4 수치 한계 | 아래 extreme 사례와 예외·오류 설정 복원 | US2.4, FR-004 |
| T5 경계 | Spec US3.1–4의 ±pi, 링크 같음·순서 반전·완전 접힘/펼침 | FR-005–006, SC-001,003 |
| T6 주기 | k1,k2=-2..2의 25개 조합과 양쪽 pi 경계 | US3.5, FR-006, SC-003 |
| T7 근접 | theta2=±δ, pi±δ, theta1=0, δ=1e-6 | US3.6, FR-005, SC-001 |
| T8 독립 일반값 | theta1=pi/4, theta2=-pi/2, 기본 링크: (1.8/sqrt(2),0.2/sqrt(2)) | FR-002,009 |
| T9 순수성·재현 | A1–A6 각각 동일 환경 3회 좌표 완전 동일; 그림 없이 계산, 오류 설정 복원 | FR-007, SC-004 |
| T10 기록·추적 | 모든 FR/SC·시나리오의 명령·환경·SHA·결과·미실행 항목 보고 | FR-008–009, SC-005 |

T3는 정상 NumPy 정수·실수 스칼라와 Python 정수의 수용 사례도 포함한다.
에러 사례는 한 인자만 교체하여 원인을 분리한다. T8의 sqrt는 표준 라이브러리로 구한다.

T7 독립 기준은 삼각함수 호출을 복제하지 않고 Taylor 다항식으로 구성한다.
c=1-δ²/2+δ⁴/24, s=δ-δ³/6+δ⁵/120을 사용한다.
±δ의 기준은 (1+0.8*c, ±0.8*s), pi±δ의 기준은 (1-0.8*c, ∓0.8*s) m이다.
sin의 생략항은 |δ|⁷/7!, cos는 |δ|⁶/6! 이하로 1e-9 m보다 충분히 작다.
실제 pi±δ의 binary64 표현 오차도 m 규모에서 허용량보다 작다.
이는 이론적 오차 근거이며 실측 통과 결과가 아니다.

T4 세부 사례:
- (theta1,theta2)=(0,0), l1=l2=1e-300: (2e-300,0)과 비교.
  이 추가 극단값 시험만 x의 상대 허용량 1e-14, y=0을 적용한다.
- (0,0), l1=l2=1e150: (2e150,0), 같은 상대 허용량을 적용한다.
  위 두 추가 시험의 상대 기준은 정상 사례의 1e-9 m 절대 기준을 변경하지 않는다.
- (0,0), l1=l2=float64 최대 유한값: 위치 합 overflow로 OverflowError.
- theta1=theta2=1e308, 기본 링크: 유한 결과를 확인하며 정밀도 보장 시험으로 쓰지 않는다.
  추가 기준은 표준 cmath.exp의 두 복소 회전 곱으로 얻고 성분별 1e-9 m 내 일치 여부를
  확인하되, 서로 다른 삼각함수 구현의 일치는 참 실수 해의 정확성 증명이 아니다.
- Python 정수 10**1000: 변환 OverflowError. 확장 NumPy 실수에서 binary64 범위 밖의
  유한값 또는 양수→0 변환이 가능한 환경은 같은 실패를 검증한다.
  플랫폼의 longdouble 범위가 float64와 같으면 해당 확장형 사례만 이유와 함께 skip한다.
- 최소 양의 float64 링크도 0 이하로 오인하지 않고 수용한다.
  출력 underflow 자체는 실패가 아니다. 반환값의 유한성을 확인한다.
- 호출자의 NumPy 오류 설정을 변경해도 함수가 지역 정책을 사용하고 종료 후 원복함을
  성공·실패 두 경로에서 확인한다. 테스트 자체도 기존 환경을 반드시 복원한다.

Agent B는 같은 Commit에서 테스트를 실행하고 A의 기준값만 신뢰하지 않는다.
축 방향 해석, pi/4의 기하학, Taylor 근사 또는 복소 회전의 독립 근거를 직접 확인한다.
부동소수점 제한·플랫폼 skip·실행하지 못한 검증을 명시하고 PASS/FAIL/BLOCKED를 판정한다.
미실행 시 PASS를 선언하지 않으며 B의 PASS와 사용자 Merge 승인을 구분한다.

## Implementation Sequence & Completion Criteria

1. 사용자 Plan 검토를 완료한다. 원격·로컬 이력과 사용자 변경을 보존하고
   기능 Branch·작업 위치를 확정한다. Plan 승인 후 별도 Tasks 명령으로 작업을 세분화한다.
2. 최소 패키지·의존성·ignore 설정을 구성하고 실제 Python·NumPy·pytest 버전을 기록한다.
3. T1–T3·T5–T9의 필요한 테스트를 먼저 작성해 미구현 실패를 확인한다.
   승인된 API에 따라 입력 검증·FK 계산·오류 처리를 구현하고 재실행한다.
4. T4 표현 한계·오류 환경 복원을 보강하고 전체 `python -m pytest`를 실행한다.
   이 순서는 후속 Tasks가 구체화할 구현 흐름이며 tasks.md를 대체하지 않는다.
5. A는 변경 범위·명령·실제 결과·대상 SHA를 보고한다. 승인된 Git 작업 범위에서 PR을
   준비한 뒤 B가 동일 HEAD를 독립 검증하고 결함은 A 수정·B 재검증으로 해결한다.

기능 완료는 모든 FR/SC 및 필수 테스트 충족, 독립 검증, 미해결 중요 결함 없음,
재현 가능한 기록으로 판단한다. Merge에는 현재 HEAD에 대한 B의 PASS와 사용자 최종
Merge 승인이 추가로 필요하다. 이번 문서 작성 완료를 기능 완료로 해석하지 않는다.

## Review Notes & Remaining Preparation

설계상 미해결 선택지는 없다. 구현 전 환경 호환성·실제 의존성 버전·Git 이력 연결은
준비 작업이다. 기존 Constitution·Spec의 승인 대기 표기는 이번 사용자 지시와 차이가
있으나 승인된 내용을 변경하지 않고, 승인 근거를 본 계획에 기록했다.
성능 수치·테스트 결과·설치 성공을 아직 주장하지 않는다.
