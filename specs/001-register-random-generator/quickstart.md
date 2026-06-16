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

## Validation Scenario C: 约束正确性 (2026-06-12 更新)
1. 检查 `VCPI_PIC_SIZE` 对齐约束:
  - `ve_pic_width % 16 == 0` (HEVC:8像素, H.264/JPEG:16像素 → 取最大值 16)
  - `ve_pic_height % 16 == 0`
  - `63 <= ve_pic_width <= 8191`
  - `63 <= ve_pic_height <= 8191`
2. 检查 `VCPI_SRC_MOSAIC_POS_0` 对齐约束（若启用）:
  - `ve_mosaic_0_st_x % 4 == 0` (4像素对齐)
  - `ve_mosaic_0_st_y % 2 == 0` (2像素对齐)
  - `0 <= ve_mosaic_0_st_x <= 8188`
  - `0 <= ve_mosaic_0_st_y <= 8190`
3. 预期结果: 全部满足。

## Validation Scenario D: 对齐约束多种子验证 (2026-06-12 新增)
1. 使用多个种子生成并验证对齐:
  ```powershell
  for ($i=1; $i -le 5; $i++) {
      python random_reg_cfg.py --header reg_data.h `
          --select-json register_selection.json `
          --seed $i --out "cmd_seed$i.cfg"
  }
  # 检查所有输出中 ve_pic_width 和 ve_pic_height 都是 16 的倍数
  ```
2. 预期结果:
  - 所有种子生成的 `ve_pic_width` 和 `ve_pic_height` 均满足 `value % 16 == 0`
  - 值在约束范围 [63, 8191] 内
  - 不同种子生成不同值，但都符合对齐和范围要求

## Validation Scenario E: minus1 config 正确性验证 (2026-06-12 新增)
1. 检查 `VCPI_PIC_SIZE` 中 minus1 config 字段:
  - 读取 `cmd.cfg` 中的 `ve_pic_width` 和 `ve_pic_height` 配置值
  - 计算实际值: `actual_width = config_width + 1`, `actual_height = config_height + 1`
  - 验证实际值满足对齐: `actual_width % 16 == 0` 且 `actual_height % 16 == 0`
2. 示例:
  ```
  配置值: ve_pic_width = 2879, ve_pic_height = 1919
  实际值: 2879 + 1 = 2880 (2880 % 16 = 0 ✓), 1919 + 1 = 1920 (1920 % 16 = 0 ✓)
  ```
3. 预期结果:
  - **配置值可能不对齐**（如 2879 % 16 = 15）
  - **实际值必须对齐**（如 2880 % 16 = 0）
  - 实际值在约束范围内：`64 <= actual_value <= 8192`（对应配置值 [63, 8191]）

## Validation Scenario G: 数组成员 JSON indices 选择 (2026-06-15 新增)

```json
{
  "registers": [
    {"name": "VCPI_PIC_INFO0", "enabled": true},
    {"name": "VCPI_QPG_LAMBDA", "enabled": true, "indices": [0, 1]},
    {"name": "VCPI_SAO_LAMBDA_GROUP", "enabled": true, "indices": "all"}
  ]
}
```

1. 运行生成器:
   `python random_reg_cfg.py --header reg_data.h --select-json register_selection_array.json --out cmd_array.cfg`
2. 预期结果:
   - `cmd_array.cfg` 包含 `VCPI_QPG_LAMBDA[0]` 和 `VCPI_QPG_LAMBDA[1]` 两个 section。
   - `VCPI_SAO_LAMBDA_GROUP[0]` 到 `VCPI_SAO_LAMBDA_GROUP[25]` 全部输出。
   - 数组成员缺失 `indices` 字段时脚本以非零退出并报错。

## Validation Scenario H: C 解析器编译与运行 (2026-06-15 新增)

### 前置
- GCC 或 MSVC 可用
- `parse_cmd_cfg_to_vcpi.c` 与 `reg_data.h` 在同一目录

### 编译（GCC 示例）
```bash
gcc -std=c99 -Wall -Wextra -Werror -o parse_cmd_cfg parse_cmd_cfg_to_vcpi.c
```

### 运行
```bash
./parse_cmd_cfg cmd.cfg reg_data.h
```

### 预期结果
- 标准输出打印 `VCPI_PIC_INFO0 = 0xXXXXXXXX` 格式的调试转储。
- 字段名**右对齐**（同 section 内对齐至最长字段名），使用等号分隔。
- 数组成员显示为 `VCPI_QPG_LAMBDA[0] = 0xXXXXXXXX` 格式。
- 最后打印 `API called, first register=0xXXXXXXXX`。
- 退出码为 0。

### 错误场景验证
1. 未知字段测试：在 cmd.cfg 中某 section 添加虚构字段名。预期：非零退出 + stderr 错误信息含 section 名 + 字段名。
2. 重复字段测试：在 cmd.cfg 中同一 section 复制一行字段。预期：非零退出 + stderr 含重复字段名。
3. 缺失 section 测试：删除 cmd.cfg 中某个 section。预期：正常解析，该 section 对应字段为 0。
4. 数组下标越界测试：新增 `VCPI_QPG_LAMBDA[99]` section（超出数组长度）。预期：非零退出 + stderr 含成员名与越界下标。
5. 重复数组 section 测试：复制 `VCPI_QPG_LAMBDA[3]` section 形成两份。预期：非零退出 + stderr 含成员名与重复下标。

## Validation Scenario I: 调试打印格式验证 (2026-06-15 新增)

检查 `print_vcpi_debug_dump` 输出符合以下规则：
1. 字段名在同一 section 内**右对齐**（等号在同列）。
2. 值左对齐。
3. `rsvd` 开头的保留字段不打印。
4. 数组 section 头格式为 `MEMBER[N] = 0xHEX8`。

预期输出片段示例（参见 a.log）：
```
VCPI_PIC_INFO0 = 0x0034FB46
                 ve_frame_type = 2
                   ve_protocol = 1
                      ...
VCPI_QPG_LAMBDA[0] = 0x001292C9
    ve_sqrt_lambda0 = 201
     ve_sel_lambda0 = 4754
```
1. 在 `register_selection.json` 中故意指定不存在寄存器或非法 JSON。
2. 运行脚本。
3. 预期结果:
  - 非零退出。
  - 错误信息包含 JSON 结构或目标定位信息。
  - 不生成不完整 `cmd.cfg`。
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

## Expected Output Snippet (2026-06-12 更新)

```cfg
#======== VCPI_PIC_INFO0 ================
ve_frame_type                   : 0
ve_protocol                     : 2
ve_chroma_format                : 0

#======== VCPI_PIC_SIZE =================
ve_pic_height                   : 2879
ve_pic_width                    : 7615
```

**注意 (minus1 config)**:
- 配置值: `ve_pic_height=2879`, `ve_pic_width=7615`
- 实际值: `2879+1=2880` (2880 % 16 = 0 ✓), `7615+1=7616` (7616 % 16 = 0 ✓)
- **对齐约束应用于实际值**（配置值+1），而非配置值本身
- 配置值可能不对齐（2879 % 16 = 15），但实际值必须对齐

## Validation Record

### 2026-06-11 初始验证

- Scenario A: PASS
  - 命令: `python random_reg_cfg.py --header reg_data.h --select-json register_selection.json --out cmd.cfg`
  - 结果: 成功生成 `cmd.cfg`，仅包含 `enabled=true` 的 `VCPI_PIC_INFO0` 与 `VCPI_PIC_SIZE`。
- Scenario B: PASS
  - 命令: 固定 seed 两次运行，输出 `cmd_seed123_a.cfg` 与 `cmd_seed123_b.cfg`。
  - 结果: `seed_reproducible=True`。
- Scenario C: PASS (旧标准)
  - 结果: `ve_pic_width=1586`、`ve_pic_height=894`，均为 2 对齐且不超过上限。
- Scenario D: PASS
  - 命令: `python random_reg_cfg.py --header reg_data.h --select-json invalid_selection.json --out cmd_invalid.cfg`
  - 结果: 非零退出并输出 `E_SELECTION_SCHEMA_INVALID`。

### 2026-06-12 对齐约束修复验证

- **Verilog 解析修复**: PASS
  - 修复前: `16'd8190` 错误解析为 33168 (十六进制 0x8190)
  - 修复后: 正确解析为 8190 (十进制)
  - 影响字段: VCPI_SRC_MOSAIC_POS 系列约束范围从 [0, 33k+] 修正为 [0, 8k]

- **对齐约束应用**: PASS
  - 测试: 5 个不同种子 (1, 42, 123, 456, 789)
  - 结果示例:
    ```
    Seed 1   : width=5968 (mod16=0), height=2240 (mod16=0)
    Seed 42  : width=5376 (mod16=0), height=5920 (mod16=0)
    Seed 123 : width=7472 (mod16=0), height=64   (mod16=0)
    Seed 456 : width=6048 (mod16=0), height=1568 (mod16=0)
    Seed 789 : width=4592 (mod16=0), height=2240 (mod16=0)
    ```
  - 验证点:
    - ✓ 所有值都是 16 的倍数（max(HEVC:8, H.264:16, JPEG:16) = 16）
    - ✓ 所有值在范围 [63, 8191] 内
    - ✓ 不同种子生成不同值，证明随机性
    - ✓ 同一种子多次运行结果一致，证明可复现性

- **约束统计**: PASS
  - 总字段数: 919
  - 带对齐约束: 138 (15%)
  - 带范围约束: 505 (55%)
  - 带位宽验证: 919 (100%)
  - 位宽验证冲突: 0 (所有约束范围都在位宽限制内)

### 2026-06-15 Phase 9 验证（数组成员 + C 解析器增强）

**环境**: Python 3.x, GCC (C99), Windows PowerShell

- **Scenario G: 数组成员 `indices` 选择 — PASS**
  - 命令: `python random_reg_cfg.py --header reg_data.h --select-json register_selection.json --seed 42 --out cmd.cfg`
  - 结果: 生成 358 个 register groups（含 7 个数组成员全部展开）
  - `VCPI_QPG_LAMBDA[0]...[51]` 各自独立 section，section 头格式 `#================ VCPI_QPG_LAMBDA[N] ====================`
  - 字段右对齐冒号格式：`ve_sqrt_lambda0 : 232`，`ve_sel_lambda0 : 11542`
  - ✓ `"indices":"all"` 正确展开为全部下标

- **Scenario H: C 解析器编译运行 — PASS**
  - 编译: `gcc -std=c99 -Wall -Wextra -Werror -o parse_cmd_cfg parse_cmd_cfg_to_vcpi.c`，EXIT:0，零警告
  - 运行: `.\parse_cmd_cfg.exe cmd.cfg reg_data.h`，EXIT:0
  - 端到端值一致性验证（seed=42）：
    ```
    cmd.cfg:      ve_sqrt_lambda0 : 232,  ve_sel_lambda0 : 11542   (VCPI_QPG_LAMBDA[0])
    C 输出: VCPI_QPG_LAMBDA[0] = 0x002D16E8
                ve_sqrt_lambda0 = 232
                 ve_sel_lambda0 = 11542
    ```
  - ✓ cmd.cfg 与 C 解析输出值完全一致

- **Scenario I: 调试打印格式验证 — PASS**
  - 数组 section 头：`VCPI_QPG_LAMBDA[0] = 0x002D16E8`（格式符合 FR-008c）
  - 字段行：右对齐等号格式，`rsvd` 字段跳过，与 reg_data.h 风格一致
  - ✓ VCPI_QPG_LAMBDA[0], [1], [2], [3] 全部按下标升序输出

### 2026-06-15 增量验证（数组严格失败策略）

- **Compile Recheck — PASS**
  - 命令: `gcc -std=c99 -Wall -Wextra -Werror -o parse_cmd_cfg.exe parse_cmd_cfg_to_vcpi.c`
  - 结果: 编译通过，零警告。

- **Negative Test: 数组下标越界 section — PASS**
  - 输入: `tmp_overflow.cfg` 包含 `VCPI_QPG_LAMBDA[99]`
  - 命令: `parse_cmd_cfg.exe tmp_overflow.cfg reg_data.h`
  - 结果: `EXIT:1`
  - 错误: `Array index 99 out of range for member 'VCPI_QPG_LAMBDA' (len=52)`

- **Negative Test: 重复数组 section — PASS**
  - 输入: `tmp_dupsec.cfg` 两次声明 `VCPI_QPG_LAMBDA[3]`
  - 命令: `parse_cmd_cfg.exe tmp_dupsec.cfg reg_data.h`
  - 结果: `EXIT:1`
  - 错误: `Duplicate array section 'VCPI_QPG_LAMBDA[3]'`

- **Positive Recheck: 正常 cfg 解析 — PASS**
  - 输入: `cmd.cfg`（seed=123 生成）
  - 命令: `parse_cmd_cfg.exe cmd.cfg reg_data.h`
  - 结果: `EXIT:0`
