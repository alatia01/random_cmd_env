# Tasks: 寄存器随机配置生成（JSON 选择 + 数组严格解析）

**Input**: Design documents from `/specs/001-register-random-generator/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: 本规格未要求 TDD 先行，测试任务以 quickstart/集成验证形式落地。

**Organization**: 任务按用户故事分组，确保每个故事可独立实现与验证。

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 同步计划变更并建立执行基线

- [X] T001 Sync latest clarification decisions into specs/001-register-random-generator/spec.md
- [X] T002 Sync array strictness decisions into specs/001-register-random-generator/plan.md
- [X] T003 [P] Sync error contract table into specs/001-register-random-generator/contracts/cmd-cfg-format.md
- [X] T004 [P] Sync array section uniqueness rule into specs/001-register-random-generator/data-model.md
- [X] T005 Sync validation scenarios for array overflow/duplicate sections into specs/001-register-random-generator/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 完成所有用户故事共享的解析与契约底座

**CRITICAL**: 本阶段完成前不进入用户故事实现

- [X] T006 Add array section index bounds check (`N < array_len`) in parse_cmd_cfg_to_vcpi.c
- [X] T007 Add duplicate array section detection (`MEMBER[N]` uniqueness) in parse_cmd_cfg_to_vcpi.c
- [X] T008 Add structured stderr error reporting for array overflow/duplicate section in parse_cmd_cfg_to_vcpi.c
- [X] T009 [P] Validate parser behavior for missing section/field default zero in parse_cmd_cfg_to_vcpi.c
- [X] T010 [P] Validate parser behavior for unknown field and duplicate field fail-fast in parse_cmd_cfg_to_vcpi.c
- [X] T011 Keep dual separator parsing (`:` and `=`) stable in parse_cmd_cfg_to_vcpi.c
- [X] T012 Keep by-value API wrapper and pointer-path unification in parse_cmd_cfg_to_vcpi.c

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 建立全寄存器可用清单 (Priority: P1) 🎯 MVP

**Goal**: 可完整枚举 `t_reg_vcpi` 的寄存器/位域/数组元信息

**Independent Test**: `--dump-registers` 输出完整且可对照 `reg_data.h`

- [X] T013 [US1] Ensure full `t_reg_vcpi` member extraction remains source-of-truth in random_reg_cfg.py
- [X] T014 [US1] Ensure array length metadata is exported for struct-array members in random_reg_cfg.py
- [X] T015 [P] [US1] Improve diagnostics for malformed struct/array declarations in random_reg_cfg.py
- [X] T016 [US1] Keep stable member ordering aligned with reg_data.h in random_reg_cfg.py

**Checkpoint**: User Story 1 fully functional and independently testable

---

## Phase 4: User Story 2 - 按 JSON 选择目标并随机生成 (Priority: P1)

**Goal**: 按 JSON 精细控制随机目标，数组成员严格校验

**Independent Test**: `indices` 缺失/越界立即失败；合法 `indices` 仅生成指定下标

- [X] T017 [US2] Enforce required `indices` for array members in random_reg_cfg.py
- [X] T018 [US2] Enforce `indices` type contract (int list or `"all"`) in random_reg_cfg.py
- [X] T019 [US2] Enforce `indices` range validation with fail-fast errors in random_reg_cfg.py
- [X] T020 [P] [US2] Implement `"indices":"all"` expansion to full index list in random_reg_cfg.py
- [X] T021 [US2] Ensure active target resolution emits sorted unique array targets in random_reg_cfg.py
- [X] T022 [P] [US2] Keep deterministic seed reproducibility for array targets in random_reg_cfg.py

**Checkpoint**: User Story 2 fully functional and independently testable

---

## Phase 5: User Story 3 - 导出可直接使用的 cmd.cfg (Priority: P2)

**Goal**: 稳定输出可消费 cfg，并保证 C 解析行为符合契约

**Independent Test**: cfg 输出格式稳定，C 读取与 debug 打印符合合同，且严格处理数组错误场景

- [X] T023 [US3] Emit array sections in `MEMBER[N]` format with ascending indices in random_reg_cfg.py
- [X] T024 [US3] Keep Python writer format as right-aligned `field : value` in random_reg_cfg.py
- [X] T025 [P] [US3] Keep C debug dump format as right-aligned `field = value` in parse_cmd_cfg_to_vcpi.c
- [X] T026 [US3] Validate C parser fail-fast on out-of-range array index sections in parse_cmd_cfg_to_vcpi.c
- [X] T027 [US3] Validate C parser fail-fast on duplicate array sections in parse_cmd_cfg_to_vcpi.c
- [X] T028 [P] [US3] Verify end-to-end value consistency (Python cfg -> C parse -> debug dump) in specs/001-register-random-generator/quickstart.md

**Checkpoint**: User Story 3 fully functional and independently testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 收尾、回归与文档一致性

- [X] T029 [P] Update decision log for strict array failure policy in specs/001-register-random-generator/research.md
- [X] T030 Run GCC strict compile verification (`-std=c99 -Wall -Wextra -Werror`) and record result in specs/001-register-random-generator/quickstart.md
- [X] T031 Run JSON selection regression scenarios and record result in specs/001-register-random-generator/quickstart.md
- [X] T032 Run array overflow/duplicate section negative scenarios and record result in specs/001-register-random-generator/quickstart.md
- [X] T033 [P] Verify contracts/spec/plan/task alignment across specs/001-register-random-generator/spec.md
- [X] T034 Finalize delivery notes and acceptance evidence in specs/001-register-random-generator/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies, start immediately
- Foundational (Phase 2): depends on Setup, blocks all user stories
- User Story phases (Phase 3-5): all depend on Foundational completion
- Polish (Phase 6): depends on all targeted user stories completion

### User Story Dependencies

- User Story 1 (P1): can start after Foundational
- User Story 2 (P1): can start after Foundational
- User Story 3 (P2): can start after Foundational; validates full producer-consumer contract

### Within Each User Story

- Contract enforcement before behavior expansion
- Parsing/selection before formatting/output
- Output formatting before end-to-end verification

### Parallel Opportunities

- Phase 1: T003 and T004 can run in parallel
- Phase 2: T009 and T010 can run in parallel after T006-T008
- US1: T015 can run in parallel with T014
- US2: T020 and T022 can run in parallel after T017-T019
- US3: T025 and T028 can run in parallel with T026/T027 once core output is stable
- Polish: T029 and T033 can run in parallel

---

## Parallel Example: User Story 2

```bash
Task: T020 [P] [US2] Implement "indices":"all" expansion in random_reg_cfg.py
Task: T022 [P] [US2] Keep deterministic seed reproducibility for array targets in random_reg_cfg.py
```

## Parallel Example: User Story 3

```bash
Task: T025 [P] [US3] Keep C debug dump format as right-aligned "field = value" in parse_cmd_cfg_to_vcpi.c
Task: T028 [P] [US3] Verify end-to-end value consistency in specs/001-register-random-generator/quickstart.md
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate catalog extraction against reg_data.h

### Incremental Delivery

1. Deliver US1 (catalog completeness)
2. Deliver US2 (JSON-driven strict selection)
3. Deliver US3 (cfg contract + C strict parsing)
4. Execute Phase 6 regression/polish and finalize evidence

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Then split by story:
   - Developer A: US1
   - Developer B: US2
   - Developer C: US3
3. Merge at Polish with integrated verification
