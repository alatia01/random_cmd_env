# Contract: register_selection.json 选择解释（v2）

## Purpose
定义 `register_selection.json` 在本特性中的可执行语义，作为脚本筛选随机目标的唯一运行时契约。

## Scope
- 目标域: `t_reg_vcpi` 下全部寄存器。
- 控制能力: 仅控制“寄存器是否参与随机”。

## JSON Schema (logical)

```json
{
  "registers": [
    {
      "name": "VCPI_PIC_INFO0",
      "enabled": true
    },
    {
      "name": "VCPI_PIC_SIZE",
      "enabled": true
    }
  ]
}
```

## Semantics
1. `registers` 是必填数组。
2. `name` 必须匹配 `t_reg_vcpi` 中存在的寄存器名。
3. `enabled=true` 表示该寄存器参与随机并写入输出。
4. `enabled=false` 表示该寄存器不参与随机，不写入输出。
5. 当寄存器重复出现时，后出现条目覆盖前者（last-write-wins）。

## Mandatory Business Constraints (2026-06-12 更新)

### VCPI_PIC_SIZE 对齐约束（从 vcpi.xlsx 提取）
- `VCPI_PIC_SIZE.ve_pic_width`:
  - **minus1 config**: 配置值 = 实际像素值 - 1
  - 实际像素值（配置值+1）必须 16 对齐（max(HEVC:8, H.264:16, JPEG:16)）
  - 约束范围: `[63, 8191]`（实际像素值: [64, 8192]）
  - 示例: 配置值 2879 → 实际值 2880 (2880 % 16 = 0 ✓)

- `VCPI_PIC_SIZE.ve_pic_height`:
  - **minus1 config**: 配置值 = 实际像素值 - 1
  - 实际像素值（配置值+1）必须 16 对齐（max(HEVC:8, H.264:16, JPEG:16)）
  - 约束范围: `[63, 8191]`（实际像素值: [64, 8192]）
  - 示例: 配置值 1919 → 实际值 1920 (1920 % 16 = 0 ✓)

### VCPI_SRC_MOSAIC_POS 对齐约束
- `VCPI_SRC_MOSAIC_POS.ve_mosaic_st_x`:
  - 4 像素对齐（配置值直接对齐）
  - 约束范围: `[0, 8188]`

- `VCPI_SRC_MOSAIC_POS.ve_mosaic_st_y`:
  - 2 像素对齐（配置值直接对齐）
  - 约束范围: `[0, 8190]`

**注意**: 约束信息硬编码于脚本的 `VCPI_FIELD_CONSTRAINTS` 字典，运行时不依赖外部约束文件。

## Validation Errors
- `E_SELECTION_FILE_MISSING`
- `E_SELECTION_JSON_INVALID`
- `E_SELECTION_SCHEMA_INVALID`
- `E_SELECTION_TARGET_NOT_FOUND`
- `E_SELECTION_EMPTY_ACTIVE_SET`

## Error Examples
- `E_SELECTION_FILE_MISSING: register_selection.json`
- `E_SELECTION_JSON_INVALID: Expecting value`
- `E_SELECTION_SCHEMA_INVALID: registers[0] requires name(str), enabled(bool)`
- `E_SELECTION_TARGET_NOT_FOUND: VCPI_UNKNOWN at index 2`
- `E_SELECTION_EMPTY_ACTIVE_SET`

## Runtime Input Rules
- 脚本运行时必须读取 `register_selection.json`。
- 脚本运行时不得解析 `random_require.md`。
