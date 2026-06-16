# Feature Specification: 寄存器随机配置生成（更新）

**Feature Branch**: `001-register-random-generator`

**Created**: 2026-06-11

**Status**: Draft

**Input**: User description: "更新 001：支持 t_reg_vcpi 全寄存器随机；通过 JSON 指定寄存器是否参与随机；脚本通过解析该 JSON 完成指定寄存器随机；random_require.md 仅用于制定开发规则，不作为脚本运行输入。"

## Clarifications

### Session 2026-06-12

- Q: 寄存器定义数据源是什么？vcpi.xlsx 还是 reg_data.h，还是两者都需要？ → A: 以 reg_data.h 作为寄存器与位域结构的唯一定义来源；vcpi.xlsx 仅用于提供字段级随机约束规则（列J 约束范围、列I 规则描述）。两者均为运行时输入。
- Q: vcpi.xlsx 是否覆盖 reg_data.h 中的全部字段？缺失字段如何处理？ → A: 以 reg_data.h 为准，vcpi.xlsx 中未记录的字段按完整位宽范围随机，不报错。
- Q: vcpi.xlsx 列J 约束的格式如何，脚本应如何解析并生成符合约束的随机值？ → A: 三种格式：(1) 单一值（如 `0`）→ 固定赋该值；(2) 区间（如 `[a,b]` 或 `[a:b]`，含 Verilog 写法如 `[-4'd6:4'd6]` 仅取 `d` 后数字简化为 `[-6,6]`）→ 在区间内随机，同时遵守列I 描述规则；(3) 候选值列表（如 `0,1,2,3`）→ 从候选值中随机选取。
- Q: vcpi.xlsx 列I 描述规则应如何执行？对无法解析的规则如何处理？ → A: 识别固定关键词模式（如对齐约束、特定编解码格式限制等）并应用至随机生成逻辑；无法识别的规则内容记录 WARNING 日志后跳过，不阻断生成过程。
- Q: vcpi.xlsx 列H 重置值应如何处理？是否影响随机逻辑？ → A: 当字段无列J 约束时，以列H 重置值为随机基准（在重置值附近浮动随机）；若同时无列H 则回退到完整位宽范围均匀随机。
- Q: vcpi.xlsx 是否作为运行时输入？ → A: 否。vcpi.xlsx 已一次性解析，全部约束规则（列J/H/I）以静态 Python 字典 `VCPI_FIELD_CONSTRAINTS` 形式硬编码于脚本中，运行时不再依赖 vcpi.xlsx 文件。
- Q: 列I 描述中的"minus1 config"字段（如 ve_pic_height/width）应如何处理对齐约束？对齐约束应应用于配置值还是实际像素值？ → A: 对齐约束应用于**实际像素值**（即配置值+1）。生成流程：(1) 按对齐规则生成对齐的实际像素值（如2880，16的倍数）；(2) 减去1后存储到配置文件（如存储2879）；(3) 硬件读取时通过+1还原得到对齐的实际值。这样确保实际使用的像素尺寸满足编解码器对齐要求（HEVC 8x8 CTU、H.264/JPEG 16x16宏块）。

### Session 2026-06-15

- Q: cmd.cfg 的键值分隔符是否需要兼容多种格式？ → A: 需要。cmd.cfg 同时支持 `field : value` 与 `field = value` 两种分隔格式，生成与解析链路都必须兼容。
- Q: 解析到未知字段时应如何处理？ → A: 严格失败。遇到未知字段必须立即返回非零并输出包含 section 与字段名的错误信息，不允许静默跳过。
- Q: API 调用形参应采用哪种方式传递 `t_reg_vcpi`？ → A: 提供按值与指针两种入口（包装层），内部统一为 `const t_reg_vcpi*` 调用路径，保证性能与兼容性。
- Q: 同一 section 内字段重复出现时如何处理？ → A: 严格失败。重复字段视为输入错误，必须立即返回非零并报告重复字段名与 section。
- Q: cfg 缺失 section 或字段时应如何处理？ → A: 默认按 0 填充并继续解析，不报错；仅对未知字段与重复字段执行严格失败。
- Q: t_reg_vcpi 中结构体数组成员（如 VCPI_QPG_LAMBDA[52]）在 JSON 中如何表示逐元素选择？ → A: 使用 `indices` 列表：`{"name":"VCPI_QPG_LAMBDA","indices":[0,1,5],"enabled":true}`；支持 `"indices":"all"` 作为全选语法糖；未出现在 indices 中的元素不随机，不写入 cfg。
- Q: cfg section 头 `MEMBER[N]` 中 `N` 的合法格式是什么？非法格式如何处理？ → A: `N` 接受十进制非负整数或关键字 `all`（含义为全数组遍历）；其他内容跳过该 section 头行，不报错，不终止解析。
- Q: register_selection.json 中数组类型条目缺失 `indices` 字段时如何处理？ → A: 快速失败。数组成员条目 MUST 声明 `indices`，缺失视为格式错误，系统 MUST 立即返回非零并报告缺失成员名。
- Q: `print_vcpi_debug_dump` 格式化打印数组元素时如何输出？ → A: 每个元素输出 `MEMBER[N] = 0xXXXXXXXX` 行，再跟缩进的位域展开行（字段名右对齐，值左对齐）；与 cfg section 头格式一致，便于对照和 diff。
- Q: Python 生成器写出 cfg 时使用冒号还是等号？C 解析器调试打印使用哪种？ → A: Python 生成器 MUST 写冒号（`field : value`）；C 解析器读取时兼容冒号与等号；调试打印 `print_vcpi_debug_dump` MUST 输出等号（`field = value`），与 reg_data.h 结构体风格一致。
- Q: cfg 中数组 section 下标越界（如 `VCPI_QPG_LAMBDA[99]`）时 C 解析器应如何处理？ → A: 严格失败。立即返回非零并报告成员名与越界下标，禁止静默跳过或自动裁剪。
- Q: cfg 中同一数组成员下标重复出现（如两次 `VCPI_QPG_LAMBDA[3]`）时 C 解析器应如何处理？ → A: 严格失败。立即返回非零并报告重复成员名与下标，禁止覆盖或忽略。

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

1. **Given** 已完成寄存器解析与 JSON 选择后的随机赋值，**When** 生成 cmd.cfg，**Then** 输出文件包含按寄存器分组的键值条目（支持 `:` 或 `=` 分隔）。
2. **Given** 同一次运行存在多个寄存器结果，**When** 写入 cmd.cfg，**Then** 文件内分组顺序稳定且每个字段仅出现一次。

### Edge Cases

- JSON 文件中包含 `t_reg_vcpi` 不存在的寄存器名时，系统应报告明确错误并指出目标名称。
- JSON 文件缺失、格式非法或关键字段缺失时，系统应快速失败并给出可诊断信息。
- JSON 文件将全部寄存器标记为禁用时，系统应给出明确提示并按约定输出空结果或失败。
- reg_data.h 缺失或不可读时，系统应快速失败并输出可诊断信息。
- vcpi.xlsx 缺失或格式非法时，系统应快速失败并输出可诊断信息。
- vcpi.xlsx 列J 约束区间范围超过字段位宽上限时，系统应警告并自动裁剪至合法范围。
- vcpi.xlsx 列I 描述规则无法识别时，记录 WARNING 日志并跳过，不阻断生成。
- 标记为"minus1 config"的字段同时具有对齐约束时，对齐应用于实际值（配置值+1），生成的配置值为对齐后的实际值减1（如实际2880对齐，存储2879）。
- 标记为"minus1 config"的字段若约束范围为[min, max]，生成的配置值应确保实际值（配置值+1）在对齐后仍满足[min+1, max+1]范围。
- cmd.cfg 中键值行若混用 `:` 与 `=` 分隔符，系统应保持稳定解析并输出一致结果。
- cmd.cfg 中若出现不属于当前 section 的未知字段，系统应立即失败并给出可定位错误信息。
- cmd.cfg 同一 section 内若出现同名字段重复赋值，系统应立即失败并报告冲突位置。
- cmd.cfg 缺失某些 section 或字段时，系统应将对应 `t_reg_vcpi` 位置保留为 0 并继续处理。
- 结构体数组成员的 JSON 条目中若 `indices` 越界（下标 >= 数组长度），系统应快速失败并报告越界下标。
- cfg 文件中结构体数组 section 头格式为 `MEMBER_NAME[N]`（如 `VCPI_QPG_LAMBDA[0]`），C 解析器必须能识别并路由到正确的数组槽；`N` 为十进制非负整数或关键字 `all`，其他格式跳过该行。
- cfg 文件中若数组 section 下标越界（`N` >= 数组长度），C 解析器应立即失败并输出成员名与越界下标。
- cfg 文件中若同一数组成员下标 section 重复出现（同一 `MEMBER_NAME[N]` 出现多次），C 解析器应立即失败并输出成员名与下标。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统 MUST 读取并解析 reg_data.h 中 `t_reg_vcpi` 下定义的全部寄存器与位域信息（寄存器名、位宽、位域列表）。
- **FR-002**: 系统 MUST 提取每个寄存器及其位域的名称与位宽信息，以 reg_data.h 为唯一结构权威来源。
- **FR-002b**: 系统 MUST 使用静态内嵌的 `VCPI_FIELD_CONSTRAINTS` 字典（由 vcpi.xlsx 一次性解析生成，硬编码于脚本中）作为字段级随机约束来源，匹配键为（寄存器名, 字段名）元组。运行时不依赖 vcpi.xlsx 文件。字典中未记录的字段按完整位宽范围随机，不视为错误。
- **FR-003**: 系统 MUST 读取 JSON 选择文件并识别每个寄存器是否参与随机。
- **FR-003b**: 对 `t_reg_vcpi` 中的结构体数组成员，JSON MUST 使用 `indices` 字段指定参与随机的下标列表；`"indices":"all"` 表示全部元素均参与随机。未列出的下标不随机且不写入 cfg。越界下标 MUST 触发快速失败并报告具体下标与成员名。数组成员缺失 `indices` 字段时 MUST 快速失败，并提示成员名。
- **FR-004**: 系统 MUST 仅对 JSON 标记为参与随机的寄存器执行随机赋值。
- **FR-005**: 系统 MUST 在随机赋值前校验 JSON 与寄存器定义的一致性（目标存在性、字段完整性、格式合法性）。
- **FR-006**: 系统 MUST 为被选中寄存器的每个位域生成符合约束的随机值，按以下优先级：
  1. vcpi.xlsx 列J 为单一值 → 固定赋该值；
  2. vcpi.xlsx 列J 为区间（`[a,b]` / `[a:b]`，含 Verilog 位宽前缀格式，仅取 `d` 后数字）→ 在 `[a,b]` 内随机，同时满足列I 描述规则（如对齐、编解码格式限制等）；
  3. vcpi.xlsx 列J 为候选值列表（`v1,v2,...`）→ 从候选值中均匀随机选取；
  4. vcpi.xlsx 无对应记录且列H 有重置值 → 以重置值为随机基准，在 `[0, 2^width-1]` 范围内浮动随机（具体浮动策略为实现阶段确定）；
  5. vcpi.xlsx 无对应记录且列H 无重置值 → 按字段位宽 `[0, 2^width-1]` 均匀随机。
- **FR-006b**: 对列I 描述规则，系统 MUST 识别并应用已知关键词模式（如 2/4/8/16 像素对齐、编解码格式限制、minus1 config等）至随机候选过滤或调整。无法识别的规则内容 MUST 记录 WARNING 日志后跳过，不阻断生成流程。
- **FR-006c**: 对标记为"minus1 config"的字段（如 ve_pic_height/width），系统 MUST：(1) 先按对齐约束生成对齐的实际值V（如2880满足16对齐）；(2) 验证V在约束范围[min, max]内；(3) 存储V-1至配置文件（如存储2879）。对齐约束应用于实际值（配置值+1），而非配置值本身。
- **FR-007**: 系统 MUST 支持由用户提供随机种子以保证结果可复现。
- **FR-008**: 系统 MUST 将最终结果写入 cmd.cfg，格式为按寄存器分组的键值文本；Python 生成器 MUST 使用冒号分隔符（`field : value`）；C 解析器读取时 MUST 同时兼容冒号与等号。
- **FR-008b**: 结构体数组成员在 cfg 中 MUST 以 `MEMBER_NAME[N]` 作为 section 头（如 `#================ VCPI_QPG_LAMBDA[0] ====================`），每个启用的下标占一个独立 section，按下标升序排列；`N` 为十进制非负整数；C 解析器 MUST 同时支持 `MEMBER_NAME[all]` 语法，等价于遍历全部数组元素。
- **FR-008c**: `print_vcpi_debug_dump` 调试打印 MUST 使用等号分隔符（`field = value`），字段名右对齐至同列，值左对齐，与 reg_data.h 结构体定义风格保持一致。对数组成员 MUST 按下标升序输出每个元素，格式为 `MEMBER[N] = 0xXXXXXXXX`，其后跟缩进位域展开行。
- **FR-009**: 系统 MUST 在 cmd.cfg 中使用稳定且可预测的输出顺序。
- **FR-010**: 系统 MUST 对无效 JSON、不存在寄存器目标和输入文件缺失提供可定位错误信息。
- **FR-010b**: C 解析链路在遇到未知字段时 MUST 立即失败（非零退出），并在错误信息中同时包含 section 名与字段名。
- **FR-010c**: C 接口层 MUST 同时提供按值与按 `const t_reg_vcpi*` 传参的 API 入口；实现层 MUST 统一走 `const t_reg_vcpi*` 路径，避免重复逻辑。
- **FR-010d**: C 解析链路在同一 section 遇到重复字段时 MUST 立即失败（非零退出），并在错误信息中包含 section 名与重复字段名。
- **FR-010e**: C 解析链路在 cfg 缺失 section 或字段时 MUST 以 0 作为默认值继续解析，不得因此报错失败。
- **FR-010f**: C 解析链路在遇到数组 section 下标越界时 MUST 立即失败（非零退出），并在错误信息中包含数组成员名与越界下标值。
- **FR-010g**: C 解析链路在同一输入中遇到重复数组 section（相同 `MEMBER_NAME[N]`）时 MUST 立即失败（非零退出），并在错误信息中包含数组成员名与重复下标值。
- **FR-011**: 系统 MUST 在一次运行中完成解析、筛选、随机与导出（及可选 C 组装/调用）流程，不依赖人工干预。
- **FR-012**: 系统 MUST 不将 random_require.md 作为脚本运行时输入，不解析该文件。

## Constitution Alignment *(mandatory)*

- **CA-001 Source of Truth**: 本特性以 reg_data.h 中 `t_reg_vcpi` 及关联结构体为寄存器定义唯一来源，不维护独立位域镜像。
- **CA-002 Runtime Constraints**: 交付物严格遵循宪法中定义的运行时与依赖约束。
- **CA-003 Delivery Shape**: 交付形态为每个语言组件单一主实现文件（Python 单 `.py`，C 单 `.c`）。
- **CA-004 Function Design**: 功能边界划分为头文件解析、JSON 选择解析、随机生成、输出写入与错误报告等单一职责函数。
- **CA-005 Verifiability**: 支持显式随机种子与结构化中间结果校验，保证可复现实验。
- **CA-006 Maintainability**: 对位域边界计算、规则优先级与异常分支提供完整注释说明。

### Key Entities *(include if feature involves data)*

- **RegisterDefinition**: 单个寄存器定义，包含寄存器名、寄存器位宽、位域列表；来源 reg_data.h。
- **BitFieldDefinition**: 位域定义，包含位域名、位宽、所在寄存器、可选默认值信息；来源 reg_data.h。
- **FieldConstraint**: 字段约束规则，来源 vcpi.xlsx，匹配键为（寄存器名, 字段名）元组。包含：列J 约束格式（单一值/区间/候选列表）、列I 规则描述（含对齐约束、minus1 config标记等）、列H 重置值。字段无对应约束且有重置值时以重置值为随机基准；字段无对应约束且无重置值时使用 `[0, 2^width-1]`。对标记为"minus1 config"的字段：先按对齐要求生成对齐的实际值V，再存储V-1至配置文件。
- **RegisterSelection**: 来自 JSON 文件的寄存器选择项，包含寄存器名与是否参与随机标记。对数组类型成员，额外包含 `indices` 字段（整数列表或字符串 `"all"`），用于指定参与随机的数组下标。
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
