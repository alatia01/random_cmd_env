# Data Model: 寄存器随机配置生成（JSON 选择更新）

## Entity: RegisterDefinition
- Purpose: 表示一个可随机配置的寄存器。
- Fields:
  - `name` (string): 寄存器名，例如 `VCPI_PIC_INFO0`。
  - `type_name` (string): 对应结构类型名，例如 `t_reg_vcpi_pic_info0`。
  - `bit_width` (int | null): 整寄存器位宽（可选，位域拼装场景可为空）。
  - `fields` (list[BitFieldDefinition]): 位域列表，按头文件定义顺序。
- Validation:
  - `name` 非空且唯一（在一个寄存器域内）。
  - `fields` 中位域名不重复。

## Entity: BitFieldDefinition
- Purpose: 表示寄存器中的单个位域。
- Fields:
  - `register_name` (string)
  - `name` (string): 位域名，例如 `ve_frame_type`。
  - `width` (int): 位宽，必须 >0。
  - `lsb` (int | null): 最低位索引（若可解析）。
  - `msb` (int | null): 最高位索引（若可解析）。
  - `reset_value` (int | null): 可选复位值。
- Validation:
  - `0 < width <= 32`。
  - 若 `lsb/msb` 存在，则 `msb - lsb + 1 == width`。

## Entity: RegisterSelection
- Purpose: 来自 `register_selection.json` 的寄存器参与开关条目。
- Fields:
  - `name` (string): 寄存器名，例如 `VCPI_PIC_INFO0`。
  - `enabled` (bool): 是否参与随机。
  - `source_index` (int): 在 JSON 列表中的位置，便于错误定位。
- Validation:
  - `name` 必须存在于 `t_reg_vcpi` 解析结果中。
  - `enabled` 必须为布尔值。

## Entity: GenerationContext
- Purpose: 单次运行上下文。
- Fields:
  - `seed` (int | null)
  - `registers` (dict[str, RegisterDefinition])
  - `selection` (list[RegisterSelection])
  - `active_registers` (list[string]): 由 JSON 中 `enabled=true` 过滤得到

## Entity: GeneratedFieldValue
- Purpose: 记录单个位域的最终值。
- Fields:
  - `register_name` (string)
  - `field_name` (string)
  - `value` (int)
  - `applied_rule_mode` (enum)

## Entity: GenerationResult
- Purpose: 最终输出结果。
- Fields:
  - `items` (list[GeneratedFieldValue])
  - `ordered_map` (dict[str, list[GeneratedFieldValue]]): 用于稳定写出 `cmd.cfg`。
  - `warnings` (list[string])
  - `metadata` (dict): 包含 `seed`、输入文件路径、生成时间。

## Relationships
- 一个 `RegisterDefinition` 拥有多个 `BitFieldDefinition`（1:N）。
- 一个 `RegisterSelection` 绑定一个寄存器（N:1 到 `RegisterDefinition`）。
- 一个 `GenerationResult` 包含多个 `GeneratedFieldValue`（1:N）。

## State Transitions
1. `Parsed`: 从 `reg_data.h` 解析出寄存器模型。
2. `Selected`: 从 `register_selection.json` 得到参与随机的寄存器集合。
3. `Validated`: 完成选择目标存在性、JSON 结构与边界约束校验。
4. `Generated`: 随机值生成完成。
5. `Exported`: `cmd.cfg` 写出完成。
