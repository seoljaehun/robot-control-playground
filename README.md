# robot-control-playground

2-DOF 평면 로봇 기구학과 Spec-Driven Development 실습 프로젝트다.
현재 구현은 FK이며 IK·Jacobian·Target Tracking·시각화는 후속 범위다.

Python 3.11 환경에서 실행한다:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -c "import math; from robot_control.kinematics import forward_kinematics; print(forward_kinematics(0, math.pi/2, 1.0, 0.8))"
```

`python --version`이 3.11인지 먼저 확인한다. 검증 PC의 conda 환경은
`.\.venv\python.exe`를 사용한다. 자세한 명령은 [quickstart](specs/001-forward-kinematics/quickstart.md)에 있다.
기본 호출 예상 좌표는 `(1.0, 0.8)` m이다.

`robot_control.kinematics.forward_kinematics(theta1, theta2, l1, l2)`는 `(x, y)`를 반환한다.
각도는 rad, 길이·좌표는 m, Base는 원점이며 반시계 회전이 양수다.
theta2는 Link 1 기준 상대각이다. Python/NumPy 실수·정수 스칼라만 받는다.
타입 오류는 TypeError, NaN·Infinity·0 이하 링크는 ValueError,
float64 표현 실패는 OverflowError다. Matplotlib 없이 import·호출할 수 있다.
정상 기준 자세는 성분별 절대 오차 1e-9 m 이하로 검증한다.
큰 각도·극단 길이의 모든 실수 해에 동일 절대 정확도를 보장하지 않는다.

- [프로젝트 기준](PROJECT_PLAN.md), [작업 규칙](AGENTS.md), [Constitution](.specify/memory/constitution.md)
- [FK Spec](specs/001-forward-kinematics/spec.md), [Plan](specs/001-forward-kinematics/plan.md), [Tasks](specs/001-forward-kinematics/tasks.md)
- [API 계약](specs/001-forward-kinematics/contracts/fk-api.md), [실제 검증 기록](specs/001-forward-kinematics/verification.md)

루트 ARCHITECTURE.md·TASKS.md·PROJECT_STATE.md는 보존된 이전 미채택 초안이다.
현재 FK 기준은 위 승인 문서와 기능 산출물이며 Merge는 사용자 판단으로 남긴다.
