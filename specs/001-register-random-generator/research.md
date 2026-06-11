# Phase 0 Research: 寄存器随机配置生成（JSON 选择更新）

## Decision 1: `reg_data.h` 全寄存器解析策略
- Decision: 保持两阶段解析（结构体定义解析 + `t_reg_vcpi` 成员映射），并将覆盖范围扩展为 `t_reg_vcpi` 下全部寄存器。
- Rationale: 满足“全寄存器随机能力”需求，同时保持与头文件同步。
- Alternatives considered:
  - 仅维护白名单寄存器: 不满足全覆盖。
  - 手工映射配置文件: 与单一事实来源冲突。

## Decision 2: JSON 选择文件作为唯一运行时筛选输入
- Decision: 新增 `register_selection.json` 作为运行时输入，指定寄存器是否参与随机；脚本不读取 `random_require.md`。
- Rationale: 用户明确要求运行阶段通过 JSON 控制参与范围，`random_require.md` 仅用于开发规则说明。
- Alternatives considered:
  - 继续解析 `random_require.md`: 与更新要求冲突。
  - CLI 直接传大量寄存器名: 可维护性与可复用性较差。

## Decision 3: JSON 契约的最小结构
- Decision: 定义稳定 JSON 结构（`registers` 列表，元素包含 `name` 与 `enabled`），并允许附加元数据字段。
- Rationale: 结构简单，易于手工编写与程序校验。
- Alternatives considered:
  - 扁平键值 map: 不便扩展字段（例如优先级、备注）。
  - 复杂层级嵌套: 增加解析与使用成本。

## Decision 4: 随机与复现机制
- Decision: 使用 `random.Random(seed)` 实例化 RNG，且同一运行内共享随机源。
- Rationale: 可复现且符合标准库-only约束。
- Alternatives considered:
  - `secrets`: 不强调可复现。
  - 全局随机状态: 易受外部干扰。

## Decision 5: 业务约束保留策略
- Decision: 对 `VCPI_PIC_SIZE.ve_pic_width/height` 保留 2 对齐与 1080p 上限约束，无论是否全寄存器模式。
- Rationale: 这是明确业务约束，不应因输入方式变更而丢失。
- Alternatives considered:
  - 仅按位宽上限: 无法保证业务有效分辨率。

## Decision 6: `cmd.cfg` 输出契约
- Decision: 保持分组头 + 键值行格式，顺序由 `t_reg_vcpi` 与字段定义顺序确定。
- Rationale: 与现有下游兼容，便于差异比对。
- Alternatives considered:
  - JSON 输出: 可读性/兼容性不足。

## Decision 7: 错误处理策略
- Decision: 对 JSON 文件缺失/格式非法/寄存器不存在/全部禁用采用 fail-fast（或按契约输出空结果），并提供清晰错误码。
- Rationale: 工具链自动化需要可诊断与可预期行为。
- Alternatives considered:
  - 静默忽略非法项: 风险不可控。
