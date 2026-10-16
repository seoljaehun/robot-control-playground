# Quickstart Validation Guide: Forward Kinematics

승인된 FK를 실제 구현·검증한 후 현행화한 실행 안내다.
실제 테스트 결과·환경·실패 이력은 [verification.md](verification.md)를 따른다.
모든 명령은 프로젝트 루트에서 PowerShell로 실행한다.

## 사전 조건

Plan 승인 → Tasks 작성 → 승인 범위의 구현 완료가 필요하다.
Git 원격 main과 로컬 이력을 확인·연결하고 기능 Branch 및 대상 Commit을 확정한다.
기존 사용자 파일을 보존하고 main에 임의 Commit·Push하지 않는다.
Python 3.11과 최소 소스·requirements.txt·테스트를 사용한다.

검증 PC는 py launcher 없이 Anaconda를 사용해 아래 명령으로 새 Python 3.11 환경을 구성했다.
표준 venv는 `.venv/Scripts/python.exe`, conda 환경은 `.venv/python.exe`를 사용한다.

```powershell
& C:/Anaconda3/Scripts/conda.exe create --prefix C:/SJH/robot-control-playground/.venv python=3.11 pip -y
.\.venv\python.exe -m pip install -r requirements.txt
.\.venv\python.exe -m pytest -q -rs
.\.venv\python.exe -c "import math; from robot_control.kinematics import forward_kinematics; print(forward_kinematics(0, math.pi/2, 1.0, 0.8))"
```

기존 환경을 덮어쓰지 않는다. Python 3.11이 이미 설치되어 있으면 다음 표준 venv 절차를 사용한다.

## 환경 준비 (구현 후)

```powershell
Set-Location -LiteralPath 'C:\SJH\robot-control-playground'
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip freeze
```

requirements.txt의 NumPy·pytest를 Python 3.11 호환 환경에 설치하고 실제 버전을 기록한다.
가상 환경 활성화 없이 명시적 실행 경로를 사용하여 PowerShell 실행 정책 변경을 피한다.
이미 승인된 실행 환경이 있으면 그것을 사용하며 재설치를 강제하지 않는다.

## 수용 검증 (구현 후)

환경을 활성화한 경우 기본 명령은 `python -m pytest`다.
위 가상 환경을 직접 지정하는 동등 명령은 다음과 같다.

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pytest tests/test_forward_kinematics.py -v
```

첫 명령으로 전체 테스트를 수행한다. 둘째 명령은 FK만 진단할 필요가 있을 때 사용한다.
예상되는 통과 조건은 [plan.md](plan.md)의 T1–T10이다.
정확한 테스트 개수·통과 출력은 구현 전 예측 결과로 작성하지 않는다.
실패가 있으면 예상값·실제값·재현 명령을 남기고 종료 코드를 숨기지 않는다.

별도 수동 호출로 그림 없이 기본 자세를 확인할 수 있다.

```powershell
.\.venv\Scripts\python.exe -c "import math; from robot_control.kinematics import forward_kinematics; print(forward_kinematics(0.0, math.pi/2, 1.0, 0.8))"
```

예상 위치는 (1.0,0.8) m이며 성분별 절대 오차 1e-9 m 이하다.
인자·실패 예시는 [contracts/fk-api.md](contracts/fk-api.md),
입력 값 모델은 [data-model.md](data-model.md)를 참조한다.

## 기록과 독립 검증

구현 후 대상 SHA가 존재할 때 다음 읽기 전용 명령으로 확인한다.

```powershell
git rev-parse HEAD
git status --short --branch
```

현재 대상 SHA는 PR HEAD와 대조한다. B 최종 판정은 PR 본문에 기록한다.
verification.md에 담당자(A/B), SHA, OS·Python·의존성 버전, 명령·종료 코드,
각 요구사항/시나리오의 실제 결과·실패·skip 사유·미실행 항목을 기록한다.
NumPy 확장 실수 범위 차이에 따른 선택적 skip은 필수 float64 검증의 대체가 아니다.
A 테스트와 별도로 B가 동일 Commit의 기하학적 기준값·근접 자세 근거를 확인한다.
B 판정은 PASS/FAIL/BLOCKED이며 사용자 Merge 승인을 대신하지 않는다.

로컬 `.specify/feature.json`은 기존 ignore 정책대로 추적하지 않는다. 깨끗한 clone에서
후속 Spec Kit 명령을 실행할 때는 PowerShell 세션에 기능 경로를 명시한다.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/001-forward-kinematics'
```
