# Contract: cmd.cfg 输出格式（v1）

## Purpose
定义生成脚本输出 `cmd.cfg` 的稳定文本格式，供下游工具直接消费。

## File Encoding
- UTF-8
- LF 或 CRLF 均可，但同一文件内应一致。

## Layout
1. 每个寄存器一个分组头。
2. 分组头格式:
   `#======== <REGISTER_NAME> ================`
3. 分组内每行一个键值:
   `<field_name><padding>: <decimal_value>`
4. 寄存器组之间空一行。

## Ordering
- 寄存器顺序: 按在 `t_reg_vcpi` 中出现顺序。
- 位域顺序: 按对应结构体中定义顺序。

## Example
```cfg
#======== VCPI_PIC_INFO0 ================
ve_frame_type                    : 1
ve_protocol                      : 3
ve_chroma_format                 : 3
ve_enc_bitdepth                  : 0

#======== VCPI_PIC_SIZE =================
ve_pic_height                    : 578
ve_pic_width                     : 376
```

## Value Constraints
- 所有值必须为十进制非负整数。
- 所有值必须满足位宽上限与规则约束。

## Error Handling
- 发生规则校验错误时不得写出不完整 `cmd.cfg`。
- 脚本应以非零状态退出并输出错误原因。
