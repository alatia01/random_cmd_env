# Implementation Plan: 寄存器随机配置生成（JSON 选择更新）

**Branch**: `001-register-random-generator` | **Date**: 2026-06-11 | **Spec**: `specs/001-register-random-generator/spec.md`

**Input**: Feature specification from `/specs/001-register-random-generator/spec.md`

## Summary

在现有单脚本基础上升级为“全 `t_reg_vcpi` 寄存器随机引擎 + JSON 参与开关控制”。
脚本运行时输入改为 `reg_data.h + register_selection.json`，不再解析 `random_require.md`。
输出保持 `cmd.cfg` 稳定格式，并保留 seed 可复现。

## Technical Context

**Language/Version**: Python 3.x

**Primary Dependencies**: Python standard library (`re`, `json`, `random`, `argparse`, `pathlib`, `tempfile`, `typing`, `dataclasses`)

**Storage**: N/A (文件 I/O: `reg_data.h`, `register_selection.json`, `cmd.cfg`)

**Testing**: `unittest` + quickstart 命令行校验

**Target Platform**: Windows PowerShell / 通用桌面 Python 运行环境

**Project Type**: 单脚本 CLI 工具

**Performance Goals**: 在 1000 位域规模下 5 秒内完成生成

**Constraints**: 
- 单脚本；标准库-only
- `reg_data.h` 为唯一寄存器定义来源
- 稳定输出顺序；seed 可复现
- 运行时不读取 `random_require.md`
- **约束来源**: `VCPI_FIELD_CONSTRAINTS` 静态字典（从 vcpi.xlsx 一次性提取并硬编码）
  - 包含 919 个字段的约束信息
  - 138 个字段带对齐约束（2/4/8/16 像素对齐）
  - 505 个字段带范围/固定值约束
  - 支持协议特定对齐（HEVC: 8像素, H.264/JPEG: 16像素）

**Scale/Scope**: 覆盖 `t_reg_vcpi` 下全部寄存器，最终随机范围由 JSON 选择文件控制

**Key Implementation Details**:
- **Verilog 数字解析**: 支持 `16'd8190` (十进制), `16'hFF` (十六进制), `4'b1010` (二进制), `4'o7` (八进制)
- **对齐约束应用**: 使用 `pick_aligned(rng, lo, hi, alignment)` 确保生成值符合像素对齐要求
- **多协议对齐处理**: 对于 `{'hevc': 8, 'h264': 16, 'jpeg': 16}` 取最大值 (16) 以满足所有协议
- **位宽验证**: 所有约束范围已验证不超过字段实际位宽 (列 G vs 列 J)
- **minus1 config 处理**: 对标记为"minus1 config"的字段（如 ve_pic_height/width）：
  1. 先按对齐约束生成对齐的实际值 V（如 2880 满足 16 对齐）
  2. 验证 V 在约束范围 [min, max] 内
  3. 存储 V-1 至配置文件（如存储 2879）
  4. 对齐约束应用于**实际值**（配置值+1），而非配置值本身
  5. 确保硬件读取时通过 +1 还原得到满足编解码器对齐要求的实际尺寸

## Constitution Check (Pre-Design Gate)

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Register source compliance: PASS（定义仅来源 `reg_data.h` + `t_reg_vcpi`）。
- Language/runtime compliance: PASS（Python 3 + 标准库）。
- Delivery shape compliance: PASS（单脚本交付）。
- Design compliance: PASS（解析/选择/随机/导出函数职责分离）。
- Quality compliance: PASS（seed 可复现 + JSON 校验 + 稳定输出）。
- Documentation compliance: PASS（复杂逻辑需补充 why 注释）。

## Project Structure

### Documentation (this feature)

```text
specs/001-register-random-generator/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── random-require-rules.md
│   └── cmd-cfg-format.md
└── tasks.md
```

### Source Code (repository root)

```text
random_reg_cfg.py
reg_data.h
register_selection.json
cmd.cfg
tests/
├── test_parser.py
├── test_selection.py
└── test_generation.py
```

**Structure Decision**: 维持单脚本形态；新增 JSON 选择输入文件，不新增框架或多模块主流程。

## Phase 0 Output Reference

- `research.md`：完成“JSON 选择契约、全寄存器覆盖、不解析 random_require.md、错误策略”的决策收敛。

## Phase 1 Design Artifacts

- `data-model.md`：更新为 `RegisterSelection` 实体驱动的模型。
- `contracts/random-require-rules.md`：重定义为 JSON 选择文件契约（沿用文件名，内容更新）。
- `contracts/cmd-cfg-format.md`：保留输出契约并确认稳定顺序。
- `quickstart.md`：更新命令行为 `--select-json` 输入。

## Constitution Check (Post-Design Re-check)

- Register source compliance: PASS（契约与模型均要求从头文件实时解析）。
- Language/runtime compliance: PASS（设计仅依赖标准库 json/re/random）。
- Delivery shape compliance: PASS（仍为单脚本）。
- Design compliance: PASS（新增 JSON 解析但不破坏单一职责分层）。
- Quality compliance: PASS（定义了 JSON 验证、空选择策略、seed 复现）。
- Documentation compliance: PASS（quickstart + contracts 可直接用于验收）。

## Complexity Tracking

无宪法违规项，无需豁免。
