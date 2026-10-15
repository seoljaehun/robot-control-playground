# PROJECT_STATE.md — Robot Control Playground

**Specification revision:** 1.0.0 (2026-10-15)  
**Decision authority:** Project owner  
**Status:** Proposed consolidated baseline — owner requested recommended reconciliation; repository sync and PR approval not verified  
**Source of truth:** Approved repository versions of `PRD.md`, `PROJECT_STATE.md`, `ARCHITECTURE.md`, `TASKS.md`, and `AGENTS.md`. In case of conflict, stop and ask the owner; this document does not silently override existing approved files.

## 1. Mission and scope

Phase 1 is a lightweight, reproducible Python implementation of a 2-DOF planar revolute–revolute (RR) manipulator to learn forward/inverse kinematics, position Jacobian, **fixed-damping DLS target tracking**, automatic numerical verification, and experiment visualization. Development is staged to support Codex implementation with explicit acceptance tests.

**Included:** FK, analytical IK, Jacobian, DLS iteration, reachable/unreachable target evaluation, error plots, Python/NumPy/Matplotlib/pytest, documented experiments.  
**Excluded:** dynamics, gravity/inertia, torque control, collision avoidance, hard joint constraints, hardware control, MuJoCo, vision control, PyTorch training, RL, adaptive damping, and algorithm-comparison claims. All are deferred to later phases.

## 2. Decision register

| ID | Decision | Status | Basis |
|---|---|---|---|
| DEC-001 | Phase 1 scope above; 2R planar arm | CONFIRMED | Planning / Theory / Experiment handoffs |
| DEC-002 | Stage 4 baseline algorithm = fixed-damping DLS | CONFIRMED | Planning handoff |
| DEC-003 | Stages 0–6, in order: bootstrap, FK, IK, Jacobian, DLS, evaluation, reproducibility | ADOPTED FOR REVIEW | Planning proposal; this revision reconciles stages |
| DEC-004 | Base origin (0,0), x right/y up, CCW-positive, angles rad, lengths m; q2 relative | ADOPTED FOR REVIEW | Theory handoff |
| DEC-005 | Iterative **position-increment** DLS (no physical `dt` in Stage 4) | ADOPTED FOR REVIEW | Reconciliation of Planning vs Theory |
| DEC-006 | `damping=0.1 m/rad`, dimensionless `gain=0.2`, `position_tolerance=1e-3 m`, `max_iterations=500` | ADOPTED FOR REVIEW | Theory-first consistent baseline; unvalidated empirically |
| DEC-007 | Central-difference `h=1e-5 rad`, Jacobian test `atol=1e-8 m/rad`, `rtol=1e-7`; FK `atol=1e-10 m`, IK round-trip `atol=1e-9 m` | ADOPTED FOR REVIEW | Experiment test proposal; scale-limited to reference lengths |
| DEC-008 | `float64`, finite-only `(2,)` arrays, `L_i>0`, no batch API; Python >=3.10 | ADOPTED FOR REVIEW | Simplicity/compatibility proposal |
| DEC-009 | IK: always return normalized `[-pi,pi)` branches in defined order, structured status for unreachable/infinite families | ADOPTED FOR REVIEW | Explicit policy to resolve OPEN questions |
| DEC-010 | DLS trajectory preserves **unwrapped** angles; no joint limits or speed limits; explicit statuses | ADOPTED FOR REVIEW | Consistent kinematic iteration |
| DEC-011 | Experiment configuration/results as JSON and histories as CSV; artifacts not committed by default | ADOPTED FOR REVIEW | Lightweight reproducibility |
| DEC-012 | First Codex task: TASK-001 bootstrap; implementation requires owner approval and repository comparison | PENDING APPROVAL | Project governance |

`CONFIRMED` means explicitly affirmed in the supplied three handoffs; `ADOPTED FOR REVIEW` means the orchestrator's coherent recommendation, **not evidence of prior approval**. The user's request authorizes document drafting, not an assertion of PR merger or completed implementation.

## 3. Reconciled cross-dialogue differences

| Concern | Conflicting proposals | Single recommended rule |
|---|---|---|
| DLS gain | Planning 1.0 / Theory 0.2 | 0.2 |
| DLS stop error | Planning & Theory 1e-3 / Experiment 1e-4 m | 1e-3 m; 1e-4 stays a stretch/diagnostic only |
| DLS budget | Planning 10 s at dt=.01 / Theory 500 steps / Experiment 300 steps | 500 iterations; no simulated physical time |
| Time discretization | Planning forward Euler dt=.01 / Theory iteration | Pure position-increment discrete iteration, no dt |
| Jacobian finite difference | Theory 1e-6 / Experiment 1e-5 rad | 1e-5 rad |
| Default lengths | Planning (1,1) m / Theory positive generic | Reference experiments (1,1) m; functions accept any finite positive pair |

Damping is `0.1 m/rad` under the radian-aware convention in `ARCHITECTURE.md`. Numerical values are defaults **to be validated**, not measurements or guarantees of convergence.

## 4. Workstream responsibilities

- **Planning:** PRD priorities, Stage scope, module and implementation dependencies.
- **Theory:** formulas, coordinate conventions, degeneracy behavior, DLS dimension checks.
- **Experiment:** test vectors, success/failure metrics, reproducible configuration and analysis; no invented results.
- **Orchestrator:** check agreement with GitHub versions, maintain this register, prepare bounded Codex tasks after owner approval.

## 5. Approval and execution gates

1. Compare these three proposed files against the **real** GitHub `PRD.md` and `AGENTS.md`, plus existing versions of the three documents. Repository content has not been checked here.
2. Owner reviews/approves the reconciled defaults and contracts in `ARCHITECTURE.md`; unresolved conflicts take precedence over this proposal.
3. Mark a task `READY_FOR_CODEX` only after its spec and dependent contracts are approved and prerequisites are satisfied.
4. Codex works in a branch/PR, with pytest logs and precise file changes, and does not merge without owner permission.
5. Report actual results only: not-yet-run tests are `NOT_RUN`; not-yet-pushed files are `LOCAL_DRAFT`.

## 6. Current execution status (as of 2026-10-15)

- Three dialogue handoffs: **received and reconciled as proposed documents**.
- Files in this output: **generated locally**; GitHub upload/PR: **NOT DONE**.
- Existing GitHub `PRD.md` and `AGENTS.md`: **NOT INSPECTED IN THIS SESSION**.
- Implementation/tests/experiments: **NOT RUN / NOT VERIFIED**.
- Owner sign-off on consolidated implementation specification: **PENDING**.
- Next concrete action: review file differences with repository, approve `DEC-003`–`DEC-011`, then explicitly authorize `TASK-001`.
