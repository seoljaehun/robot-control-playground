> 상태 기록(2026-10-16): 이 문서의 기준 문서 작성 단계·placeholder·향후 생성·작업 금지 설명은 최초 작성 당시 범위를 기록한다. 이후 사용자가 Constitution 및 FK Spec·Plan 검토 완료를 전제로 Tasks부터 구현·Commit·Push·PR·독립 검증까지 승인했다. 현재 작업 범위는 FK이며 Merge는 금지한다. 원칙·요구사항은 유지한다.

# Robot Control Playground — 에이전트 작업 지침

## 1. 목적과 작업 전 확인

로봇 제어 학습과 Spec-Driven Development(SDD) 검증을 지원한다. 기본 응답과 문서는 한국어로 작성하며 파일명, Python 식별자, 수학 기호 및 표준 기술 용어는 영어를 사용할 수 있다.

작업 시작 시 다음 실제 파일을 읽는다. 없는 파일을 존재한다고 가정하지 않는다.

1. `PROJECT_PLAN.md`
2. 이 `AGENTS.md`
3. `.specify/memory/constitution.md`가 있으면 내용과 수립 상태
4. 현재 기능의 Spec Kit 산출물: `spec.md`, `plan.md`, `tasks.md` 및 관련 자료
5. 기존 관련 코드와 테스트

`PROJECT_PLAN.md`는 상위 요구사항, 이 문서는 작업 규칙, Constitution은 승인된 프로젝트 원칙, 기능 Spec은 기능 수용 조건을 정의한다. 문서 간 충돌을 임의의 우선순위로 해결하지 않는다. 충돌 위치·영향·대안을 보고하고 사용자 결정을 요청한다.

ChatGPT Project의 Planning, Theory, Experiment, Orchestrator 대화나 다른 Codex 대화의 내용을 완전히 공유한다고 가정하지 않는다. 참고한 결정과 확정된 저장소 문서를 구분한다. 설계 변경 승인 시 `PROJECT_PLAN.md`와 관련 Spec Kit 산출물을 갱신한다. 기존 상태 문서가 있다면 필요한 범위에서 함께 반영하되 별도의 중복 기준 문서를 관례적으로 만들지 않는다.

## 2. 작업 범위와 승인

- Phase 1 범위를 준수한다. 동역학·MuJoCo·학습 기반 제어 등으로 임의 확장하지 않는다.
- 핵심 알고리즘, 프로젝트 범위, 주요 인터페이스 및 수용 기준 변경은 근거·영향·대안을 먼저 제안하고 사용자 승인을 받는다.
- 승인된 범위 내 일반적인 구현·수정·자체 점검은 진행한다. 파괴적인 변경이나 범위 밖 작업은 수행하지 않는다.
- 사용자 파일·기존 테스트·설정을 임의로 삭제하거나 덮어쓰지 않는다.
- 중요한 작업은 목표, 입력, 수정 범위, 완료 조건 및 테스트 기준을 명시한다.
- 이론적 사실·해석·가설·실험 결과를 구분한다. 수식의 변수·좌표계·단위·가정·적용 조건과 실패 조건을 설명한다.
- 실행하지 않은 코드·테스트·실험을 실행 또는 통과했다고 보고하지 않는다.

## 3. 기존 Spec Kit 환경

2026-10-16 기준 `.specify/init-options.json`에는 Spec Kit 1.2.0, Codex 통합, PowerShell, sequential feature numbering이 기록되어 있다. 이는 설정 파일 확인 결과이며 설치 실행 검증 결과는 아니다.

다음 기존 경로를 재사용한다.

- `.agents/skills/speckit-*/SKILL.md`: Codex 명령의 실제 정의
- `.specify/integration.json`, `.specify/integrations/`: 통합 설정
- `.specify/templates/`: 문서 템플릿
- `.specify/scripts/powershell/`: PowerShell 지원 스크립트
- `.specify/workflows/speckit/workflow.yml`: review gate를 포함한 기본 SDD workflow

Spec Kit을 임의로 재설치·초기화·업데이트하지 않는다. 호출 전 설치된 명령의 지침과 부수 효과를 확인한다. 설정을 바꾸어 문제를 우회하지 않는다.

`.specify/memory/constitution.md`는 현재 placeholder 템플릿이다. 이를 승인된 원칙으로 간주하지 않는다. 다음 별도 작업에서 Constitution을 수립하고 사용자 검토를 받는다. 이번 기준 문서 작성 과정에서는 수정하지 않는다.

## 4. Spec Kit 필수 워크플로

권장 흐름은 다음과 같다. 아래 표기는 설치된 Codex용 skill 이름이며 다른 도구의 slash 명령 형식을 추정하여 사용하지 않는다.

| 단계 | Codex 호출 | 확인 사항 |
|---|---|---|
| Constitution | `$speckit-constitution` | 기존 원칙 확인 또는 수립·사용자 검토 |
| Specify | `$speckit-specify` | 상위 요구사항에서 기능 범위를 추출 |
| Clarify | `$speckit-clarify` | 필요 시 모호한 조건 해소 |
| Plan | `$speckit-plan` | 수식·단위·구조·인터페이스·수치 안정성 구체화 |
| Tasks | `$speckit-tasks` | 수용 조건에 연결된 구현·테스트 작업 |
| Analyze | `$speckit-analyze` | 필요 시 문서 일관성과 누락 분석 |
| Implement | `$speckit-implement` | 승인된 명세와 계획에 따른 구현 |
| 독립 검증 | Agent B | 동일 Commit에서 검증·수정·재검증 |

설치된 실제 지침과 사용자 승인 범위를 우선하며, 자동 생성 산출물을 무조건 정확하다고 가정하지 않는다. 기본 workflow의 Spec·Plan review gate를 존중한다. 사용자 검토가 필요한 상태에서 구현을 진행하지 않는다.

하나의 기능은 가능하면 하나의 PR로 검토 가능한 크기로 나눈다. 권장 단위는 FK, IK, Jacobian, Target Tracking and Visualization이다. 앞선 기능에 대한 의존성을 명세한다.

기능 산출물은 기본적으로 향후 `specs/<NNN-short-name>/` 아래에 생성한다. 실제 생성 경로는 설치된 명령과 명시적 설정을 확인한다. 디렉터리 이름과 Git 브랜치 이름이 반드시 동일하다고 가정하지 않는다. 명령 hook의 브랜치 생성 등 Git 부수 효과를 실행 전에 확인한다.

상위 요구사항을 기능 Spec에 추적 가능하게 반영한다. **프로젝트의 자동 테스트는 필수**다. `tasks-template.md`의 테스트 선택 안내는 일반 템플릿 설명이며, 이 프로젝트에서는 Spec에 테스트를 명시하고 Tasks에 포함한다. 템플릿 자체를 임의 수정할 필요는 없다.

## 5. Agent A — Implementation Agent

담당 업무:

- 승인된 Spec과 Plan에 따른 코드 구현 및 단위 테스트 작성
- 구현 자체 점검과 실제 테스트 실행
- 승인된 작업 범위의 Commit·Push 및 PR 작성
- Agent B가 재현한 오류 수정 및 변경 결과 보고

작업 규칙:

- 범위와 무관한 대규모 리팩터링을 하지 않는다.
- 기존 테스트를 임의 삭제하거나 실패를 숨기기 위해 수용 기준을 약화하지 않는다.
- 수학 공식 변경 시 근거를 제공하고 핵심 알고리즘 변경이면 사전 승인을 받는다.
- 테스트 실패는 원인과 영향·미해결 상태를 보고한다. 실행하지 못한 검증도 명시한다.
- 작업 결과에 수정 파일, 테스트 명령, 실제 실행 결과, 남은 문제 및 검증 대상 Commit SHA를 요약한다.

## 6. Agent B — Verification Agent

초기 역할은 **Read-only Reviewer**다. Agent A의 구현 파일을 기본적으로 수정하지 않는다. 필요한 독립 계산이나 검증 명령은 실행할 수 있으나 추적 파일을 변경하지 않고 재현 절차를 보고한다. 테스트 추가가 필요하면 A에게 제안하며, 직접 수정 역할로 전환하려면 사용자에게 범위 승인을 받는다.

검증 범위:

- 기능 Spec의 필수 요구사항 및 수용 조건 충족
- 수학 계산·좌표계·단위·가정의 일관성
- 특이점·경계·도달 불가능 목표·비정상 입력의 처리
- 수치 안정성, 속도 제한 및 종료 조건
- 자동 테스트 실제 실행 결과와 누락된 검증 조건
- 실험 설정·결과의 재현성과 PR 변경 범위

A가 작성한 테스트만을 근거로 PASS를 선언하지 않는다. 가능한 경우 독립적인 해석적 계산, FK 복원 검증, 수치 미분 등 별도 근거를 사용한다.

결함 보고에는 재현 조건, 예상 결과, 실제 결과 및 영향 범위를 포함한다. 검증 보고에는 다음 항목을 기록한다.

- 검증한 Commit SHA
- 확인한 Spec과 요구사항
- 실행한 테스트·검증 명령과 실제 결과
- 통과 항목, 실패 항목, 발견된 결함
- 해결 필요 사항 및 실행하지 못한 검증
- 최종 판정: `PASS`, `FAIL`, `BLOCKED`

`PASS`는 필수 검증이 충족된 기술적 판단이다. 확인된 결함이나 기준 미충족은 `FAIL`, 환경·자료·접근 문제로 필수 판단이 불가능하면 `BLOCKED`다. PASS는 사용자 Merge 승인을 대신하지 않는다.

## 7. 두 에이전트 협업

1. A와 B는 동일한 기준 문서와 검증 대상 Commit을 사용한다.
2. 가능하면 Git worktree 또는 별도 작업 디렉터리로 공간을 분리한다. 동일 파일을 동시에 수정하지 않는다.
3. A가 구현·자체 테스트·PR 작성을 완료한 후 B가 독립 검증한다.
4. B의 결함을 A가 수정하고, B가 새 Commit을 다시 검증한다.
5. 검증 중 PR HEAD가 바뀌면 이전 PASS를 그대로 적용하지 않는다. 변경된 HEAD를 대상으로 영향 범위와 필요한 검증을 다시 확인한다.
6. 필수 검증이 모두 통과한 후 사용자가 Merge를 결정한다.

자동 수렴 도구를 사용하더라도 B의 독립 검증과 사용자 승인 조건을 대체하지 않는다. 역할이나 작업 위치를 추측하지 말고 인계 시 명시한다.

## 8. Git/GitHub 운영

기준 브랜치는 `main`이다. 실제 저장소 상태와 원격 기본 브랜치가 다르면 임의 변경하지 않고 차이를 보고한다.

기능 브랜치 권장 예시:

- `feat/001-forward-kinematics`
- `feat/002-inverse-kinematics`
- `feat/003-jacobian`
- `feat/004-target-tracking`

이 이름은 예시다. 설치된 Spec Kit의 실제 브랜치 생성 방식·hook과 충돌하면 사용자 의도 및 지원되는 명시적 브랜치 설정을 확인한다. 기존 스크립트나 설정을 임의로 바꾸지 않는다.

Conventional Commits를 권장한다. 예: `feat: implement forward kinematics`, `test: add forward kinematics tests`, `fix: handle unreachable ik target`, `docs: update project requirements`.

표준 순서:

1. 작업 트리와 main의 최신 상태·원격 상태를 확인한다. 사용자 변경을 보존한다.
2. Feature Branch를 생성하거나 승인된 해당 브랜치를 사용한다.
3. Spec 기반으로 구현하고 테스트한다.
4. 변경 내용을 검토한 뒤 Commit·Push한다.
5. PR에 문제·변경 내용·검증 결과·미해결 사항을 기록한다.
6. B가 독립 검증하고, A의 수정 후 B가 재검증한다.
7. 사용자가 최종 변경과 검증 대상 HEAD를 확인하고 Merge를 승인한다.
8. 승인 후 Merge하고 main 상태와 작업 완료 여부를 확인한다.

main에 임의로 직접 Push하거나 사용자 승인 없이 Merge하지 않는다. 가능하면 main 보호와 CI pytest를 활용한다. 계정·저장소 정책상 어렵다면 수동 검증 절차와 실제 결과를 PR에 남긴다. CI나 보호 설정이 존재한다고 가정하지 않는다.

## 9. PR Merge 완료 조건

다음 조건을 모두 충족해야 한다.

- 기능 Spec 필수 요구사항 충족
- 관련 테스트 실제 통과
- 현재 PR HEAD에 대한 B의 필수 검증 완료 및 PASS
- 중요한 미해결 결함 없음
- 변경 내용과 테스트 결과가 PR에 기록됨
- 사용자 최종 Merge 승인 완료

Spec 변경이 필요하면 먼저 변경을 제안하고 승인을 받은 후 문서·코드·테스트를 일관되게 갱신한다.

## 10. 문서화 작업의 경계와 다음 작업

이번 기준 문서 작성 작업은 `PROJECT_PLAN.md`와 `AGENTS.md`만 대상으로 한다. Spec Kit 재설치·초기화·업데이트, Constitution 덮어쓰기, 기능 명세·계획·Tasks 선행 생성, Python 구현, 테스트 코드 생성·실행, Branch·Commit·Push·PR·Merge는 수행하지 않는다.

`PRD.md`, `ARCHITECTURE.md`, `TASKS.md`, `PROJECT_STATE.md`를 관례적으로 생성하지 않는다. 향후 실제 필요가 생기면 문서 역할과 중복 여부를 먼저 검토한다. 기준 문서의 경로·사실 확인은 코드 테스트 실행과 구분한다.

다음 권장 작업은 사용자 기준 문서 검토 → Constitution 수립·검토 → FK 기능 Specify → 필요 시 Clarify → Plan 검토 → Tasks → Implement → 독립 검증이다. 새 작업 시작 시 승인 범위와 실제 환경을 다시 확인한다.
