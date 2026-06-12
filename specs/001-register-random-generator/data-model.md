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

## Entity: FieldConstraint (2026-06-12 更新)
- Purpose: 表示从 vcpi.xlsx 提取的字段级约束信息，存储于 `VCPI_FIELD_CONSTRAINTS` 静态字典。
- Key: `(register_name: str, field_name: str)` 元组
- Fields:
  - `c` (tuple | null): 约束类型
    - `('fixed', value: int)`: 固定值
    - `('range', lo: int, hi: int)`: 范围约束
  - `r` (int | null): 复位值（列 H）
  - `d` (str | null): 描述摘要（列 I 前 80 字符）
  - `w` (int): 位宽（列 G 解析结果，已验证）
  - `a` (dict | null): 对齐约束（2026-06-12 新增）
    - `{'default': int}`: 通用对齐（如 `{'default': 4}` 表示 4 像素对齐）
    - `{'hevc': int, 'h264': int, 'jpeg': int}`: 协议特定对齐
  - `m` (bool | null): minus1 config 标记（2026-06-12 新增）
    - `True`: 字段使用 minus1 存储格式（实际值 = 配置值 + 1）
    - 对齐约束应用于实际值，存储时减 1
    - 示例：ve_pic_height/width, ve_num_tile_columns_minus1, ve_num_tile_rows_minus1
- Validation:
  - 若 `c` 为 range，则 `lo <= hi` 且 `hi <= 2^w - 1`
  - 若 `a` 存在，对齐值必须为 2 的幂（1, 2, 4, 8, 16）
  - 若 `m` 为 True 且 `a` 存在，对齐应用于 `value+1` 而非 `value`
- Examples:
  ```python
  ("VCPI_PIC_SIZE", "ve_pic_width"): {
      "c": ('range', 63, 8191),
      "r": 127,
      "d": "the picture width for enc view...",
      "w": 16,
      "a": {'hevc': 8, 'h264': 16, 'jpeg': 16},
      "m": True  # 存储值 = 实际像素值 - 1
  }
  
  ("VCPI_SRC_MOSAIC_POS_0", "ve_mosaic_0_st_x"): {
      "c": ('range', 0, 8188),
      "r": 0,
      "d": "Mosaic_0_START_X,4pixel align",
      "w": 16,
      "a": {'default': 4}
      # 无 "m" 字段，对齐直接应用于配置值
  }
  ```

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
