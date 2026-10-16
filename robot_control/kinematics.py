"""2R 평면 매니퓰레이터 기구학."""
import numpy as np


def forward_kinematics(
    theta1: float | int | np.integer | np.floating,
    theta2: float | int | np.integer | np.floating,
    l1: float | int | np.integer | np.floating,
    l2: float | int | np.integer | np.floating,
) -> tuple[float, float]:
    """Base (0,0), +x 오른쪽, +y 위쪽, CCW 양의 회전.

    theta1은 +x 기준, theta2는 Link 1 기준 상대각 [rad].
    l1/l2는 링크 길이 [m], 반환 (x,y)는 Base 좌표 [m].
    NaN/Infinity 및 0 이하 링크는 ValueError, 미지원 타입은 TypeError,
    float64 표현·계산 한계는 OverflowError. 극단값의 절대 정확도는 보장하지 않는다.
    """
    values = (theta1, theta2, l1, l2)
    names = ('theta1', 'theta2', 'l1', 'l2')
    for name, value in zip(names, values):
        if isinstance(value, (bool, np.bool_)) or not isinstance(
            value, (int, float, np.integer, np.floating)
        ):
            raise TypeError(f'{name} must be a scalar real number')
    for name, value in zip(names, values):
        if not isinstance(value, (int, np.integer)) and not np.isfinite(value):
            raise ValueError(f'{name} must be finite')

    converted = []
    with np.errstate(over='raise', invalid='raise', divide='raise', under='ignore'):
        for index, (name, value) in enumerate(zip(names, values)):
            try:
                number = np.float64(value)
            except (OverflowError, FloatingPointError) as exc:
                raise OverflowError(f'{name} cannot be represented as float64') from exc
            if not np.isfinite(number) or (index >= 2 and value > 0 and number == 0):
                raise OverflowError(f'{name} cannot be represented as float64')
            converted.append(number)
        for name, number in zip(names[2:], converted[2:]):
            if number <= 0:
                raise ValueError(f'{name} must be positive')
        t1, t2, a, b = converted
        try:
            c1, s1, c2, s2 = np.cos(t1), np.sin(t1), np.cos(t2), np.sin(t2)
            x = a*c1 + b*(c1*c2-s1*s2)
            y = a*s1 + b*(s1*c2+c1*s2)
            if not (np.isfinite(x) and np.isfinite(y)):
                raise OverflowError('FK calculation produced a nonfinite coordinate')
        except FloatingPointError as exc:
            raise OverflowError('FK calculation exceeded float64 representation') from exc
    return float(x), float(y)
