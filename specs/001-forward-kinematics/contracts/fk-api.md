# Python API Contract: Forward Kinematics

상태: Plan 검토 대상. 이 파일은 인터페이스 문서이며 Python 구현 파일이 아니다.

## 공개 함수

- 모듈: robot_control.kinematics
- 이름: forward_kinematics
- 필수 인자 순서: theta1, theta2, l1, l2. 위치 인자와 동일 이름의 keyword 인자 허용.
- 인자별 타입 표기: float | int | np.integer | np.floating.
- 반환 타입: tuple[float, float]. 순서는 (x, y).
- 기본 인자값·배열 broadcasting·그림 표시·파일 기록 없음.
- Python int·float, NumPy 정수·실수 스칼라만 수용하며 내부 계산은 float64다.
  bool·np.bool_·complex·문자열·None·컨테이너·0-D 포함 ndarray와
  기타 수치 객체(Decimal·Fraction 등)는 TypeError로 거부한다.

## 의미

Base 원점, 오른손 x/y 평면, 양의 반시계 회전을 사용한다.
theta1은 x축 기준, theta2는 Link 1 기준 상대 각도, 단위는 rad다.
l1·l2는 각각 유한한 양수 [m], 결과는 Base 기준 위치 [m]다.
각도를 정규화하거나 관절 제한을 부과하지 않는다.
공식과 실제 덧셈정리 평가는 [plan.md](../plan.md)의 수치 정책을 따른다.

## 실패 계약

| 조건 | 예외 | 메시지·결과 규칙 |
|------|------|----------------|
| 지원하지 않는 타입 | TypeError | 인자명과 scalar real 조건 식별 |
| 필수 인자 누락 | TypeError | Python 호출 규칙의 누락 인자 식별 |
| NaN·±Infinity | ValueError | 인자명과 finite 조건 식별 |
| 링크 <=0 (-0.0 포함) | ValueError | l1 또는 l2와 positive 조건 식별 |
| 유한값이 float64 변환 시 overflow 또는 양수 링크가 0으로 변환됨 | OverflowError | 인자명과 float64 표현 실패 식별 |
| 계산 중 overflow·invalid 또는 최종 비유한값 | OverflowError | FK 계산 단계의 표현 실패 식별 |

원본 유한값이더라도 계산 표현 실패를 ValueError로 오인하지 않는다.
오류는 정상 좌표 대신 예외로 전달하며 sentinel·NaN 좌표·부분 결과를 반환하지 않는다.
복수 오류 입력에서 타입 확인, 원본 유한성, 변환, 링크 양수, 계산 순서로 처리한다.
같은 단계는 theta1, theta2, l1, l2 순서로 확인한다. 오류 메시지 전체의 정확한 문자열은
공개 계약으로 고정하지 않으며 예외 종류·인자명·조건이 검증 대상이다.

## 성공·부수 효과 계약

- 완전 펼침·접힘과 같은 역문제 특이 자세도 정상 계산한다.
- 동일 환경·입력에서 좌표는 반복 실행 시 완전히 동일하다.
- 입력·전역 NumPy 오류 설정을 변경하지 않는다. 계산용 errstate는 종료 시 복원한다.
- matplotlib·시뮬레이션 없이 import·호출 가능하다.
- 정상 기준 사례의 성분별 절대 오차는 1e-9 m 이하.
  극단값의 정밀도·표현 한계는 plan의 별도 사례를 따른다.
- 예: (theta1,theta2,l1,l2)=(0,pi/2,1.0,0.8) → (1.0,0.8) m
  (부동소수점 결과는 허용 오차로 비교).

## 추적

FR-001–002: 인자·좌표 의미; FR-003–004: 오류 계약;
FR-005–006: 경계·주기; FR-007: 순수성; FR-008–009: plan의 테스트·기록 전략.
