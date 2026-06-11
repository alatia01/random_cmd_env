<!--
Sync Impact Report
- Version change: 0.0.0 -> 1.0.0
- Modified principles:
	- Template Principle 1 -> I. 寄存器定义单一事实来源
	- Template Principle 2 -> II. Python 3 + 标准库优先
	- Template Principle 3 -> III. 单脚本交付与函数单一职责
	- Template Principle 4 -> IV. 可复现实验与可验证输出
	- Template Principle 5 -> V. 注释与可维护性为强约束
- Added sections:
	- 技术与实现约束
	- 研发流程与质量门禁
- Removed sections:
	- 无
- Templates requiring updates:
	- ✅ .specify/templates/plan-template.md
	- ✅ .specify/templates/spec-template.md
	- ✅ .specify/templates/tasks-template.md
	- ⚠ pending: .specify/templates/commands/*.md (目录不存在，无需更新)
	- ✅ .github/copilot-instructions.md (已核对，无需改动)
- Follow-up TODOs:
	- 无
-->

# Random Register Generator Constitution

## Core Principles

### I. 寄存器定义单一事实来源
所有位域定义 MUST 以 `reg_data.h` 中 `t_reg_vcpi` 及其关联结构体为唯一事实来源。
生成逻辑不得手工复制或硬编码位宽、偏移和字段语义；若解析与头文件冲突，
必须以头文件为准并修复解析实现。Rationale: 防止规格漂移导致随机数据无效。

### II. Python 3 + 标准库优先
所有实现 MUST 使用 Python 3，并且 MUST 仅依赖标准库。不得引入大型框架或第三方
运行时依赖。Rationale: 降低部署复杂度，保证工具在受限环境可直接运行。

### III. 单脚本交付与函数单一职责
生产代码 MUST 以单一脚本文件交付。每个函数 MUST 仅承担一个明确职责，输入输出
边界清晰，禁止在单函数中混合解析、随机生成、格式化与 I/O 副作用。Rationale:
简化审阅、调试与后续移植。

### IV. 可复现实验与可验证输出
随机生成流程 MUST 支持可复现（例如显式随机种子）并提供可验证输出。
至少应支持一种结构化输出格式（如 JSON 文本）用于自动比对。
Rationale: 便于回归测试与问题复现。

### V. 注释与可维护性为强约束
代码 MUST 遵循 PEP8。对非直观逻辑（位域解析、边界裁剪、随机策略）
MUST 提供完整且准确的注释，注释需解释“为什么”而不仅是“做什么”。
Rationale: 该项目是底层寄存器工具，长期维护依赖高可读性。

## 技术与实现约束

- 语言版本: Python 3.x。
- 依赖策略: 仅标准库，禁止引入大型框架。
- 输入规范: 从 `reg_data.h` 中提取 `t_reg_vcpi` 结构层级、字段位宽与名称。
- 输出规范: 生成结果应包含寄存器名、位域名、随机值及位宽信息，便于验证。
- 异常处理: 对解析失败、字段不合法、输入文件缺失 MUST 给出明确错误信息。

## 研发流程与质量门禁

- 变更前 MUST 在 spec 或 plan 中明确本次影响的寄存器范围与输出格式。
- 实现阶段 MUST 保持单脚本约束，不得拆分为多模块主逻辑。
- 验证阶段 MUST 至少执行:
	- 语法有效性检查。
	- 固定 seed 的可复现性检查。
	- 示例寄存器字段范围检查（随机值不超过位宽上限）。
- 评审阶段 MUST 核对:
	- 是否仍以 `reg_data.h` 为唯一定义来源。
	- 是否引入非标准库依赖。
	- 函数是否遵循单一职责与注释要求。

## Governance

本宪法优先级高于仓库内其他流程说明。修订流程 MUST 包含: 变更动机、受影响原则、
模板同步结果与迁移说明。版本管理遵循语义化规则:
- MAJOR: 移除或重定义核心原则，导致既有流程不兼容。
- MINOR: 新增原则/章节或扩展强制门禁。
- PATCH: 术语澄清、文字修订、无语义变化的整理。

每次 PR/评审 MUST 执行合规检查，至少覆盖原则 II-V 与质量门禁。若临时豁免，
必须记录原因、范围与失效日期。

**Version**: 1.0.0 | **Ratified**: 2026-06-11 | **Last Amended**: 2026-06-11
