# logscope

`logscope.py` 是一个只使用 Python 标准库的服务器日志摘要工具。它仅统计完整匹配 `时间戳 级别 [模块] 消息` 格式的行（时间戳为有效的 `YYYY-MM-DD HH:MM:SS` 日期时间，级别为大写字母组成的名称，模块不能为空且不能含空格或方括号，消息不能为空），其他行会跳过。对 `ERROR` 行，消息的第一个词作为错误码。

## 用法

```sh
python3 logscope.py top sample.log
python3 logscope.py trend sample.log
python3 logscope.py window sample.log "2026-10-21 20:00:00" "2026-10-21 21:00:00"
```

- `top` 输出各级别的行数、按数量从多到少排列的 `ERROR` 消息首词（错误码）计数，以及每个错误码首次出现的文件行号。计数相同时按错误码字母顺序排列。
- `trend` 按小时汇总 `ERROR` 数量，并始终输出 `00` 到 `23` 共 24 行，格式为 `HH: 数量`。
- `window` 统计指定时间窗口内的日志，输出级别统计和 `ERROR` 错误码计数。起始时间包含在窗口内，结束时间不包含在窗口内；时间格式为 `YYYY-MM-DD HH:MM:SS`。

三个子命令均逐行流式读取日志；不符合日志格式或时间戳无效的行会跳过。也可以将 `sample.log` 换成其他日志文件路径。
