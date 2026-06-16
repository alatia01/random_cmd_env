# Implementation Plan: 寄存器随机配置生成（JSON 选择更新）

**Branch**: `001-register-random-generator` | **Date**: 2026-06-11 | **Spec**: `specs/001-register-random-generator/spec.md`

**Input**: Feature specification from `/specs/001-register-random-generator/spec.md`

## Summary

在现有单脚本基础上升级为“全 `t_reg_vcpi` 寄存器随机引擎 + JSON 参与开关控制”。
脚本运行时输入改为 `reg_data.h + register_selection.json`，不再解析 `random_require.md`。
输出保持 `cmd.cfg` 稳定格式，并保留 seed 可复现。

## Technical Context

**Language/Version**: Python 3.x（生成器）；C99/C11（解析器）

**Primary Dependencies**: Python standard library (`re`, `json`, `random`, `argparse`, `pathlib`, `tempfile`, `typing`, `dataclasses`)；标准 C 库（`stdio.h`, `stdlib.h`, `string.h`, `ctype.h`, `stdint.h`）

**Storage**: N/A (文件 I/O: `reg_data.h`, `register_selection.json`, `cmd.cfg`)

**Testing**: `unittest` + quickstart 命令行校验；C 编译检查 (`gcc -std=c99 -Wall -Wextra -Werror`)

**Target Platform**: Windows PowerShell / 通用桌面 Python + C 运行环境

**Project Type**: 双组件 CLI 工具链（Python 生成器 + C 解析器）

**Performance Goals**: 在 1000 位域规模下 5 秒内完成 Python 生成；C 解析器单次运行 < 100ms

**Constraints**: 
- Python 单脚本；C 单源文件；标准库-only（各自语言）
- `reg_data.h` 为唯一寄存器定义来源（Python 和 C 均运行时解析）
- 稳定输出顺序；seed 可复现
- 运行时不读取 `random_require.md`
- **约束来源**: `VCPI_FIELD_CONSTRAINTS` 静态字典（从 vcpi.xlsx 一次性提取并硬编码）
  - 包含 919 个字段的约束信息
  - 138 个字段带对齐约束（2/4/8/16 像素对齐）
  - 505 个字段带范围/固定值约束
  - 支持协议特定对齐（HEVC: 8像素, H.264/JPEG: 16像素）
- **cfg 分隔符规范**: Python 写冒号（`field : value`）；C 解析器读冒号和等号均兼容；调试打印用等号（右对齐）
- **数组成员**: JSON 中数组类型成员必须声明 `indices`；cfg 中数组 section 头格式为 `MEMBER[N]`
- **数组解析严格性**: 数组 section 下标越界（`N >= array_len`）或重复数组 section（相同 `MEMBER[N]`）均立即失败并返回非零

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

- Register source compliance: PASS（定义仅来源 `reg_data.h` + `t_reg_vcpi`，Python 和 C 均运行时解析）。
- Language/runtime compliance: PASS（Python 3 + 标准库；C99/C11 + 标准 C 库；宪法 v1.1.0 多语言协同原则）。
- Delivery shape compliance: PASS（Python 单 `.py`，C 单 `.c`，符合宪法 v1.1.0 更新后的 CA-003）。
- Design compliance: PASS（解析/选择/随机/导出/C 解析/C 打印函数职责分离）。
- Quality compliance: PASS（seed 可复现 + JSON 校验 + 稳定输出 + C 编译无警告）。
- Documentation compliance: PASS（复杂逻辑需补充 why 注释，包括 C 内存管理路径）。

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
random_reg_cfg.py           # Python 生成器（单脚本）
parse_cmd_cfg_to_vcpi.c     # C 解析器（单源文件）
reg_data.h                  # 共享寄存器定义（单一事实来源）
register_selection.json     # 运行时选择文件
cmd.cfg                     # Python 生成器输出 / C 解析器输入
```

**Structure Decision**: Python 维持单脚本形态；C 解析器为独立单源文件，共享 `reg_data.h`；两者通过 `cmd.cfg` 文本接口解耦。

## Phase 0 Output Reference

- `research.md`：完成“JSON 选择契约、全寄存器覆盖、不解析 random_require.md、错误策略”的决策收敛。- **2026-06-15 新增决策 12-18**：C 解析器多语言协同策略、cfg 分隔符三段式规范、数组成员 JSON/cfg 格式、C 错误策略、API 传参规范、数组越界与重复 section 的 fail-fast 规则。
## Phase 1 Design Artifacts

- `data-model.md`：更新为 `RegisterSelection`（含 `indices` 字段）+ `ArrayMemberSection` 新实体。
- `contracts/cmd-cfg-format.md`：v2 更新，定义分隔符三段式规范、数组 `[N]` section 头格式、调试打印格式、C 解析器错误策略表。
- `contracts/random-require-rules.md`：JSON 选择文件契约（含 `indices` 规范）。
- `quickstart.md`：新增 Scenario G（数组成员 JSON indices）、H（C 解析器编译运行）、I（调试打印格式验证）。

## Phase 1 Implementation Plan (2026-06-15)

### 已完成（Phases 1-8）
- Python 生成器：头文件解析、JSON 选择、随机生成、cfg 输出、对齐约束、minus1 config。
- C 解析器基础实现（parse_cmd_cfg_to_vcpi.c）：头文件解析、cfg 解析、调试打印（等号右对齐）。

### 待实现（Phase 9 — 2026-06-15 澄清驱动）

**T060: Python 生成器 — 数组成员 indices 校验**
- JSON 验证层：对数组类型成员检查 `indices` 字段存在性（缺失 → 快速失败）
- 验证下标范围（越界 → 快速失败）
- `"indices":"all"` 展开为 `[0, ..., array_len-1]`

**T061: Python 生成器 — 数组成员 cfg 输出格式**
- `format_cfg` 对数组成员每个下标输出独立 section，section 头为 `MEMBER[N]`
- 下标按升序排列

**T062: register_selection.json — 补充 indices 字段**
- 为 `t_reg_vcpi` 中全部数组成员条目添加 `"indices":"all"` 或精细下标列表
- 受影响成员：`VCPI_SRC_MOSAIC_POS[16]`、`VCPI_SRC_MOSAIC_SIZE[16]`、`VCPI_ROI_POS[16]`、`VCPI_ROI_SIZE[16]`、`VCPI_ROI_VALUE[16]`、`VCPI_QPG_LAMBDA[52]`、`VCPI_SAO_LAMBDA_GROUP[26]`

**T063: C 解析器 — 重复字段检测**
- 在 `parse_cmd_cfg_to_vcpi` 中增加 per-section 已见字段位集（或哈希表）
- 重复字段时立即返回 -1 并输出 stderr 信息

**T064: C 解析器 — 按值 API 包装**
- 新增 `vcpi_submit_api_by_value(t_reg_vcpi vcpi)` 薄包装，内部调用 `vcpi_submit_api(&vcpi)`

**T065: C 解析器 — `[N]`/`[all]` section 头解析增强**
- 验证 `extract_section_name` 正确提取 `MEMBER[N]` 并将 N 映射到数组槽
- 支持 `[all]` 语法遍历整个数组
- 对 `N >= array_len` 的 section 执行立即失败并输出成员名+下标

**T065b: C 解析器 — 重复数组 section 检测**
- 在解析过程中记录每个数组成员已见下标
- 相同 `MEMBER[N]` 再次出现时立即失败并输出成员名+下标

**T066: 验证与文档同步**
- 编译验证：`gcc -std=c99 -Wall -Wextra -Werror`
- 端到端集成测试：Python 生成含数组 section 的 cfg → C 解析 → 验证 VCPI_QPG_LAMBDA[0] 值匹配
- 更新 quickstart.md 验证记录

## Constitution Check (Post-Design Re-check)

- Register source compliance: PASS（Python 和 C 均运行时解析 `reg_data.h`，无手工复制）。
- Language/runtime compliance: PASS（Python 标准库 + C 标准库；宪法 v1.1.0 多语言协同原则 PASS）。
- Delivery shape compliance: PASS（Python 单 `.py`，C 单 `.c`）。
- Design compliance: PASS（T060-T066 各任务职责单一）。
- Quality compliance: PASS（编译无警告 + 集成测试 + seed 复现 + 数组越界/重复 section fail-fast）。
- Documentation compliance: PASS（C 重复检测、内存管理路径需补充 why 注释）。

## Complexity Tracking

无宪法违规项，无需豁免。
