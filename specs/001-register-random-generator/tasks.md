# Tasks: 寄存器随机配置生成（JSON 选择更新）

**Input**: Design documents from `/specs/001-register-random-generator/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: 本次规格未显式要求 TDD，以下不强制生成测试先行任务。

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Status Update (2026-06-12)**:
- Phases 1-6: ✅ COMPLETED
- Phase 7 (Alignment Constraints Enhancement): ✅ COMPLETED
  - Added to address Verilog parsing bugs and alignment constraint extraction from vcpi.xlsx
  - All 15 tasks (T035-T049) completed and validated
  - Key achievements: 919 fields validated, 138 alignment constraints applied, 0 conflicts
- Phase 8 (minus1 Config Processing): ✅ COMPLETED
  - Added to handle fields using minus1 storage format (actual = config + 1)
  - Ensures alignment constraints apply to actual values, not config values
  - Key fields: ve_pic_height, ve_pic_width, ve_num_tile_columns_minus1, ve_num_tile_rows_minus1
  - All 10 tasks (T050-T059) completed

---

## Task Summary

| Phase | Purpose | Tasks | Status |
|-------|---------|-------|--------|
| 1. Setup | CLI 参数更新与输入契约对齐 | T001-T005 | ✅ 5/5 |
| 2. Foundational | 全寄存器解析、JSON 选择、约束基线 | T006-T015 | ✅ 10/10 |
| 3. User Story 1 | 建立全寄存器可用清单 (P1) | T016-T019 | ✅ 4/4 |
| 4. User Story 2 | JSON 选择随机生成 (P1) | T020-T025 | ✅ 6/6 |
| 5. User Story 3 | 导出 cmd.cfg (P2) | T026-T030 | ✅ 5/5 |
| 6. Polish | 文档、示例、验证 | T031-T034 | ✅ 4/4 |
| 7. Alignment | Verilog 解析、对齐约束、位宽验证 | T035-T049 | ✅ 15/15 |
| 8. minus1 Config | minus1 存储格式处理与对齐 | T050-T059 | ✅ 10/10 |
| **Total** | | **59** | **✅ 59/59** |

---

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

## Phase 7: Alignment Constraints Enhancement (2026-06-12)

**Purpose**: 修复 Verilog 数字解析，提取并应用对齐约束，验证位宽一致性

**Context**: vcpi.xlsx 包含字段级约束（列 J 范围、列 H 复位值、列 I 对齐规则），需要正确解析并应用于随机生成

### Setup & Extraction

- [X] T035 Create vcpi.xlsx full field extraction script in _extract_full_constraints.py
  - Extract columns A (register), E (field), G (bit-width), H (reset), I (description), J (constraint)
  - Output to _vcpi_full.json for analysis
  
- [X] T036 Implement Verilog number parser with base specifier support in _gen_constraints_with_alignment.py
  - Support `'d` (decimal), `'h` (hex), `'b` (binary), `'o` (octal)
  - Fix `16'd8190` → 8190 (not 0x8190=33168)
  - Fix `16'd127` → 127 (not 0x127=295)

- [X] T037 Implement bit-width parser for column G in _gen_constraints_with_alignment.py
  - Parse "a:b" format → width = a - b + 1
  - Parse single digit → width = 1
  - Return validated width for all 919 fields

### Alignment Constraint Extraction

- [X] T038 [P] Implement alignment pattern extractor for column I in _gen_constraints_with_alignment.py
  - Pattern: "Npixel align" or "NxN align"
  - Pattern: "HEVC：8pixel align" (support Chinese colon)
  - Pattern: "H.264/JPGE：16x16 align"
  - Output: `{'default': N}` or `{'hevc': N1, 'h264': N2, 'jpeg': N3}`

- [X] T039 [P] Implement constraint range validation against bit-width in _gen_constraints_with_alignment.py
  - Validate J-column ranges fit within `[0, 2^width - 1]`
  - Clamp if necessary (result: 0 fields needed clamping)
  - Report validation statistics

- [X] T040 Generate enhanced VCPI_FIELD_CONSTRAINTS dict in _vcpi_constraints_fixed.py
  - Include 'c' (constraint), 'r' (reset), 'd' (description), 'w' (width), 'a' (alignment)
  - 919 total fields, 138 with alignment, 505 with constraints, 0 conflicts

### Integration into random_reg_cfg.py

- [X] T041 Update VCPI_FIELD_CONSTRAINTS dict in random_reg_cfg.py (lines 42-962)
  - Replace with enhanced version from _vcpi_constraints_fixed.py
  - Add documentation for 'w' and 'a' fields
  - Preserve 922-line structure

- [X] T042 Enhance generate_field_value() to support alignment in random_reg_cfg.py (lines 1140-1195)
  - Extract alignment from constraint dict 'a' field
  - For multi-codec: use max(hevc, h264, jpeg) to satisfy all protocols
  - Call pick_aligned(rng, lo, hi, alignment) for range constraints
  - Apply alignment to reset-based randomization

### Validation & Testing

- [X] T043 [P] Create alignment verification script in _verify_alignment_detailed.py
  - Test VCPI_PIC_SIZE: verify 16-pixel alignment (max of 8, 16, 16)
  - Test VCPI_SRC_MOSAIC_POS_0: verify 4-pixel (x) and 2-pixel (y) alignment
  - Test with multiple seeds (1, 42, 123, 456, 789)

- [X] T044 [P] Verify constraint parsing fixes
  - VCPI_SRC_MOSAIC_POS: range [0, 8188] for st_x (was [0, 33160])
  - VCPI_SRC_MOSAIC_POS: range [0, 8190] for st_y (was [0, 33168])
  - VCPI_PIC_SIZE: reset value 127 (was 295)

- [X] T045 Run multi-seed alignment verification tests
  - Result: All seeds produce 16-aligned values for VCPI_PIC_SIZE
  - Result: All values within correct ranges [63, 8191]
  - Result: Deterministic reproducibility maintained

### Documentation Updates

- [X] T046 [P] Update plan.md technical context with constraint details
  - Document 919 fields, 138 with alignment, 505 with constraints
  - Document Verilog parsing, alignment strategy, bit-width validation
  - Add key implementation details section

- [X] T047 [P] Update research.md with alignment decisions
  - Decision 8: Verilog number format parsing strategy
  - Decision 9: Alignment constraint extraction and application
  - Decision 10: Bit-width validation and range clamping

- [X] T048 [P] Update data-model.md with FieldConstraint entity
  - Document constraint dict structure (c/r/d/w/a fields)
  - Provide examples: VCPI_PIC_SIZE, VCPI_SRC_MOSAIC_POS_0
  - Document validation rules for alignment values

- [X] T049 [P] Update quickstart.md validation scenarios
  - Update Scenario C: 16-pixel alignment (was 2-pixel)
  - Add Scenario D: Multi-seed alignment verification
  - Add validation record for 2026-06-12 fixes

**Checkpoint**: Alignment constraints fully integrated and validated

---

## Phase 8: minus1 Config Processing (2026-06-12)

**Purpose**: 处理使用 minus1 存储格式的字段，确保对齐约束应用于实际值而非配置值

**Context**: 部分寄存器字段使用 minus1 config 存储优化（实际值 = 配置值 + 1），对齐约束应用于实际使用的像素值

**Rationale**: 
- 硬件编码器对齐要求（HEVC 8x8 CTU、H.264/JPEG 16x16 宏块）针对实际像素尺寸
- minus1 只是存储优化，不应影响对齐语义
- 若对配置值对齐，则实际值 = 对齐值 + 1 会破坏对齐

### Constraint Extraction

- [X] T050 Implement minus1 pattern detector for column I in _gen_constraints_with_alignment.py
  - Pattern: "minus1 config" (case-insensitive)
  - Pattern: "minus 1" or "minus1" in description
  - Pattern: "plus 1 specifies" (indicates value+1 encoding)
  - Add "m": True field to constraint dict for matched fields

- [X] T051 Identify all minus1 fields in vcpi.xlsx
  - ve_pic_height (VCPI_PIC_SIZE)
  - ve_pic_width (VCPI_PIC_SIZE)
  - ve_num_tile_columns_minus1 (VE_TILE_INFO)
  - ve_num_tile_rows_minus1 (VE_TILE_INFO)
  - Record field count for validation

- [X] T052 [P] Update _vcpi_constraints_fixed.py with minus1 markers
  - Add "m": True for identified fields
  - Keep existing c/r/d/w/a fields intact
  - Validate minus1 + alignment combinations

### Integration into random_reg_cfg.py

- [X] T053 Update VCPI_FIELD_CONSTRAINTS dict in random_reg_cfg.py
  - Import updated dict from _vcpi_constraints_fixed.py
  - Add documentation for "m" field meaning
  - Verify field count matches extraction (4 minus1 fields)

- [X] T054 Enhance generate_field_value() to handle minus1 config in random_reg_cfg.py
  - Check for constraint_dict.get("m") == True
  - If minus1 + alignment: call pick_aligned(rng, min+1, max+1, align)
  - If minus1 + range (no align): generate in [min+1, max+1] then subtract 1
  - Return actual_value - 1 as config_value
  - Preserve existing logic for non-minus1 fields

- [X] T055 [P] Add minus1 config validation logic in random_reg_cfg.py
  - Verify generated config_value in [min, max]
  - Verify actual_value (config+1) satisfies alignment
  - Log warning if minus1 field lacks alignment constraint (unexpected)

### Validation & Testing

- [X] T056 Create minus1 verification script in verify_minus1_config.py
  - Read cmd.cfg and extract ve_pic_height/width config values
  - Calculate actual values: actual = config + 1
  - Verify actual % 16 == 0 (alignment on actual, not config)
  - Verify actual in [64, 8192] (config range [63, 8191])
  - Test with multiple seeds (1, 42, 123, 456, 789)

- [X] T057 [P] Verify minus1 fields produce correct output
  - Example: config=2879 → actual=2880 (2880 % 16 = 0 ✓)
  - Config value may NOT align: 2879 % 16 = 15 (expected)
  - Actual value MUST align: 2880 % 16 = 0 (required)
  - Range check: 64 <= 2880 <= 8192 ✓

### Documentation Updates

- [X] T058 [P] Update quickstart.md with minus1 validation scenario
  - Add Validation Scenario E: minus1 config correctness
  - Update Expected Output Snippet with minus1 example
  - Document that config values may not align but actual values must

- [X] T059 [P] Update contracts/random-require-rules.md business constraints
  - Replace old constraints (2-align, 1920x1080 limit)
  - Document minus1 config handling for VCPI_PIC_SIZE
  - Provide examples: config 2879 → actual 2880 (16-aligned)

**Checkpoint**: minus1 config processing integrated and validated

---

## Dependencies & Execution Order (Updated)

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, start immediately
- **Foundational (Phase 2)**: Depends on Setup, blocks all user stories
- **User Stories (Phase 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all targeted user stories completion
- **Alignment Enhancement (Phase 7)**: Depends on Phase 2 completion; enhances constraint accuracy
- **minus1 Config Processing (Phase 8)**: Depends on Phase 7 completion; builds on alignment constraint infrastructure

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
- **Alignment Enhancement**:
  - T038 and T039 can run in parallel after T037
  - T043 and T044 can run in parallel after T042
  - T046, T047, T048, T049 can all run in parallel (documentation updates)
- **minus1 Config Processing (Phase 8)**:
  - T052 can run in parallel with T051
  - T055 can run in parallel with T054 (validation can be developed alongside generation)
  - T056 and T057 can run in parallel after T054 (verification scripts)
  - T058 and T059 can run in parallel (documentation updates)

---

## Parallel Example: Alignment Enhancement (Phase 7)

```bash
# Extraction phase
Task: T038 [P] Implement alignment pattern extractor in _gen_constraints_with_alignment.py
Task: T039 [P] Implement constraint range validation in _gen_constraints_with_alignment.py

# Validation phase
Task: T043 [P] Create alignment verification script in _verify_alignment_detailed.py
Task: T044 [P] Verify constraint parsing fixes

# Documentation phase
Task: T046 [P] Update plan.md technical context
Task: T047 [P] Update research.md with alignment decisions
Task: T048 [P] Update data-model.md with FieldConstraint entity
Task: T049 [P] Update quickstart.md validation scenarios
```

---

## Parallel Example: minus1 Config Processing (Phase 8)

```bash
# Extraction phase
Task: T051 Identify all minus1 fields in vcpi.xlsx
Task: T052 [P] Update _vcpi_constraints_fixed.py with minus1 markers

# Validation phase
Task: T056 Create minus1 verification script in verify_minus1_config.py
Task: T057 [P] Verify minus1 fields produce correct output

# Documentation phase
Task: T058 [P] Update quickstart.md with minus1 validation scenario
Task: T059 [P] Update contracts/random-require-rules.md business constraints
```

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
5. **Deliver Phase 7 alignment constraints enhancement** (2026-06-12)
   - Fix Verilog number parsing bugs (decimal vs hex)
   - Extract and apply 138 alignment constraints from vcpi.xlsx
   - Validate all 919 fields for bit-width consistency
   - Update documentation with constraint details
6. **Deliver Phase 8 minus1 config processing** (2026-06-12)
   - Handle minus1 storage format (actual = config + 1)
   - Apply alignment to actual values, not config values
   - Validate 4 minus1 fields (ve_pic_height/width, tile_columns/rows_minus1)
   - Update validation scenarios and documentation

### Parallel Team Strategy

1. Dev A: parser/model tasks (T006-T010, T016-T019, T035-T037, T050-T052)
2. Dev B: JSON selection tasks (T008, T011-T012, T020-T025)
3. Dev C: output/docs tasks (T026-T034, T046-T049, T058-T059)
4. **Dev D: constraint enhancement tasks** (T038-T045, T053-T057) - can run in parallel with Phase 6

### Phase 7 Implementation Notes (2026-06-12)

**Impact**: Enhances constraint accuracy without breaking existing functionality
- **Backward compatible**: Existing JSON selection and seed reproducibility unchanged
- **Constraint source**: Static `VCPI_FIELD_CONSTRAINTS` dict (no runtime vcpi.xlsx dependency)
- **Key fixes**:
  - Verilog parsing: `16'd8190` now correctly → 8190 (was 33168)
  - MOSAIC ranges: [0, 8188] for st_x (was [0, 33160])
  - PIC_SIZE reset: 127 (was 295)
  - Alignment: 138 fields now enforce pixel alignment (2/4/8/16)

**Validation results**:
- ✓ All 919 fields validated, 0 bit-width conflicts
- ✓ Multi-seed testing: 100% alignment compliance
- ✓ Deterministic reproducibility maintained
- ✓ Range constraints within bit-width limits

### Phase 8 Implementation Notes (2026-06-12)

**Impact**: Correct handling of minus1 storage format to ensure alignment semantics apply to actual hardware values

**Rationale**:
- Hardware uses minus1 config as storage optimization: `actual_value = config_value + 1`
- Alignment constraints come from codec requirements (HEVC 8x8 CTU, H.264/JPEG 16x16 macroblock)
- Alignment must apply to actual pixel dimensions used by encoder, not stored config values
- Example: If config=2879, then actual=2880; 2880 must be 16-aligned (2880 % 16 = 0 ✓)

**Implementation strategy**:
1. **Extraction**: Detect "minus1 config" pattern in vcpi.xlsx column I descriptions
2. **Constraint dict**: Add `"m": True` field to mark minus1 fields
3. **Generation logic**: 
   - Generate aligned actual value: `V = pick_aligned(rng, min+1, max+1, alignment)`
   - Store config value: `config = V - 1`
   - Result: actual value (config+1) satisfies alignment, config value may not
4. **Validation**: Verify actual values align, config values in range

**Affected fields** (identified from vcpi.xlsx):
- `VCPI_PIC_SIZE.ve_pic_height`: 16-aligned actual, range [63, 8191] config → [64, 8192] actual
- `VCPI_PIC_SIZE.ve_pic_width`: 16-aligned actual, range [63, 8191] config → [64, 8192] actual
- `VE_TILE_INFO.ve_num_tile_columns_minus1`: tile count constraints
- `VE_TILE_INFO.ve_num_tile_rows_minus1`: tile count constraints

**Backward compatibility**:
- ✓ Existing seed reproducibility preserved (deterministic RNG)
- ✓ JSON selection logic unchanged
- ✓ Output format unchanged (cmd.cfg structure)
- ⚠️ Generated values for minus1 fields will change (correct alignment on actual values)

**Validation approach**:
- Read generated cmd.cfg values
- Calculate actual = config + 1
- Assert: `actual % alignment == 0`
- Assert: `min+1 <= actual <= max+1`
- Test with multiple seeds to ensure consistency
