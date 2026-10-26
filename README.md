# logscope

## Three questions this tool answers

- **Where do errors concentrate?** `top` shows counts by log level, counts by ERROR code, and the first occurrence of each ERROR code.
- **Which hour hits hardest?** `trend` shows hourly aggregation of ERROR counts.
- **What happened inside a time range?** `window` summarizes entries from the start timestamp (inclusive) up to the end timestamp (exclusive).

## `top`

```sh
python3 logscope.py top sample.log
```

Shows valid log-line counts by level, ERROR counts grouped by the first word of each ERROR message (the error code), and the source line of the first occurrence of each ERROR code. Code counts are sorted by descending count, with ties alphabetically.

## `trend`

```sh
python3 logscope.py trend sample.log
```

Shows ERROR counts for each hour of the day as `HH: count`, including hours with no errors.

## `window`

```sh
python3 logscope.py window sample.log "2026-10-21 20:00:00" "2026-10-21 21:00:00"
```

Shows valid log-line counts by level and ERROR counts by code in the selected time range. The start is inclusive and the end is exclusive. Timestamps must use `YYYY-MM-DD HH:MM:SS`.

## Notes

- Malformed log lines are skipped and counted. Every command ends with `Skipped malformed lines: N`.
- Parsing streams line by line and never loads the whole file into memory.
- Run the tests with `python3 -m unittest`. The tool requires only Python 3 and the standard library.
