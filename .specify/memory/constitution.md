<!--
Sync Impact Report
- Version change: 1.0.0 -> 1.1.0
- Modified principles:
	- II. Python 3 + 标准库优先 -> II. 标准库优先与多语言协同
	- III. 单脚本交付与函数单一职责 -> 澄清适用于各语言组件
	- V. 注释与可维护性为强约束 -> 扩展至 C 语言风格
- Added sections:
	- 技术与实现约束：新增 Python 生成器、C 解析器、接口契约三个子章节
	- Changelog：版本历史记录
- Removed sections:
	- 无
- Templates requiring updates:
	- ✅ .specify/templates/plan-template.md (Constitution Check 已更新语言合规检查)
	- ✅ .specify/templates/spec-template.md (无需更新，用户场景与语言无关)
	- ✅ .specify/templates/tasks-template.md (无需更新，任务分解与语言无关)
	- ✅ .github/copilot-instructions.md (无需更新，仅引用 plan.md)
- Follow-up TODOs:
	- 为 C 解析器添加编译验证脚本（make/CMakeLists.txt）
	- 添加集成测试脚本（Python 生成 → C 解析 → diff 验证）
-->
-->

# Random Register Generator Constitution

## Core Principles

### I. 寄存器定义单一事实来源
所有位域定义 MUST 以 `reg_data.h` 中 `t_reg_vcpi` 及其关联结构体为唯一事实来源。
生成逻辑不得手工复制或硬编码位宽、偏移和字段语义；若解析与头文件冲突，
必须以头文件为准并修复解析实现。Rationale: 防止规格漂移导致随机数据无效。

### II. 标准库优先与多语言协同
Python 组件 MUST 使用 Python 3 且仅依赖标准库。C 组件 MUST 使用 C99/C11 标准
且仅依赖标准 C 库（libc）。不得引入大型框架或第三方运行时依赖。
Python 生成器与 C 解析器通过 cmd.cfg 文本格式解耦，两者可独立编译和部署。
Rationale: 降低部署复杂度，保证工具链在受限环境可直接运行；Python 负责生成，
C 负责高性能解析和集成到下游系统。

### III. 单脚本交付与函数单一职责
Python 生产代码 MUST 以单一脚本文件交付（random_reg_cfg.py）。C 解析器 MUST 以
单一源文件交付（parse_cmd_cfg_to_vcpi.c），可包含必要的头文件引用（reg_data.h）。
每个函数 MUST 仅承担一个明确职责，输入输出边界清晰，禁止在单函数中混合解析、
随机生成、格式化与 I/O 副作用。Rationale: 简化审阅、调试与后续移植；
单文件约束不妨碍跨语言协同。

### IV. 可复现实验与可验证输出
随机生成流程 MUST 支持可复现（例如显式随机种子）并提供可验证输出。
至少应支持一种结构化输出格式（如 JSON 文本）用于自动比对。
Rationale: 便于回归测试与问题复现。

### V. 注释与可维护性为强约束
Python 代码 MUST 遵循 PEP8。C 代码 MUST 遵循一致的命名与缩进风格（snake_case
函数名，4 空格缩进）。对非直观逻辑（位域解析、边界裁剪、随机策略、字符串解析、
内存管理）MUST 提供完整且准确的注释，注释需解释"为什么"而不仅是"做什么"。
Rationale: 该项目是底层寄存器工具，长期维护依赖高可读性；C 代码因手动内存管理
更需注释说明生命周期。

## 技术与实现约束

### Python 生成器（random_reg_cfg.py）
- 语言版本: Python 3.x。
- 依赖策略: 仅标准库（re, json, random, argparse, pathlib 等）。
- 输入规范: 从 `reg_data.h` 中提取 `t_reg_vcpi` 结构层级、字段位宽与名称。
- 输出规范: 生成 cmd.cfg 文本文件，格式为 `field_name : value` 或 `field_name = value`，
  包含寄存器名、位域名、随机值及位宽信息，便于验证和解析。
- 异常处理: 对解析失败、字段不合法、输入文件缺失 MUST 给出明确错误信息。

### C 解析器（parse_cmd_cfg_to_vcpi.c）
- 语言版本: C99 或 C11。
- 编译器: GCC/Clang/MSVC，MUST 支持标准 C 编译选项（-std=c99, -Wall, -Wextra）。
- 依赖策略: 仅标准 C 库（stdio.h, stdlib.h, string.h, ctype.h, stdint.h）。
- 输入规范: 读取 cmd.cfg 文本文件并解析为 `t_reg_vcpi` 结构体实例。
- 输出规范: 按指定格式输出结构体字段，支持人类可读格式和机器可解析格式。
- 内存管理: MUST 使用 malloc/free 手动管理堆内存，避免内存泄漏，所有分配失败
  MUST 返回错误码。
- 错误处理: 对解析失败、格式非法、文件缺失 MUST 返回非零退出码并输出错误诊断
  到 stderr，不得 abort() 或 segfault。

### 接口契约（cmd.cfg 格式）
- 格式: 文本文件，UTF-8 编码，行分隔符 LF 或 CRLF。
- 语法: 每行为 `field_name : value` 或 `field_name = value`，注释行以 `#` 开头。
- 兼容性: Python 生成器与 C 解析器 MUST 保持格式兼容，变更需双向回归测试。

## 研发流程与质量门禁

- 变更前 MUST 在 spec 或 plan 中明确本次影响的寄存器范围与输出格式。
- 实现阶段 MUST 保持单脚本约束（Python 单.py，C 单.c），不得拆分为多模块主逻辑。
- 验证阶段 MUST 至少执行:
	- Python: 语法有效性检查（python -m py_compile）。
	- C: 编译检查（gcc -std=c99 -Wall -Wextra -Werror），无警告无错误。
	- 固定 seed 的可复现性检查（Python 生成器）。
	- 示例寄存器字段范围检查（随机值不超过位宽上限）。
	- 集成测试: Python 生成 cmd.cfg → C 解析 → 验证结果一致性。
- 评审阶段 MUST 核对:
	- 是否仍以 `reg_data.h` 为唯一定义来源。
	- 是否引入非标准库依赖（Python 和 C 均检查）。
	- 函数是否遵循单一职责与注释要求。
	- C 代码是否存在内存泄漏风险（通过代码审查或 valgrind）。

## Governance

本宪法优先级高于仓库内其他流程说明。修订流程 MUST 包含: 变更动机、受影响原则、
模板同步结果与迁移说明。版本管理遵循语义化规则:
- MAJOR: 移除或重定义核心原则，导致既有流程不兼容。
- MINOR: 新增原则/章节或扩展强制门禁。
- PATCH: 术语澄清、文字修订、无语义变化的整理。

每次 PR/评审 MUST 执行合规检查，至少覆盖原则 II-V 与质量门禁。若临时豁免，
必须记录原因、范围与失效日期。

**Version**: 1.1.0 | **Ratified**: 2026-06-11 | **Last Amended**: 2026-06-12

---

## Changelog

### 1.1.0 (2026-06-12)
**Type**: MINOR - 新增 C 语言解析器支持

**变更动机**: 
项目需要支持 C 语言程序解析生成的 cmd.cfg 文件，将配置数据组装为 `t_reg_vcpi`
结构体并传递给下游 API。这扩展了工具链的适用范围，使其可集成到 C/C++ 项目中。

**修改内容**:
- **原则 II**: 从"Python 3 + 标准库优先"扩展为"标准库优先与多语言协同"，
  明确 Python 和 C 各自的语言版本和依赖约束。
- **原则 III**: 澄清"单脚本交付"适用于各语言组件（Python 单.py，C 单.c），
  不妨碍跨语言协同。
- **原则 V**: 扩展注释与可维护性要求至 C 代码，要求遵循一致风格和内存管理注释。
- **技术约束**: 新增"C 解析器"和"接口契约"章节，定义 C 语言编译器、内存管理、
  错误处理规范，以及 cmd.cfg 格式契约。
- **质量门禁**: 新增 C 编译检查、集成测试（Python 生成 → C 解析）和内存泄漏检查。

**受影响组件**:
- 新增: `parse_cmd_cfg_to_vcpi.c` (C 解析器实现)
- 保持: `random_reg_cfg.py` (Python 生成器，无变化)
- 共享: `reg_data.h` (单一事实来源，两语言均引用)
- 接口: `cmd.cfg` (Python 写，C 读)

**模板同步需求**:
- `.specify/templates/plan-template.md`: 更新 Constitution Check 的语言合规检查，
  从"Python 3 only"改为"Python 3 for generator, C99/C11 for parser"。

**迁移说明**:
- 现有 Python 生成器无需修改，保持向后兼容。
- C 解析器为可选组件，不影响纯 Python 使用场景。
- cmd.cfg 格式保持稳定，支持 `:` 和 `=` 两种分隔符。

### 1.0.0 (2026-06-11)
**Type**: MAJOR - 初始宪法发布

**核心原则**:
- I. 寄存器定义单一事实来源
- II. Python 3 + 标准库优先
- III. 单脚本交付与函数单一职责
- IV. 可复现实验与可验证输出
- V. 注释与可维护性为强约束
