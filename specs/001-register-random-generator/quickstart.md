# Quickstart: 寄存器随机配置生成验证指南（JSON 选择更新）

## Prerequisites
- Python 3 可用（遵循项目宪法约束）。
- 输入文件存在:
  - `reg_data.h`
  - `register_selection.json`

## Validation Scenario A: 基础生成
1. 运行脚本（示例命令，实际脚本名以实现为准）:
  `python random_reg_cfg.py --header reg_data.h --select-json register_selection.json --out cmd.cfg`
2. 预期结果:
  - 生成 `cmd.cfg`。
  - 仅包含 JSON 中 `enabled=true` 的寄存器分组。
  - 每个位域均有十进制值。

## Validation Scenario B: 可复现性
1. 使用固定 seed 连续运行两次:
  `python random_reg_cfg.py --header reg_data.h --select-json register_selection.json --seed 123 --out cmd.cfg`
2. 预期结果:
  - 两次输出的 `cmd.cfg` 完全一致。

## Validation Scenario C: 约束正确性
1. 检查 `VCPI_PIC_SIZE`:
  - `ve_pic_width % 2 == 0`
  - `ve_pic_height % 2 == 0`
  - `ve_pic_width <= 1920`
  - `ve_pic_height <= 1080`
2. 预期结果: 全部满足。

## Validation Scenario D: 非法 JSON
1. 在 `register_selection.json` 中故意指定不存在寄存器或非法 JSON。
2. 运行脚本。
3. 预期结果:
  - 非零退出。
  - 错误信息包含 JSON 结构或目标定位信息。
  - 不生成不完整 `cmd.cfg`。

## References
- Data model: `data-model.md`
- Rule contract: `contracts/random-require-rules.md`
- Output contract: `contracts/cmd-cfg-format.md`

## Sample register_selection.json

```json
{
  "registers": [
    {"name": "VCPI_PIC_INFO0", "enabled": true},
    {"name": "VCPI_PIC_SIZE", "enabled": true},
    {"name": "VCPI_ME_INFO0", "enabled": false}
  ]
}
```

## Expected Output Snippet

```cfg
#======== VCPI_PIC_INFO0 ================
ve_frame_type                   : 0
ve_protocol                     : 2
ve_chroma_format                : 0

#======== VCPI_PIC_SIZE =================
ve_pic_height                   : 894
ve_pic_width                    : 1586
```

## Validation Record (2026-06-11)

- Scenario A: PASS
  - 命令: `python random_reg_cfg.py --header reg_data.h --select-json register_selection.json --out cmd.cfg`
  - 结果: 成功生成 `cmd.cfg`，仅包含 `enabled=true` 的 `VCPI_PIC_INFO0` 与 `VCPI_PIC_SIZE`。
- Scenario B: PASS
  - 命令: 固定 seed 两次运行，输出 `cmd_seed123_a.cfg` 与 `cmd_seed123_b.cfg`。
  - 结果: `seed_reproducible=True`。
- Scenario C: PASS
  - 结果: `ve_pic_width=1586`、`ve_pic_height=894`，均为 2 对齐且不超过上限。
- Scenario D: PASS
  - 命令: `python random_reg_cfg.py --header reg_data.h --select-json invalid_selection.json --out cmd_invalid.cfg`
  - 结果: 非零退出并输出 `E_SELECTION_SCHEMA_INVALID`。
