> 상태: 이전 미채택 초안(보존). 2026-10-16 사용자 승인에 따라 현재 FK 개발 기준은 PROJECT_PLAN.md, AGENTS.md, .specify/memory/constitution.md 및 specs/001-forward-kinematics/의 승인된 spec.md·plan.md·tasks.md이다. 아래 기존 내용은 역사적 초안이며 현재 구현 지시가 아니다.

# TASKS.md — Phase 1 Work Orders and Acceptance Gates

**Revision:** 1.0.0 proposed reconciliation (2026-10-15)  
**State:** DOCUMENT_DRAFT; no task has been implemented or tested in this session.

## 1. Task governance

Status vocabulary: `PROPOSED`, `BLOCKED`, `READY_FOR_CODEX`, `IN_PROGRESS`, `PR_OPEN`, `VERIFIED`, `DONE`. A task is `READY_FOR_CODEX` only if **(a)** owner explicitly approves its technical contract, **(b)** GitHub repository structure/docs are checked, **(c)** prerequisites satisfied, and **(d)** acceptance tests are specified. Codex must not merge PRs without user approval; `DONE` requires merged/approved state verified, not a guessed outcome.

All tasks below are **PROPOSED / BLOCKED pending owner approval and repository comparison**, regardless of the order in this list.

## 2. Dependency map

`TASK-001 bootstrap -> TASK-002 FK -> TASK-003 IK`  
`TASK-002 FK -> TASK-004 Jacobian`  
`TASK-002 + TASK-004 -> TASK-005 DLS`  
`TASK-003 + TASK-005 -> TASK-006 evaluation/visualization -> TASK-007 reproducibility/docs`

Stage 2 IK and Stage 3 Jacobian are mathematically independent after FK. The staged learning order remains IK before Jacobian. DLS does not require IK at runtime.

## 3. Candidate Codex jobs

### TASK-001 — Stage 0: Project bootstrap

- **Goal:** Create importable, minimal CPU-only Python project and pytest scaffold.
- **Inputs:** owner-approved repository tree and Python baseline; `ARCHITECTURE.md` package suggestion.
- **Scope/files:** `pyproject.toml`, `src/robot_control_playground/__init__.py`, `tests/test_smoke.py`, `.gitignore`, basic `README.md`. Do not overwrite existing configs silently.
- **Acceptance:** documented clean install, `python -m pytest -q` passes a real import smoke test, Windows instructions work in target environment; dependencies limited to NumPy/Matplotlib/pytest (plus packaging tools).
- **Reports:** exact environment, command output, changed file list, PR diff.
- **Status:** BLOCKED (owner approval + repository verification).

### TASK-002 — Stage 1: Forward kinematics

- **Goal:** Implement deterministic 2R FK and shared finite shape validation.
- **Input:** `(q, link_lengths)` shape `(2,)`, float64, rad/meters.
- **Scope/files:** `src/robot_control_playground/kinematics.py`, `tests/test_kinematics.py`.
- **Acceptance:** `(0,0)->(2,0)`, `(pi/2,0)->(0,2)` for unit links; periodicity and invalid inputs; `atol=1e-10 m` reference scale. No IK or plotting in this PR.
- **Status:** BLOCKED (TASK-001, approved FK contract).

### TASK-003 — Stage 2: Analytical IK

- **Goal:** Implement both finite-solution branches with status-aware exceptional cases.
- **Input:** target `(2,)` m and positive lengths `(2,)` m.
- **Scope/files:** `kinematics.py`, `models.py`, `tests/test_kinematics.py`.
- **Acceptance:** branch order by sign of `sin(theta2)`; normalized angles; round-trip `atol=1e-9 m`; one boundary solution; unreachable empty result; equal-length origin `INFINITE` empty result; invalid input raises `ValueError`.
- **Status:** BLOCKED (TASK-002, approved IK contract).

### TASK-004 — Stage 3: Position Jacobian

- **Goal:** Implement analytic 2x2 Jacobian independent of IK.
- **Scope/files:** `jacobian.py`, `tests/test_jacobian.py`.
- **Acceptance:** central finite differences `h=1e-5 rad`, `atol=1e-8 m/rad`, `rtol=1e-7`; `det(J)=L1*L2*sin(q2)` reference cases; invalid-input tests.
- **Status:** BLOCKED (TASK-002, approved Jacobian contract).

### TASK-005 — Stage 4: Fixed DLS tracker

- **Goal:** One deterministic kinematic iterative position-increment DLS controller.
- **Inputs:** `(initial_q,target,link_lengths)`, `damping=0.1 m/rad`, `gain=0.2`, `position_tolerance=1e-3 m`, `max_iterations=500`.
- **Scope/files:** `control.py`, `models.py`, `tests/test_control.py`.
- **Acceptance:** update uses `J.T @ np.linalg.solve(J @ J.T + damping**2 * I, error)` and `q += gain * delta_q`; no `dt`; convergence check, robust histories, finite error metrics; singular zero-update labeled `STAGNATED`; unreachable target never falsely reported converged; exhaustive status tests; deterministic reruns.
- **Status:** BLOCKED (TASK-002 + TASK-004, approved DLS & termination contract).

### TASK-006 — Stage 5: Evaluation and visualization

- **Goal:** Compute auditable metrics and create two plots without changing controller behavior.
- **Scope/files:** `evaluation.py`, `visualization.py`, `tests/test_evaluation.py`, experiment driver.
- **Acceptance:** recompute final position error independently, report status, iterations, applied joint increment norms; labeled arm and error plots; plotting works headless with Agg backend in tests; do not confuse iterations with physical/simulated time.
- **Status:** BLOCKED (TASK-003 + TASK-005).

### TASK-007 — Stage 6: Reproducibility and docs

- **Goal:** Supply reproducible reference scenarios and machine-readable records.
- **Scope/files:** `experiments/reference.json`, `experiments/run_reference.py`, JSON/CSV serializers and tests, `README.md`, applicable docs.
- **Acceptance:** deterministic reruns; valid `result.json`, `history.csv`, `arm.png`, `error.png` schemas and columns; configurations/versions recorded; generated artifacts ignored by Git; README contains exact commands and limitations; verification log attached.
- **Status:** BLOCKED (TASK-006).

## 4. Explicit pre-implementation review

1. Compare repository `PRD.md` and `AGENTS.md` to proposed scope, naming, and implementation rules.
2. Owner approves or revises numeric and API policy in `ARCHITECTURE.md`, especially IK degeneracies, position-increment iteration, fixed `0.1/0.2`, `1e-3 m`, `500`, and float64 validation.
3. Confirm supported Python / dependency pinning on the actual developer environment.
4. Only then mark **one** bounded job `READY_FOR_CODEX`, beginning with TASK-001; send it with objective, input, file scope, tests, done criteria, and prohibition on unrelated edits.

## 5. Testing and reporting rules for every PR

- Report test command **and actual log**; if not executed, write `NOT_RUN` with reason.
- Separate observations from conjectures; do not create fabricated numerical experiment claims.
- Preserve deterministic parameters and attach failure scenario when a test fails.
- Update `PROJECT_STATE.md` when an approved architectural decision or verified task state changes; update other specs only with approval.
- Require user permission for a meaningful algorithm change and for PR merge.

## 6. Immediate next action

**Owner:** Review/approve this consolidated contract after comparing it to current GitHub documents.  
**Orchestrator:** Prepare TASK-001 Codex prompt once the approval and repository check are recorded.  
**Codex:** No implementation is authorized by this draft alone.
