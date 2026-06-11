# Tasks: 寄存器随机配置生成（JSON 选择更新）

**Input**: Design documents from `/specs/001-register-random-generator/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: 本次规格未显式要求 TDD，以下不强制生成测试先行任务。

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 对齐输入契约变更并准备单脚本运行入口

- [X] T001 Update CLI argument spec to use `--select-json` in random_reg_cfg.py
- [X] T002 Remove runtime dependency on random_require.md in random_reg_cfg.py
- [X] T003 [P] Add default JSON selection file path handling in random_reg_cfg.py
- [X] T004 [P] Define JSON selection error code constants in random_reg_cfg.py
- [X] T005 Create sample selection file in register_selection.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 完成所有用户故事共享能力（全寄存器解析、JSON 选择解析、约束与输出基线）

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement full `t_reg_vcpi` member parsing in random_reg_cfg.py
- [X] T007 Normalize scalar typedef members with empty bitfield lists in random_reg_cfg.py
- [X] T008 [P] Implement JSON loader and schema validation for `registers[]` in random_reg_cfg.py
- [X] T009 Implement register existence validation against parsed catalog in random_reg_cfg.py
- [X] T010 Implement last-write-wins merge for duplicated register entries in random_reg_cfg.py
- [X] T011 Implement active register filtering (`enabled=true`) in random_reg_cfg.py
- [X] T012 Implement empty active set handling (`E_SELECTION_EMPTY_ACTIVE_SET`) in random_reg_cfg.py
- [X] T013 Keep VCPI_PIC_SIZE constraints (2-align, width<=1920, height<=1080) in random_reg_cfg.py
- [X] T014 Implement deterministic seed pipeline for reproducible generation in random_reg_cfg.py
- [X] T015 Preserve stable output ordering by source order in random_reg_cfg.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 建立全寄存器可用清单 (Priority: P1)

**Goal**: 可完整枚举 `t_reg_vcpi` 下全部寄存器与位域

**Independent Test**: 执行 `--dump-registers` 后可看到完整寄存器目录，且无关输入文件不会影响解析结果

- [X] T016 [US1] Refine register catalog extraction API for full coverage in random_reg_cfg.py
- [X] T017 [US1] Ensure `--dump-registers` output includes scalar-only registers in random_reg_cfg.py
- [X] T018 [US1] Improve malformed header diagnostics for missing `t_reg_vcpi` in random_reg_cfg.py
- [X] T019 [US1] Add summary output for parsed register/field counts in random_reg_cfg.py

**Checkpoint**: User Story 1 should be independently functional

---

## Phase 4: User Story 2 - 按 JSON 选择目标并随机生成 (Priority: P1)

**Goal**: 只对 JSON 启用寄存器随机赋值并保证错误可诊断

**Independent Test**: 使用混合启用/禁用 JSON 运行，输出仅包含启用寄存器；非法 JSON 或未知寄存器时报错退出

- [X] T020 [US2] Implement selection parser entrypoint for register_selection.json in random_reg_cfg.py
- [X] T021 [US2] Apply active register filter before generation loop in random_reg_cfg.py
- [X] T022 [US2] Implement target-not-found validation (`E_SELECTION_TARGET_NOT_FOUND`) in random_reg_cfg.py
- [X] T023 [US2] Implement schema-invalid validation (`E_SELECTION_SCHEMA_INVALID`) in random_reg_cfg.py
- [X] T024 [P] [US2] Extend runtime metadata to include selected register list in random_reg_cfg.py
- [X] T025 [US2] Update user-facing JSON validation errors in random_reg_cfg.py

**Checkpoint**: User Story 2 should be independently functional

---

## Phase 5: User Story 3 - 导出可直接使用的 cmd.cfg (Priority: P2)

**Goal**: 在 JSON 选择模式下稳定输出可消费 cfg

**Independent Test**: 运行后 cmd.cfg 分组头、键值格式、顺序稳定且仅含启用寄存器

- [X] T026 [US3] Keep cfg section header contract in random_reg_cfg.py
- [X] T027 [US3] Keep aligned `field : value` renderer in random_reg_cfg.py
- [X] T028 [US3] Ensure writer skips disabled registers in random_reg_cfg.py
- [X] T029 [US3] Keep atomic file write behavior for cmd.cfg in random_reg_cfg.py
- [X] T030 [US3] Update end-to-end flow to `parse header -> parse JSON -> generate -> emit` in random_reg_cfg.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 文档、示例、收尾验证与一致性同步

- [X] T031 [P] Update quickstart commands to JSON mode in specs/001-register-random-generator/quickstart.md
- [X] T032 [P] Update selection error examples in specs/001-register-random-generator/contracts/random-require-rules.md
- [X] T033 Add validated sample in register_selection.json
- [X] T034 Run quickstart scenarios and record results in specs/001-register-random-generator/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, start immediately
- **Foundational (Phase 2)**: Depends on Setup, blocks all user stories
- **User Stories (Phase 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all targeted user stories completion

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2; independent of US2/US3
- **User Story 2 (P1)**: Starts after Phase 2; independently testable with selection JSON
- **User Story 3 (P2)**: Starts after Phase 2; validates output contract under JSON mode

### Within Each User Story

- Parser/selection validation before generation wiring
- Generation logic before output formatting checks
- Story checkpoint before moving to lower priority story

### Parallel Opportunities

- Setup: T003 and T004 can run in parallel after T002
- Foundational: T008 can run parallel with T007; T014 can run parallel with T015
- US2: T024 can run in parallel with T022/T023 after T021
- Polish: T031 and T032 can run in parallel

---

## Parallel Example: User Story 1

```bash
Task: T017 [US1] Ensure --dump-registers output includes scalar-only registers in random_reg_cfg.py
Task: T019 [US1] Add summary output for parsed register/field counts in random_reg_cfg.py
```

## Parallel Example: User Story 2

```bash
Task: T022 [US2] Implement target-not-found validation in random_reg_cfg.py
Task: T023 [US2] Implement schema-invalid validation in random_reg_cfg.py
```

## Parallel Example: User Story 3

```bash
Task: T026 [US3] Keep cfg section header contract in random_reg_cfg.py
Task: T027 [US3] Keep aligned field renderer in random_reg_cfg.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate full `t_reg_vcpi` catalog extraction independently

### Incremental Delivery

1. Deliver US1 full catalog parsing
2. Deliver US2 JSON-based register selection randomization
3. Deliver US3 stable cmd.cfg output under JSON mode
4. Finish Phase 6 polish and validation record

### Parallel Team Strategy

1. Dev A: parser/model tasks (T006-T010, T016-T019)
2. Dev B: JSON selection tasks (T008, T011-T012, T020-T025)
3. Dev C: output/docs tasks (T026-T034)
