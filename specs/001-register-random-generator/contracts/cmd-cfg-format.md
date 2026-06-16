# Contract: cmd.cfg 输出格式（v2 — 2026-06-15 更新）

## Purpose
定义生成脚本输出 `cmd.cfg` 的稳定文本格式，供下游 C 解析器与工具链直接消费。

## File Encoding
- UTF-8
- LF 或 CRLF 均可，但同一文件内应一致。

## 分隔符规范（三段式）

| 角色 | 分隔符 | 说明 |
|------|--------|------|
| Python 生成器（写） | `field : value`（冒号+空格） | 规范输出，向后兼容 |
| C 解析器（读） | `:` 或 `=` 均接受 | 解析时两种格式均合法 |
| `print_vcpi_debug_dump`（打印） | `field = value`（等号） | 右对齐字段名，与 reg_data.h 风格一致 |

## Layout — 非数组成员

1. section 头：`#================ <REGISTER_NAME> ====================`
2. 每行一个字段：`<field_name padded right-aligned> : <decimal_value>`（Python 写）
3. section 间空一行。

## Layout — 数组成员（2026-06-15 新增）

对 `t_reg_vcpi` 中类型为结构体数组的成员（如 `VCPI_QPG_LAMBDA[52]`），每个启用下标独立输出一个 section：

1. section 头：`#================ <MEMBER_NAME>[<N>] ====================`（`N` 为十进制整数）
2. 字段行格式同非数组成员。
3. 下标按升序排列。

## Ordering
- 成员顺序: 按在 `t_reg_vcpi` 中出现顺序。
- 数组成员各下标按升序紧跟当前成员位置。
- 位域顺序: 按对应结构体中定义顺序。

## 调试打印格式（print_vcpi_debug_dump）

```
VCPI_PIC_INFO0 = 0x0034FB46
                     ve_frame_type = 2
                       ve_protocol = 1
                  ve_chroma_format = 0
ve_direct_spatial_mv_pred_flag = 0

VCPI_QPG_LAMBDA[0] = 0x001292C9
    ve_sqrt_lambda0 = 201
     ve_sel_lambda0 = 4754

VCPI_QPG_LAMBDA[1] = 0x00000000
    ve_sqrt_lambda0 = 0
     ve_sel_lambda0 = 0
```

规则：
- 寄存器/成员行：`{MEMBER_NAME}[N] = 0x{HEX8}`（无对齐）
- 字段行：字段名在同 section 内右对齐至最长字段名宽度，等号分隔，值左对齐
- `rsvd` 开头的保留字段跳过不打印

## Example — Python 生成器写出格式（冒号）

```cfg
#================ VCPI_PIC_INFO0 ====================
                 ve_frame_type : 1
                   ve_protocol : 3
              ve_chroma_format : 3

#================ VCPI_QPG_LAMBDA[0] ====================
    ve_sqrt_lambda0 : 201
     ve_sel_lambda0 : 4754

#================ VCPI_QPG_LAMBDA[1] ====================
    ve_sqrt_lambda0 : 0
     ve_sel_lambda0 : 0
```

## C 解析器 section 头解析规则

- `#` 开头行为 section 头，提取其中的大写标识符（或 `MEMBER[N]` / `MEMBER[all]`）。
- `[N]`：`N` 为十进制非负整数，路由到数组第 N 个元素。
- `[all]`：遍历整个数组，逐下标赋值（用于手写 cfg 场景）。
- `[X]` 中 X 为其他内容：跳过该行，不终止解析。

## C 解析器错误策略

| 情形 | 行为 |
|------|------|
| 未知字段 | 立即失败（非零退出），stderr 输出 section + 字段名 |
| 同 section 内重复字段 | 立即失败，stderr 输出 section + 字段名 |
| 缺失 section/字段 | 保留 0，继续解析 |
| 数组下标越界 | 立即失败，stderr 输出成员名 + 下标 |
| 重复数组 section（相同 `MEMBER[N]`） | 立即失败，stderr 输出成员名 + 下标 |

## Value Constraints
- 所有值必须为十进制非负整数。
- 所有值必须满足位宽上限与规则约束（在 Python 生成阶段保证）。

## Error Handling
- Python 生成器发生规则校验错误时不得写出不完整 `cmd.cfg`，以非零状态退出并输出错误原因。
