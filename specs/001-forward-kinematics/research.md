# Research: Forward Kinematics

작성일: 2026-10-16. 범위는 설계 결정 조사이며 구현·테스트·설치 실험은 수행하지 않았다.
입력은 승인된 [spec.md](spec.md), 프로젝트 기준 문서 및 Constitution이다.
설치된 Plan 스킬의 지침에 따라 읽기 전용 연구 에이전트가 수치 정책을 독립 검토했다.

## R1. 최소 구성

- **Decision**: 루트 robot_control 패키지, kinematics 모듈, 공개 FK 함수 하나,
  단일 테스트 파일과 NumPy·pytest를 사용한다. 저장소·네트워크·GUI 계층은 없다.
- **Rationale**: 한 자세 계산을 독립적으로 시험하며 후속 기구학에서 import할 수 있다.
- **Alternatives considered**: src 레이아웃·패키징 도구는 현재 규모에서 불필요하다.
  표준 math만 사용하는 대안도 가능하지만 프로젝트의 NumPy 수치 처리와 일관성을 택한다.

## R2. 스칼라 계약과 예외

- **Decision**: Python int·float 및 NumPy 정수·실수 스칼라만 수용한다.
  bool·np.bool_는 먼저 거부하고 모든 ndarray는 0-D까지 거부한다.
  타입 오류는 TypeError, 비유한 입력·0 이하 링크는 ValueError,
  유한값의 float64 변환·계산 표현 실패는 OverflowError다.
- **Rationale**: 잘못된 입력과 유효하지만 계산할 수 없는 입력의 원인을 분리한다.
  입력값 전체를 float로 무조건 변환하면 문자열·bool이 잘못 수용될 수 있다.
- **Alternatives considered**: 배열 일괄 계산·자동 문자열 변환·사용자 정의 예외 클래스는
  Spec에 필요하지 않다. Decimal·Fraction 등 다른 수치 타입도 현재 계약에서 제외한다.
- **Sources**: [NumPy scalar 계층](https://numpy.org/doc/stable/reference/arrays.scalars.html),
  [유한성 판정](https://numpy.org/doc/stable/reference/generated/numpy.isfinite.html).

## R3. 각도 합과 정규화

- **Decision**: 각도를 정규화하지 않고 각 관절의 sin/cos와 덧셈정리로 평가한다.
  이론적 FK는 theta1+theta2를 사용하지만 실제 평가는 그 합을 직접 만들지 않는다.
- **Rationale**: 유한한 큰 각도의 합 overflow를 피한다. 나머지 연산으로 강제 정규화하면
  큰 각도의 인자 축소 정확도를 오히려 잃을 수 있고 불필요한 ±pi 경계 정책이 생긴다.
  이는 공식 API 권장 알고리즘이 아닌 수학적 동치와 표현 한계에 근거한 설계 판단이다.
- **Alternatives considered**: 직접 각도 합은 단순하지만 큰 값에서 불필요한 overflow가 있다.
  각도 크기 제한은 승인 Spec에 없으므로 도입하지 않는다.
- **Sources**: [NumPy sin의 rad 규칙](https://numpy.org/doc/stable/reference/generated/numpy.sin.html),
  [Python 부동소수점 표현 한계](https://docs.python.org/3/tutorial/floatingpoint.html).

## R4. 오류 환경

- **Decision**: 계산 블록을 np.errstate(over=raise, invalid=raise, divide=raise,
  under=ignore)로 제한하고 최종 유한성을 확인한다. 계산의 FloatingPointError를
  API의 OverflowError로 변환한다. 출력의 작은 값이 underflow로 0이 되는 것은 허용한다.
- **Rationale**: 호출자 설정이 바뀌어도 일관된 실패를 제공하고 설정이 외부로 누출되지 않는다.
  양수 링크 자체가 float64 변환 시 0이 되는 경우는 입력 표현 실패로 별도 처리한다.
- **Alternatives considered**: 전역 seterr는 다른 코드에 영향을 주므로 사용하지 않는다.
  모든 underflow를 실패 처리하는 것은 유효한 작은 입력을 과도하게 거부한다.
- **Source**: [NumPy errstate의 raise 및 설정 복원](https://numpy.org/doc/stable/reference/generated/numpy.errstate.html).

## R5. 독립 기준값과 정확도

- **Decision**: 정상 사례는 성분별 atol=1e-9 m, rtol=0.
  축 방향의 길이 합·차, pi/4의 sqrt(2) 기하학 및 근접 자세의 Taylor 다항식을
  생산 함수와 별도로 준비한다. 일반 자세의 추가 근거는 표준 cmath의 복소 회전이다.
- **Rationale**: 동일 FK 구현을 테스트 기준으로 복제하지 않으며 기본 상대 오차가
  승인된 절대 오차를 완화하지 않게 한다. 비교 대상의 단위와 수치 조건을 분리한다.
- **Alternatives considered**: 생산 함수를 다시 호출한 기준값은 독립성이 없다.
  모든 finite 입력에 동일 절대 오차를 보장하는 것은 binary64 표현 한계상 부적절하다.
- **Sources**: [assert_allclose의 atol·rtol](https://numpy.org/doc/stable/reference/generated/numpy.testing.assert_allclose.html),
  [Python 부동소수점 한계](https://docs.python.org/3/tutorial/floatingpoint.html).

## 조사 결론

설계 선택은 위와 같이 해소했다. 의존성의 실제 설치 버전·환경 호환성과 수치 결과는
구현 시 검증·기록한다. 모든 수치 허용량과 극단값 사례는 [plan.md](plan.md)에 정의한다.
상위 Spec·Constitution의 내용과 수용 기준을 변경하지 않는다.
