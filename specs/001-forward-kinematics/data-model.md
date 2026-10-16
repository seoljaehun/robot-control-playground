# Data Model: Forward Kinematics

## 값 모델

아래는 개념적 값 모델이며 dataclass·상태 객체를 구현하라는 요구가 아니다.
모든 값은 함수 호출 동안만 사용하고 영구 저장하지 않는다.

| 개체 | 필드 | 단위·의미 | 검증 |
|------|------|-----------|------|
| Joint Configuration | theta1, theta2 | rad; 기준 x축 각도와 Link 1 상대 각도 | 스칼라 실수·유한값 |
| Link Geometry | l1, l2 | m; 순서 있는 강체 링크 길이 | 스칼라 실수·유한값·각각 >0 |
| End-Effector Position | x, y | m; Base 기준 끝점 위치 | float 두 개·각각 유한값 |
| Validation Failure | 예외 클래스·메시지 | 입력 또는 계산 실패 원인 | 계약의 오류 분류 준수 |

관절 상태와 링크 길이 한 쌍의 조합이 끝점 위치 하나를 결정한다.
목표점·속도·시간·관절 제한·역해 분기·저장 ID는 없다.

## 입력 표현과 변환

- Python int·float, NumPy 정수·실수 scalar를 허용한다.
- bool·np.bool_, complex, 문자열, None, list·tuple 및 ndarray(0-D 포함)는 거부한다.
  Decimal·Fraction 등 다른 수치 객체는 자동 변환하지 않는다.
- 원본 유한성을 확인하고 float64로 변환한다. 매우 큰 정수는 값 자체는 유한하지만
  변환 실패할 수 있으므로 OverflowError로 구분한다.
- 확장 정밀도 NumPy 값은 원본의 유한성과 변환 이후 유한성·양수 보존을 따로 확인한다.
- 링크 0·-0.0·음수 및 네 입력의 NaN·±Infinity는 ValueError.
- 변환·계산 중 표현 한계는 OverflowError. tiny 출력 underflow는 허용한다.
- 반환은 Python tuple[float, float]이며 배열·원본 참조를 반환하지 않는다.

## 처리 흐름

타입 검증 → 원본 유한성 → float64 변환·변환 한계 → 링크 양수 검증 →
해석적 FK → 결과 유한성 검증 → (x,y).
어느 단계든 실패하면 예외로 종료하고 좌표·부분 결과를 반환하지 않는다.
이것은 호출별 처리 순서이며 지속 상태 전이는 없다.

수학·오차·테스트 기준은 [plan.md](plan.md),
공개 인자 순서·예외 정책은 [contracts/fk-api.md](contracts/fk-api.md)를 따른다.
