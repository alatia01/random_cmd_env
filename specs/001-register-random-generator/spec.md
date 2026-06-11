# Feature Specification: 寄存器随机配置生成（更新）

**Feature Branch**: `001-register-random-generator`

**Created**: 2026-06-11

**Status**: Draft

**Input**: User description: "更新 001：支持 t_reg_vcpi 全寄存器随机；通过 JSON 指定寄存器是否参与随机；脚本通过解析该 JSON 完成指定寄存器随机；random_require.md 仅用于制定开发规则，不作为脚本运行输入。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 建立全寄存器可用清单 (Priority: P1)

作为工具使用者，我希望系统能从 reg_data.h 中完整提取 `t_reg_vcpi` 下定义的全部寄存器及位域信息，形成可查询清单，这样我可以确认随机目标覆盖完整且可信。

**Why this priority**: 若寄存器定义提取不正确，后续随机规则与配置输出都失去基础。

**Independent Test**: 提供包含 `t_reg_vcpi` 定义的 reg_data.h，执行解析后应得到可枚举的寄存器列表与对应位域信息，并可人工对照头文件验证。

**Acceptance Scenarios**:

1. **Given** 提供有效的 reg_data.h，**When** 执行寄存器解析，**Then** 系统返回 `t_reg_vcpi` 下全部寄存器名、位宽信息与位域名的结构化清单。
2. **Given** 某寄存器仅有整寄存器定义无位域，**When** 执行寄存器解析，**Then** 系统仍将其纳入清单并标记为无显式位域。

---

### User Story 2 - 按 JSON 选择目标并随机生成 (Priority: P1)

作为验证工程师，我希望系统能读取 JSON 选择文件，根据其中对寄存器参与随机的配置，仅对被启用的寄存器执行随机赋值，以便精确控制测试输入范围。

**Why this priority**: JSON 驱动的目标选择是本次更新核心，直接决定工具是否满足可控随机需求。

**Independent Test**: 提供启用/禁用混合的 JSON 选择文件，执行后应仅出现被启用寄存器的随机结果，禁用寄存器不参与输出。

**Acceptance Scenarios**:

1. **Given** JSON 文件将部分寄存器标记为启用，**When** 执行随机生成，**Then** 仅这些寄存器被随机赋值并进入结果。
2. **Given** JSON 文件将某寄存器标记为禁用，**When** 执行随机生成，**Then** 该寄存器不参与随机且不写入输出结果。

---

### User Story 3 - 导出可直接使用的 cmd.cfg (Priority: P2)

作为下游工具链使用者，我希望生成结果以固定格式写入 cmd.cfg，便于直接消费，不需要二次转换。

**Why this priority**: 该能力是交付闭环，优先级略低于解析与随机策略本身。

**Independent Test**: 执行生成后，检查 cmd.cfg 的分组头和键值行格式，确认可直接读取。

**Acceptance Scenarios**:

1. **Given** 已完成寄存器解析与 JSON 选择后的随机赋值，**When** 生成 cmd.cfg，**Then** 输出文件包含按寄存器分组的键:值条目。
2. **Given** 同一次运行存在多个寄存器结果，**When** 写入 cmd.cfg，**Then** 文件内分组顺序稳定且每个字段仅出现一次。

### Edge Cases

- JSON 文件中包含 `t_reg_vcpi` 不存在的寄存器名时，系统应报告明确错误并指出目标名称。
- JSON 文件缺失、格式非法或关键字段缺失时，系统应快速失败并给出可诊断信息。
- JSON 文件将全部寄存器标记为禁用时，系统应给出明确提示并按约定输出空结果或失败。
- reg_data.h 缺失或不可读时，系统应快速失败并输出可诊断信息。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统 MUST 读取并解析 reg_data.h 中 `t_reg_vcpi` 下定义的全部寄存器与位域信息。
- **FR-002**: 系统 MUST 提取每个寄存器及其位域的名称与可用于计算取值边界的位宽信息。
- **FR-003**: 系统 MUST 读取 JSON 选择文件并识别每个寄存器是否参与随机。
- **FR-004**: 系统 MUST 仅对 JSON 标记为参与随机的寄存器执行随机赋值。
- **FR-005**: 系统 MUST 在随机赋值前校验 JSON 与寄存器定义的一致性（目标存在性、字段完整性、格式合法性）。
- **FR-006**: 系统 MUST 为被选中寄存器的每个位域生成不超过位宽上限的随机值。
- **FR-007**: 系统 MUST 支持由用户提供随机种子以保证结果可复现。
- **FR-008**: 系统 MUST 将最终结果写入 cmd.cfg，格式为按寄存器分组的键:值文本。
- **FR-009**: 系统 MUST 在 cmd.cfg 中使用稳定且可预测的输出顺序。
- **FR-010**: 系统 MUST 对无效 JSON、不存在寄存器目标和输入文件缺失提供可定位错误信息。
- **FR-011**: 系统 MUST 在一次运行中完成解析、筛选、随机与导出流程，不依赖人工干预。
- **FR-012**: 系统 MUST 不将 random_require.md 作为脚本运行时输入，不解析该文件。

## Constitution Alignment *(mandatory)*

- **CA-001 Source of Truth**: 本特性以 reg_data.h 中 `t_reg_vcpi` 及关联结构体为寄存器定义唯一来源，不维护独立位域镜像。
- **CA-002 Runtime Constraints**: 交付物严格遵循宪法中定义的运行时与依赖约束。
- **CA-003 Delivery Shape**: 交付形态为单一脚本文件。
- **CA-004 Function Design**: 功能边界划分为头文件解析、JSON 选择解析、随机生成、输出写入与错误报告等单一职责函数。
- **CA-005 Verifiability**: 支持显式随机种子与结构化中间结果校验，保证可复现实验。
- **CA-006 Maintainability**: 对位域边界计算、规则优先级与异常分支提供完整注释说明。

### Key Entities *(include if feature involves data)*

- **RegisterDefinition**: 单个寄存器定义，包含寄存器名、寄存器位宽、位域列表。
- **BitFieldDefinition**: 位域定义，包含位域名、位宽、所在寄存器、可选默认值信息。
- **RegisterSelection**: 来自 JSON 文件的寄存器选择项，包含寄存器名与是否参与随机标记。
- **GenerationResult**: 单次生成结果，包含寄存器分组、位域名和值、运行元数据（如种子与校验状态）。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 对提供的 reg_data.h，`t_reg_vcpi` 下寄存器与位域识别完整率达到 100%（以基线对照）。
- **SC-002**: 在 50 组 JSON 选择样例中，寄存器参与/不参与随机的命中正确率达到 100%。
- **SC-003**: 固定同一随机种子重复运行 10 次，生成的 cmd.cfg 内容一致率达到 100%。
- **SC-004**: 对 1000 个位域随机赋值任务，整体生成流程在 5 秒内完成。
- **SC-005**: 输出 cmd.cfg 可被下游流程直接读取，人工修正步骤为 0。

## Assumptions

- random_require.md 仅作为开发阶段参考规则来源，不作为脚本运行时输入。
- 当前范围以 `t_reg_vcpi` 及其可达结构为主，不强制覆盖无关寄存器族。
- JSON 选择文件由调用方按约定格式提供，且包含合法的寄存器名。
- 地址信息若在头文件中未直接声明，可允许以寄存器标识和位域信息完成生成目标。
- cmd.cfg 输出编码与换行格式满足当前运行环境默认规范。
