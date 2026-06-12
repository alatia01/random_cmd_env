# Phase 0 Research: 寄存器随机配置生成（JSON 选择更新）

## Decision 1: `reg_data.h` 全寄存器解析策略
- Decision: 保持两阶段解析（结构体定义解析 + `t_reg_vcpi` 成员映射），并将覆盖范围扩展为 `t_reg_vcpi` 下全部寄存器。
- Rationale: 满足“全寄存器随机能力”需求，同时保持与头文件同步。
- Alternatives considered:
  - 仅维护白名单寄存器: 不满足全覆盖。
  - 手工映射配置文件: 与单一事实来源冲突。

## Decision 2: JSON 选择文件作为唯一运行时筛选输入
- Decision: 新增 `register_selection.json` 作为运行时输入，指定寄存器是否参与随机；脚本不读取 `random_require.md`。
- Rationale: 用户明确要求运行阶段通过 JSON 控制参与范围，`random_require.md` 仅用于开发规则说明。
- Alternatives considered:
  - 继续解析 `random_require.md`: 与更新要求冲突。
  - CLI 直接传大量寄存器名: 可维护性与可复用性较差。

## Decision 3: JSON 契约的最小结构
- Decision: 定义稳定 JSON 结构（`registers` 列表，元素包含 `name` 与 `enabled`），并允许附加元数据字段。
- Rationale: 结构简单，易于手工编写与程序校验。
- Alternatives considered:
  - 扁平键值 map: 不便扩展字段（例如优先级、备注）。
  - 复杂层级嵌套: 增加解析与使用成本。

## Decision 4: 随机与复现机制
- Decision: 使用 `random.Random(seed)` 实例化 RNG，且同一运行内共享随机源。
- Rationale: 可复现且符合标准库-only约束。
- Alternatives considered:
  - `secrets`: 不强调可复现。
  - 全局随机状态: 易受外部干扰。

## Decision 5: 业务约束保留策略
- Decision: 对 `VCPI_PIC_SIZE.ve_pic_width/height` 保留 2 对齐与 1080p 上限约束，无论是否全寄存器模式。
- Rationale: 这是明确业务约束，不应因输入方式变更而丢失。
- Alternatives considered:
  - 仅按位宽上限: 无法保证业务有效分辨率。

## Decision 6: `cmd.cfg` 输出契约
- Decision: 保持分组头 + 键值行格式，顺序由 `t_reg_vcpi` 与字段定义顺序确定。
- Rationale: 与现有下游兼容，便于差异比对。
- Alternatives considered:
  - JSON 输出: 可读性/兼容性不足。

## Decision 7: 错误处理策略
- Decision: 对 JSON 文件缺失/格式非法/寄存器不存在/全部禁用采用 fail-fast（或按契约输出空结果），并提供清晰错误码。
- Rationale: 工具链自动化需要可诊断与可预期行为。
- Alternatives considered:
  - 静默忽略非法项: 风险不可控。

## Decision 8: Verilog 数字格式解析策略 (2026-06-12)
- Decision: 实现完整 Verilog 数字格式解析器，支持基数标识符 (`'d` 十进制, `'h` 十六进制, `'b` 二进制, `'o` 八进制)，正确区分 `16'd8190` (十进制 8190) 与 `16'h8190` (十六进制 33168)。
- Rationale: vcpi.xlsx 列 J 约束值使用 Verilog 格式（如 `16'd127`），之前错误地将所有带引号数字按十六进制解析导致约束范围错误（如 `16'd8190` 被解析为 33168 而非 8190）。
- Alternatives considered:
  - 简化为仅支持十进制: 不符合 vcpi.xlsx 实际格式。
  - 手工转换 Excel 内容: 违反单一事实来源原则。
- Impact: 修复后，VCPI_SRC_MOSAIC_POS 系列字段范围从错误的 [0, 33k+] 修正为正确的 [0, 8k] 范围。

## Decision 9: 对齐约束提取与应用策略 (2026-06-12)
- Decision: 从 vcpi.xlsx 列 I 描述中提取像素对齐约束（如 "2pixel align", "HEVC：8pixel align", "H.264/JPGE：16x16 align"），存储为约束字典的 `"a"` 字段，并在随机生成时通过 `pick_aligned()` 函数强制应用。
- Rationale:
  - 寄存器字段具有硬件对齐要求（如 VCPI_PIC_SIZE 必须 16 像素对齐以满足 H.264/JPEG 编码器要求）
  - 未对齐的值会导致硬件配置错误或编码失败
  - 约束信息已存在于 vcpi.xlsx 列 I，应充分利用而非丢弃
- Implementation:
  - 支持中英文冒号混用（"HEVC：8pixel" 与 "HEVC: 8pixel"）
  - 支持多协议对齐声明，取最大值确保兼容所有协议
  - 138 个字段包含对齐约束（15% 的总字段数）
- Alternatives considered:
  - 忽略对齐约束，仅按范围随机: 生成值可能不符合硬件要求。
  - 运行时动态选择协议对齐: 当前系统无协议信息，取最大值是保守策略。
- Verification: 通过多种子测试验证 VCPI_PIC_SIZE.ve_pic_width/height 始终为 16 的倍数。

## Decision 10: 位宽验证与约束范围裁剪 (2026-06-12)
- Decision: 在约束提取阶段验证列 J 约束范围不超过列 G 实际位宽，若超出则裁剪至合法范围 `[0, 2^width - 1]`。
- Rationale: 防止生成超出字段位宽的无效值（硬件截断导致不可预期行为）。
- Result: 所有 919 个字段验证通过，0 个字段需要裁剪（vcpi.xlsx 数据质量良好）。
- Alternatives considered:
  - 运行时裁剪: 增加生成开销，且无法提前发现数据质量问题。
  - 报错停止: 过于严格，不利于部分约束缺失场景。

## Decision 11: minus1 config 字段处理策略 (2026-06-12)
- Decision: 对 vcpi.xlsx 列 I 描述中标记为"minus1 config"的字段（如 ve_pic_height/width），对齐约束应用于**实际像素值**（配置值+1），生成流程为：
  1. 按对齐规则生成对齐的实际值 V（如 2880，16 的倍数）
  2. 验证 V 在约束范围 [min, max] 内
  3. 存储 V-1 至配置文件（如存储 2879）
- Rationale:
  - 硬件使用"minus1 config"存储优化：实际值 = 配置值 + 1，节省 1 位存储空间
  - 对齐约束来自编解码器要求（HEVC 8x8 CTU、H.264/JPEG 16x16 宏块），应用于实际使用的像素尺寸
  - 若对齐应用于配置值，则实际值 = (对齐的配置值) + 1 会破坏对齐（如配置 128 → 实际 129，不满足 16 对齐）
- Implementation:
  - 在约束字典中添加 `"m"` (minus1) 标记字段（布尔值）
  - `generate_field_value()` 检测 minus1 标记时：
    - 使用 `pick_aligned(rng, min+1, max+1, alignment)` 生成实际值
    - 返回 `actual_value - 1` 作为配置值
  - 已识别的 minus1 字段：ve_pic_height, ve_pic_width, ve_num_tile_columns_minus1, ve_num_tile_rows_minus1
- Alternatives considered:
  - 对配置值对齐: 破坏实际值对齐，导致硬件配置错误。
  - 生成时不减 1，后处理减 1: 增加复杂度，且约束验证逻辑分散。
- Verification: 更新 quickstart.md 验证场景，确认 minus1 字段配置值 + 1 后满足对齐要求。
