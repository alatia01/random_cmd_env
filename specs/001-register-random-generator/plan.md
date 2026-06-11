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

**Constraints**: 单脚本；标准库-only；`reg_data.h` 为唯一寄存器定义来源；稳定输出顺序；seed 可复现；运行时不读取 `random_require.md`

**Scale/Scope**: 覆盖 `t_reg_vcpi` 下全部寄存器，最终随机范围由 JSON 选择文件控制

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
