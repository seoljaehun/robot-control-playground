"""독립 기하학 기준값으로 FK 공개 계약을 검증한다."""
import math
import subprocess
import sys
import cmath
from decimal import Decimal
from fractions import Fraction

import numpy as np
import pytest

from robot_control.kinematics import forward_kinematics as fk


BASE_CASES = [
    ((0, 0, 1.0, 0.8), (1.8, 0)),
    ((math.pi / 2, 0, 1.0, 0.8), (0, 1.8)),
    ((0, math.pi / 2, 1.0, 0.8), (1, 0.8)),
    ((math.pi / 2, -math.pi / 2, 1.0, 0.8), (0.8, 1)),
    ((0, 0, 0.5, 1.5), (2, 0)),
    ((-math.pi / 2, 0, 1.0, 0.8), (0, -1.8)),
]


@pytest.mark.parametrize('args, expected', BASE_CASES)
def test_reference_positions_and_repeatability(args, expected):
    results = [fk(*args) for _ in range(3)]
    np.testing.assert_allclose(results[0], expected, atol=1e-9, rtol=0)
    assert results[0] == results[1] == results[2]
    assert type(results[0]) is tuple
    assert all(type(v) is float for v in results[0])


def test_relative_angle_and_keywords():
    result = fk(theta1=math.pi / 4, theta2=-math.pi / 2, l1=1, l2=0.8)
    np.testing.assert_allclose(result, (1.8 / math.sqrt(2), 0.2 / math.sqrt(2)),
                               atol=1e-9, rtol=0)


def test_import_and_call_without_visualization():
    script = ('import sys; from robot_control.kinematics import forward_kinematics; '
              'assert forward_kinematics(0,0,1,1)==(2.0,0.0); '
              'assert "matplotlib" not in sys.modules')
    subprocess.run([sys.executable, '-c', script], check=True, timeout=20)


NAMES = ('theta1', 'theta2', 'l1', 'l2')


@pytest.mark.parametrize('index', range(4))
@pytest.mark.parametrize('bad', [float('nan'), float('inf'), -float('inf')])
def test_reject_nonfinite(index, bad):
    args = [0, 0, 1, 0.8]
    args[index] = bad
    with pytest.raises(ValueError, match=NAMES[index] + '.*finite'):
        fk(*args)


@pytest.mark.parametrize('index', [2, 3])
@pytest.mark.parametrize('bad', [0, -0.0, -1])
def test_reject_nonpositive_links(index, bad):
    args = [0, 0, 1, 0.8]
    args[index] = bad
    with pytest.raises(ValueError, match=NAMES[index] + '.*positive'):
        fk(*args)


@pytest.mark.parametrize('index', range(4))
@pytest.mark.parametrize('bad', ['1', 1j, True, np.bool_(False), None, [1], (1,),
                                np.array(1), np.array([1]), Decimal('1'), Fraction(1)])
def test_reject_unsupported_types(index, bad):
    args = [0, 0, 1, 0.8]
    args[index] = bad
    with pytest.raises(TypeError, match=NAMES[index] + '.*scalar real'):
        fk(*args)


@pytest.mark.parametrize('scalar', [int, float, np.int8, np.int64, np.uint64,
                                   np.float16, np.float32, np.float64, np.longdouble])
def test_accept_supported_scalars(scalar):
    assert fk(scalar(0), scalar(0), scalar(1), scalar(1)) == (2, 0)


@pytest.mark.parametrize('count', range(4))
def test_missing_arguments(count):
    with pytest.raises(TypeError):
        fk(*([1]*count))


@pytest.mark.parametrize('args, error, pattern', [
    ((float('nan'), 'x', 1, 1), TypeError, 'theta2'),
    (('x', 'y', 1, 1), TypeError, 'theta1'),
    ((10**1000, float('nan'), 1, 1), ValueError, 'theta2.*finite'),
    ((float('inf'), float('nan'), 1, 1), ValueError, 'theta1.*finite'),
    ((10**1000, 0, 0, 1), OverflowError, 'theta1.*float64'),
    ((0, 0, -1, 0), ValueError, 'l1.*positive'),
])
def test_validation_stage_and_argument_order(args, error, pattern):
    with pytest.raises(error, match=pattern):
        fk(*args)


@pytest.mark.parametrize('index', range(4))
def test_integer_conversion_overflow(index):
    args = [0, 0, 1, 1]
    args[index] = 10**1000
    with pytest.raises(OverflowError, match=NAMES[index] + '.*float64'):
        fk(*args)


@pytest.mark.parametrize('length', [1e-300, 1e150])
def test_extreme_representable_lengths(length):
    result = fk(0, 0, length, length)
    assert result[0] == pytest.approx(2*length, rel=1e-14, abs=0)
    assert result[1] == 0


def test_position_overflow():
    maximum = np.finfo(np.float64).max
    with pytest.raises(OverflowError, match='FK.*calculation'):
        fk(0, 0, maximum, maximum)


def test_huge_angles_without_angle_sum_overflow():
    rotation = cmath.exp(1j*1e308)
    expected = rotation + 0.8*rotation*rotation
    np.testing.assert_allclose(fk(1e308, 1e308, 1, 0.8),
                               (expected.real, expected.imag), atol=1e-9, rtol=0)


def test_smallest_positive_link_is_accepted():
    tiny = float.fromhex('0x0.0000000000001p-1022')
    result = fk(0, 0, tiny, tiny)
    assert result == (2*tiny, 0)


@pytest.mark.parametrize('mode', ['overflow', 'underflow'])
def test_extended_float_conversion_limits(mode):
    extended = np.finfo(np.longdouble)
    normal = np.finfo(np.float64)
    if extended.maxexp == normal.maxexp and extended.minexp == normal.minexp:
        pytest.skip('platform longdouble has the same exponent range as float64')
    value = extended.max if mode == 'overflow' else extended.tiny
    with pytest.raises(OverflowError, match='l1.*float64'):
        fk(0, 0, value, 1)


@pytest.mark.parametrize('failure', [False, True])
def test_local_error_policy_and_restoration(failure):
    previous = np.seterr(all='raise' if not failure else 'ignore')
    caller = np.geterr().copy()
    try:
        if failure:
            with pytest.raises(OverflowError):
                fk(0, 0, np.finfo(float).max, np.finfo(float).max)
        else:
            tiny = float.fromhex('0x0.0000000000001p-1022')
            assert all(math.isfinite(v) for v in fk(0.3, 0.7, tiny, tiny))
        assert np.geterr() == caller
    finally:
        np.seterr(**previous)


@pytest.mark.parametrize('args, expected', [
    ((0, math.pi, 1, 0.8), (0.2, 0)),
    ((0, -math.pi, 1, 0.8), (0.2, 0)),
    ((0, math.pi, 1, 1), (0, 0)),
    ((0, math.pi, 0.8, 1), (-0.2, 0)),
    ((math.pi, 0, 1, 0.8), (-1.8, 0)),
    ((-math.pi, 0, 1, 0.8), (-1.8, 0)),
])
def test_folded_stretched_and_pi_boundaries(args, expected):
    np.testing.assert_allclose(fk(*args), expected, atol=1e-9, rtol=0)


@pytest.mark.parametrize('k1', range(-2, 3))
@pytest.mark.parametrize('k2', range(-2, 3))
def test_independent_joint_periodicity(k1, k2):
    result = fk(2*k1*math.pi, math.pi/2 + 2*k2*math.pi, 1, 0.8)
    np.testing.assert_allclose(result, (1, 0.8), atol=1e-9, rtol=0)


@pytest.mark.parametrize('side', [-1, 1])
@pytest.mark.parametrize('folded', [False, True])
def test_near_singular_postures_against_taylor(side, folded):
    delta = 1e-6
    cosine = 1-delta**2/2+delta**4/24
    sine = side*(delta-delta**3/6+delta**5/120)
    if folded:
        angle, expected = math.pi + side*delta, (1-0.8*cosine, -0.8*sine)
    else:
        angle, expected = side*delta, (1+0.8*cosine, 0.8*sine)
    np.testing.assert_allclose(fk(0, angle, 1, 0.8), expected, atol=1e-9, rtol=0)
