# ARCHITECTURE.md — Phase 1 Implementation Contract

**Revision:** 1.0.0 — proposed final reconciliation, 2026-10-15  
**Approval:** PENDING owner/repository review. The contracts below constitute a coherent **recommended** baseline, not already-implemented code.

## 1. Constraints and dependencies

- Python **>=3.10** on Windows 10, CPU-only; `numpy`, `matplotlib`, `pytest`, standard library. Pin exact versions in dependency/lock files during Stage 0; do not claim an untested version matrix.
- No mandatory GPU, PyTorch, MuJoCo, robotics middleware, dynamics, or physical timing.
- Pure computational functions separate from persistence and plotting; deterministic default experiments, no random sampling necessary.
- Phase 1 is a kinematic teaching/simulation system, **not** a hardware controller.

## 2. Proposed package layout

```text
README.md
pyproject.toml
PRD.md
PROJECT_STATE.md
ARCHITECTURE.md
TASKS.md
AGENTS.md
src/robot_control_playground/
    __init__.py
    kinematics.py        # FK, IK, reachability
    jacobian.py          # position Jacobian
    control.py           # one DLS step and iterative tracker
    models.py            # result records and status enum
    evaluation.py        # metrics; no plotting
    visualization.py     # figures only
experiments/
    reference.json
    run_reference.py
    outputs/             # gitignored generated output
tests/                  # top-level, not nested in package
    test_kinematics.py
    test_jacobian.py
    test_control.py
    test_evaluation.py
```

Correct the indentation of `tests/` to repository root when materializing. No packages beyond `src/` are required. Repository paths are recommendations pending an existing-tree check.

## 3. Global conventions and input validation

- Base `{B}`: origin at first joint `(0,0)`; +x right, +y up, right-handed +z out of the plane. CCW positive.
- `q=(theta1,theta2)` in **rad**: theta1 absolute first-link direction; theta2 second link's relative rotation.
- `lengths=(L1,L2)` in **m**, finite and strictly positive; target `(x,y)` in **m**.
- All public array inputs: `np.asarray(..., dtype=np.float64)` with **exact shape `(2,)`**, all finite. Any wrong shape, NaN/Inf, nonpositive length, invalid control hyperparameter: `ValueError`. Never silently broadcast, reshape, or treat batch inputs as valid.
- Array outputs are freshly produced `np.ndarray` float64; angles are in rad, FK target and errors in m. Results must never silently include NaN/Inf.
- Standard IK returned joint angles normalized to `[-pi, pi)` by `wrap(theta) = (theta+pi) % (2*pi)-pi`; iterative control stores **unwrapped** `q` for trajectory continuity.
- Angles are dimensionless under SI calculus but labeled `rad` explicitly; Jacobian columns have engineering units `m/rad`, DLS damping has matching units `m/rad`, and `gain` is dimensionless in the selected incremental formulation.

## 4. Robot model and forward kinematics

Assume rigid links, ideal joints, zero base offset; no joint limits, collisions, gravity, or actuator effects.

```python
forward_kinematics(q: ArrayLike, link_lengths: ArrayLike) -> np.ndarray  # (2,), m
```

For `q=(q1,q2)`:

\[
x=L_1\cos q_1+L_2\cos(q_1+q_2),\qquad
y=L_1\sin q_1+L_2\sin(q_1+q_2).
\]

Reference: with `(L1,L2)=(1,1)` m, `q=(0,0)` -> `(2,0)` m, `q=(pi/2,0)` -> `(0,2)` m, `q=(0,pi)` -> `(0,0)` m up to floating-point tolerance.

## 5. Analytical inverse kinematics

```python
class IKStatus(str, Enum):
    REACHABLE = 'reachable'       # 1 or 2 distinct configurations
    UNREACHABLE = 'unreachable'   # no configurations
    INFINITE = 'infinite'         # infinite family at equal-length origin

@dataclass(frozen=True)
class IKResult:
    status: IKStatus
    solutions: tuple[np.ndarray, ...]  # each (2,), normalized radians

inverse_kinematics(target: ArrayLike, link_lengths: ArrayLike) -> IKResult
```

With `r²=x²+y²`, `c2=(r²-L1²-L2²)/(2 L1 L2)`, and `s2=±sqrt(max(0,1-c2²))`:

\[
q_2=\operatorname{atan2}(s_2,c_2),\qquad
q_1=\operatorname{atan2}(y,x)-\operatorname{atan2}(L_2s_2,L_1+L_2c_2).
\]

- Geometric reachability: `abs(L1-L2) <= r <= L1+L2`. Numeric test in terms of `c2`, `eps_c2=1e-12` (dimensionless) for `(1,1)` m reference scale; values within this tolerance of `[-1,1]` may be clipped; beyond it report `UNREACHABLE`. Explicitly test scaling sensitivity before treating the tolerance as universal.
- General cases: return first the branch with `sin(q2)>0` (positive elbow branch), then `sin(q2)<0`. Branch labels refer to this sign, not a possibly ambiguous world-frame 'up/down'.
- At fully extended/folded workspace boundaries the branches coincide: return **one** distinct solution after modulo-`2pi` deduplication. For `L1 != L2`, inner boundary target at origin cannot occur; when `L1=L2` and `target=(0,0)` within `r_tol=1e-12 m` at reference scale, the robot has infinitely many solutions: return `INFINITE` and an **empty tuple**; do not fabricate a canonical solution.
- Unreachable: return `UNREACHABLE`, empty tuple; invalid numerical input: raise `ValueError`.
- Every returned solution must pass FK round-trip verification in a reference test. Consider large/small link scale handling an explicitly documented limitation of the fixed reference thresholds.

## 6. Position Jacobian

```python
position_jacobian(q: ArrayLike, link_lengths: ArrayLike) -> np.ndarray  # (2, 2), m/rad
```

\[
J(q)=\begin{bmatrix}
-L_1\sin q_1-L_2\sin(q_1+q_2) & -L_2\sin(q_1+q_2)\\
L_1\cos q_1+L_2\cos(q_1+q_2) & L_2\cos(q_1+q_2)
\end{bmatrix},\qquad \dot p=J\dot q.
\]

`det(J)=L1*L2*sin(q2)`; geometric singularities occur at `q2=k*pi` (nonzero positive link lengths). Verify with central differences:

`J_fd[:,i] = (FK(q+h*ei)-FK(q-h*ei))/(2*h)`, `h=1e-5 rad`.

For reference `(1,1)` m lengths, compare with `np.allclose(J,J_fd,atol=1e-8,rtol=1e-7)`; tolerances need re-evaluation for substantially different length scales.

## 7. Fixed-damping DLS controller — one discrete iteration

```python
class TrackingStatus(str, Enum):
    CONVERGED = 'converged'
    MAX_ITERATIONS = 'max_iterations'
    STAGNATED = 'stagnated'
    NUMERICAL_FAILURE = 'numerical_failure'

@dataclass(frozen=True)
class TrackingResult:
    status: TrackingStatus
    final_q: np.ndarray               # (2,), rad, unwrapped
    final_position: np.ndarray        # (2,), m
    final_error_norm: float           # m
    iterations: int                   # executed DLS updates
    q_history: np.ndarray             # (iterations+1, 2), rad
    error_norm_history: np.ndarray    # (iterations+1,), m
    delta_q_norm_history: np.ndarray  # (iterations,), rad

track_target(initial_q: ArrayLike, target: ArrayLike,
             link_lengths: ArrayLike, *, damping: float = 0.1,
             gain: float = 0.2, position_tolerance: float = 1e-3,
             max_iterations: int = 500) -> TrackingResult
```

Inputs must be finite; `damping>0`, `0<gain<=1`, `position_tolerance>0`, `max_iterations` positive integer (reject bool). No physical `dt`, `qdot`, or simulated seconds are defined in this API.

At iteration `k`:

\[
e_k=p^*-FK(q_k),\quad A_k=J_kJ_k^{\mathsf T}+\lambda^2I_2,\quad
\Delta q_k=J_k^{\mathsf T}\operatorname{solve}(A_k,e_k),\quad
q_{k+1}=q_k+K\Delta q_k.
\]

Here `e` has units m, `J` m/rad, `lambda` m/rad, `delta_q` rad, `K` dimensionless. Do not form `inv(A)`. With `lambda>0`, `A` is positive definite in exact arithmetic; finite-precision failures remain possible.

- Record initial state at index 0. Check convergence **before** updating and after each update, using Euclidean task-space error `||target - FK(q)||_2 <= 1e-3 m`.
- Return `CONVERGED` if the error condition is met, else `MAX_ITERATIONS` after 500 updates.
- To detect exact mathematical stagnation without an arbitrary new hidden threshold: if a non-converged update computes `q_next == q` elementwise in float64, return `STAGNATED`. This covers singular-start zero-update behavior; other small-progress cases naturally reach `MAX_ITERATIONS` and can be studied from history. `NUMERICAL_FAILURE` on nonfinite intermediates or `np.linalg.LinAlgError` with last finite state and recorded history.
- Unreachable target: do not project to workspace or assert convergence. Run the same stopping rule, and report the resulting non-convergence status. `reachability` may be calculated separately as a diagnostic, not as a fabricated IK solution.
- No joint/speed limits or angle wrapping inside iteration; report these limitations in plots and analysis. Wall-clock runtime (if measured) is a performance diagnostic, not a convergence criterion.
- No adaptive lambda, pseudoinverse switch, momentum, or extra controller without separate approval.

## 8. Evaluation, experiment files and visualization

Default **reference scenario** (proposed): `L=(1,1)` m, `initial_q=(0.3,0.5)` rad, `target=(1.0,1.0)` m. These inputs are for reproducible software regression, not a claim of optimality; add a singular start `(0,0)` and unreachable `(3,0)` m as separate cases.

- Config: `experiments/reference.json`: `schema_version`, `scenario_id`, `link_lengths_m`, `initial_q_rad`, `target_m`, `damping_m_per_rad`, `gain`, `position_tolerance_m`, `max_iterations`.
- Per-run metadata/results: `experiments/outputs/<scenario_id>/result.json`: same inputs, algorithm/spec version, Python/NumPy versions, timestamp (metadata only), status, iterations, final joint vector, final position/error, initial reachability and output file names.
- History: `history.csv` with `iteration,q1_rad,q2_rad,error_norm_m,delta_q_norm_rad` (initial row has an empty/NA delta). Fixed deterministic column order and no rounding before storage.
- Images: `arm.png` and `error.png`, with labeled axes, units, and termination status. Generated outputs ignored by Git.
- Primary metrics: final error `||p*-FK(q_final)||_2` (m), convergence status, iteration count, per-step applied joint change `||q_{k+1}-q_k||_2` (rad). For `delta_q_norm_history`, store the **applied** change `K*delta_q`, not the unscaled internal solution.
- Wall-clock runtime can be reported separately with environment details, not interpreted as simulated time. No seeded randomness required unless future stochastic tests are added.

## 9. Verification contract (reference scale)

| Component | Required checks | Suggested pass rule |
|---|---|---|
| FK | exact/reference poses, angle periodicity, invalid inputs | absolute position error <= `1e-10 m` |
| IK | two branches, boundary, unreachable, infinite family at equal-length origin, round-trip | FK reconstruction <= `1e-9 m` for returned solutions |
| Jacobian | shapes, analytic reference, finite differences, det at singularities | `h=1e-5 rad`, `atol=1e-8`, `rtol=1e-7` |
| DLS algebra | compare `solve` to independent analytic/reference case; finite results | `np.allclose` relative numeric tests with documented expected values |
| DLS tracking | reachable target, singular zero-update, unreachable target, histories and status | reachable reference case `CONVERGED` at <= `1e-3 m` within 500 steps; no blanket guarantee |
| Reproducibility | same config runs twice; file-schema validation | matching deterministic status, metrics and state histories up to declared tolerance |

Original Experiment handoff mentioned FK-01..16, IK-01..11, J-01..07, DLS-01..12 but did **not** supply the individual case definitions. Do **not** claim those 46 test cases are implemented or specified; expand only when source cases are provided or approved.

## 10. Decision changes and conflict procedure

Any change to coordinate conventions, IK status policy, DLS update equation, parameters, endpoint error definition, or APIs requires owner approval and synchronization with `PRD.md`, `PROJECT_STATE.md`, `TASKS.md`, and `AGENTS.md` as relevant. If the actual repository differs, stop and provide a diff/conflict report; do not override existing files silently.
