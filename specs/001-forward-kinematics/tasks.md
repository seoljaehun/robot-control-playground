# Tasks: Forward Kinematics (FK)

**Input**: `specs/001-forward-kinematics/`의 승인된 spec.md·plan.md·research.md·data-model.md·contracts/fk-api.md.
**Prerequisites**: 사용자 승인 완료(2026-10-16 대화), 필수 pytest 검증.
**Organization**: Setup → Foundational → US1 → US2 → US3 → Polish. 구현 전에 각 테스트의 실패를 확인한다.
**Scope**: FK만 구현한다. IK·Jacobian·추종·시각화 구현 없음. PR Merge 금지.

## Format: `[ID] [P?] [Story] Description`

모든 경로는 저장소 루트 기준이다. `[P]`는 서로 다른 파일이고 선행 의존성이 없을 때만 쓴다.
같은 코드·테스트 파일을 수정하는 이야기들은 순차 실행한다.

## Path Conventions

`robot_control/kinematics.py`, `robot_control/__init__.py`, `tests/test_forward_kinematics.py`를 사용한다.
관련 문서는 기존 `specs/001-forward-kinematics/`에 둔다. 별도 중복 기준 문서를 만들지 않는다.

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 현재 Git 상태·원격 main 이력·사용자 파일 보존을 확인하고 기능 Branch를 사용하며 `specs/001-forward-kinematics/verification.md`에 작업 위치와 기준 SHA를 기록한다.
- [X] T002 Python 3.11 환경을 준비하고 `requirements.txt`에 NumPy·pytest만 선언하며 실제 Python·의존성 버전 및 설치 명령을 `specs/001-forward-kinematics/verification.md`에 기록한다.
- [X] T003 기존 `.gitignore`를 보존하고 Python 캐시·가상 환경 제외를 확인한다. 필요한 항목만 추가하고 `robot_control/__init__.py`와 `tests/`의 최소 구조를 준비한다.
- [X] T004 사용자 승인에 따라 `ARCHITECTURE.md`, `TASKS.md`, `PROJECT_STATE.md`의 내용을 삭제하지 않고 이전 미채택 초안임을 표시한다. `PROJECT_STATE.md`에는 현재 SDD 문서 경로·승인 근거를 기록하고 `PROJECT_PLAN.md`·`AGENTS.md`의 과거 상태 설명은 역사적 기록임을 명확히 한다.

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T005 `specs/001-forward-kinematics/contracts/fk-api.md`의 필수 인자 순서·반환·예외와 `data-model.md`의 "스칼라 실수·유한값", "스칼라 실수·유한값·각각 >0", "float 두 개·각각 유한값" 제약을 구현 전 확인한다. 임의 모델 클래스는 생성하지 않는다.
- [X] T006 `specs/001-forward-kinematics/verification.md`에 Analyze 결과, FR/SC·수용 시나리오→Tasks 대응, 실행·미실행 구분과 실패 기록 형식을 마련한다. 기존 Spec·Plan의 의미는 변경하지 않는다.

**Checkpoint**: Python 3.11·의존성·기능 Branch·계약 확인이 끝난 후 이야기별 구현을 시작한다.

## Phase 3: User Story 1 - 알려진 자세의 끝점 위치 확인 (Priority: P1) MVP

**Goal**: 네 스칼라 입력으로 정확한 끝점 좌표를 얻는다.
**Independent Test**: A1–A6와 일반 pi/4 기준값, 성분별 atol=1e-9 m·rtol=0.

### Tests for User Story 1 (필수)

- [X] T007 [US1] `tests/test_forward_kinematics.py`에 A1–A6, 입력 단위·상대 theta2 해석, 필수 인자·keyword 호출, tuple[float,float] 반환 계약의 테스트를 먼저 작성하고 미구현 실패를 실행·기록한다. [FR-001, FR-002, SC-001]
- [X] T008 [US1] `tests/test_forward_kinematics.py`에 theta1=pi/4·theta2=-pi/2의 독립 sqrt(2) 기준값과 A1–A6 각각 3회 완전 동일 결과를 검증한다. 그림 없이 import·호출 가능함을 확인한다. [FR-007, FR-009, SC-004]

### Implementation for User Story 1

- [X] T009 [US1] `robot_control/kinematics.py`에 승인된 공개 forward_kinematics 함수를 구현한다. 각도 rad·길이 m, Base·CCW·상대 theta2를 문서화하고 NumPy float64 sin/cos 덧셈정리로 FK를 평가한다. 각도 정규화·직접 각도 합·시각화 import·입력 변경·파일 기록은 하지 않는다. [FR-001, FR-002, FR-007]
- [X] T010 [US1] `tests/test_forward_kinematics.py`의 US1 검증을 실행하고 실제 결과 및 구현 전 실패→구현 후 결과를 `specs/001-forward-kinematics/verification.md`에 기록한다. [FR-008, FR-009, SC-001, SC-004]

## Phase 4: User Story 2 - 잘못된 입력의 명시적 거부 (Priority: P1)

**Goal**: 타입·값·표현 실패를 명시적으로 구분한다.
**Independent Test**: 각 인자를 독립 교체하여 모든 잘못된 입력의 예상 예외를 확인한다.

### Tests for User Story 2 (필수)

- [X] T011 [US2] `tests/test_forward_kinematics.py`에 l1/l2 각각 0·-0.0·음수, 네 입력 각각 NaN·±Infinity의 ValueError와 인자명·조건 식별을 검증하는 테스트를 먼저 작성·실행한다. [FR-003, SC-002]
- [X] T012 [US2] `tests/test_forward_kinematics.py`에 문자열·complex·bool·np.bool_·None·컨테이너·0-D/1-D ndarray·Decimal·Fraction·누락 인자의 TypeError 및 Python/NumPy 정상 스칼라 수용 테스트를 먼저 작성·실행한다. 복수 오류에서 계약의 단계·인자 우선순위도 검증한다. [FR-003, FR-004, SC-002]
- [X] T013 [US2] `tests/test_forward_kinematics.py`에 Plan T4 전체 사례를 먼저 작성·실행한다: tiny/huge 길이, 최대 float64 위치 합, 1e308 각도, 10**1000, 최소 양수, 가능한 longdouble 변환 overflow·양수→0, 성공·실패 경로의 NumPy 설정 복원. 플랫폼 불가 확장형 사례만 사유를 기록해 skip한다. [FR-004, FR-007, SC-002]

### Implementation for User Story 2

- [X] T014 [US2] `robot_control/kinematics.py`에서 계약 순서(타입→원본 유한성→float64 변환→링크 양수→계산)를 적용한다. 데이터 모델의 "링크 0·-0.0·음수 및 네 입력의 NaN·±Infinity는 ValueError"와 "bool·np.bool_, complex, 문자열, None, list·tuple 및 ndarray(0-D 포함)는 거부한다"를 준수한다. [FR-003, FR-004]
- [X] T015 [US2] `robot_control/kinematics.py`에서 유한값 변환·계산 한계는 OverflowError로 처리한다. 지역 errstate(over/invalid/divide=raise, under=ignore)·최종 유한성·양수 링크 변환 시 0 검사를 적용하고 호출자 설정을 복원한다. [FR-004, FR-007]
- [X] T016 [US2] `tests/test_forward_kinematics.py`의 US1·US2 검증을 실행하고 예상 예외·실제 결과·skip 사유를 `specs/001-forward-kinematics/verification.md`에 기록한다. [FR-008, FR-009, SC-002, SC-005]

## Phase 5: User Story 3 - 접힘·펼침과 주기적 각도 검증 (Priority: P2)

**Goal**: 특이 자세도 유효한 FK 입력이며 주기 등가성이 유지된다.
**Independent Test**: US3.1–6 전부, 성분별 절대 오차 1e-9 m 이하.

### Tests for User Story 3 (필수)

- [X] T017 [US3] `tests/test_forward_kinematics.py`에 US3.1–4(완전 접힘·펼침, ±pi, 같은 링크·링크 순서 반전)의 독립 길이 합·차 기준을 작성·실행한다. 이미 구현된 동작은 즉시 통과해도 되며 가짜 실패를 만들지 않는다. [FR-005, FR-006, SC-001, SC-003]
- [X] T018 [US3] `tests/test_forward_kinematics.py`에 k1,k2=-2..2의 25개 주기 조합 및 theta2=±1e-6, pi±1e-6의 독립 Taylor 기준값을 추가한다. atol=1e-9·rtol=0을 유지한다. [FR-005, FR-006, FR-009, SC-001, SC-003]

### Implementation for User Story 3

- [X] T019 [US3] `robot_control/kinematics.py`의 특이 자세·동일 길이·정규 범위 밖 각도 수용을 확인하고 일반 버그만 수정한다. 임의 각도 제한·정규화·0 보정은 추가하지 않는다. [FR-005, FR-006]
- [X] T020 [US3] `tests/test_forward_kinematics.py` 전체를 실행해 US3.1–6과 모든 기존 사례가 유지되는지 확인하고 `specs/001-forward-kinematics/verification.md`에 실제 결과를 기록한다. [FR-008, FR-009, SC-001, SC-003, SC-005]

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T021 `specs/001-forward-kinematics/quickstart.md`를 실제 Python 3.11 경로·환경 준비·설치 및 실행 명령으로 명확히 하고 기본 자세 수동 호출을 실제 실행한다. 계획 기준은 바꾸지 않는다. [FR-007, FR-009, SC-005]
- [X] T022 `README.md`에 FK 실행·테스트·Spec 링크·단위·범위·한계와 Python 3.11 준비를 간결히 작성한다. 다른 기능은 구현하지 않는다. [FR-007, FR-009, SC-005]
- [X] T023 루트에서 Python 3.11로 전체 `python -m pytest`를 실행하고 모든 FR-001–009·SC-001–005·A1–A6·US2.1–4·US3.1–6의 결과·skip·미실행·실제 버전과 명령을 `specs/001-forward-kinematics/verification.md`에 기록한다. [FR-008, FR-009, SC-001–005]
- [X] T024 `robot_control/kinematics.py`, `tests/test_forward_kinematics.py`, `.gitignore`와 문서 diff를 자체 검토하고 `specs/001-forward-kinematics/verification.md`에 범위 밖 구현 없음·사용자 파일 보존·미해결 결함 여부를 기록한다. 완료 항목만 이 tasks.md에서 표시하고 Agent B에게 현재 Commit SHA·재현 명령을 인계한다. [FR-009, SC-005]

## Dependencies & Execution Order

Setup T001–004 → Foundational T005–006 → US1 T007–010 → US2 T011–016 → US3 T017–020 → Polish T021–024.
US2·US3은 같은 함수와 테스트 파일을 사용하므로 개발은 US1 뒤 순차 진행하지만 각 사례의 결과는 독립 확인한다.
기존 구현으로 처음부터 통과하는 회귀 사례는 그렇게 기록한다. 테스트를 실패시키려고 정상 코드를 손상하지 않는다.

### Parallel Opportunities / Examples

- US1: T007–009는 같은 테스트·코드 계약에 의존하므로 순차. 파일 수정 없는 기준값 해석만 별도 검토 가능.
- US2: T011–015는 같은 파일을 수정하므로 순차. 오류 조건 검토는 읽기 전용으로 병행 가능.
- US3: T017–019는 같은 파일을 수정하므로 순차. Taylor 기준값 확인은 읽기 전용 병행 가능.
- 실제 구현 `[P]` 작업 없음. 단일 최소 모듈에서 가짜 병렬 기회를 만들지 않는다.

## Requirement Coverage

| 요구사항 | Tasks |
|----------|-------|
| FR-001 | T007,T009 |
| FR-002 | T007,T009 |
| FR-003 | T011,T012,T014 |
| FR-004 | T012,T013,T014,T015 |
| FR-005 | T017,T018,T019 |
| FR-006 | T017,T018,T019 |
| FR-007 | T008,T009,T013,T015,T021 |
| FR-008 | T007–T023 |
| FR-009 | T006,T008,T010,T013,T016,T018,T020–T024 |
| SC-001 | T007,T010,T017,T018,T020,T023 |
| SC-002 | T011–T016,T023 |
| SC-003 | T017–T020,T023 |
| SC-004 | T008,T010,T023 |
| SC-005 | T006,T016,T020–T024 |

## Implementation Strategy

US1이 계산 MVP이나 이번 완료 범위는 US1–US3 전체다. T001–024 완료 후 자체 테스트·diff 확인,
의도한 파일만 Stage → Conventional Commit → 기능 Branch Push → main 대상 PR 생성 →
별도 Agent B가 실제 PR HEAD SHA를 읽기 전용 독립 검증한다.
결함은 A 수정·새 Commit·Push 후 B가 새 HEAD 재검증한다. Merge는 절대 수행하지 않는다.
PR·B 검증은 이 구현 체크리스트 완료 이후의 인계 단계이며 테스트 실행과 혼동하지 않는다.
