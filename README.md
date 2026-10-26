# logscope

`logscope.py` answers three questions about structured server logs:

1. **Where are errors concentrated?** `top` reports counts by log level and error code, plus the first line where each error code appears.
2. **Which hours have the most errors?** `trend` aggregates `ERROR` entries by hour.
3. **What happened during a specified time period?** `window` summarizes entries in a time range whose start is inclusive and end is exclusive.

## `top`: error counts and first occurrences

```sh
python3 logscope.py top sample.log
```

Output highlights:

- Counts for each log level.
- `ERROR` counts by error code, ordered from most frequent to least frequent (ties are alphabetical).
- The first file line number for each error code.

## `trend`: hourly error counts

```sh
python3 logscope.py trend sample.log
```

Output highlights:

- One `HH: count` line for each hour from `00` through `23`.
- Each count is the number of `ERROR` entries with a timestamp in that hour.

## `window`: summarize a time range

```sh
python3 logscope.py window sample.log "2026-10-21 20:00:00" "2026-10-21 21:00:00"
```

Provide start and end timestamps in `YYYY-MM-DD HH:MM:SS` format. The start is inclusive and the end is exclusive. The output reports log-level counts and `ERROR` counts by error code for entries in that interval.

## Malformed lines and memory use

Entries that do not match the expected log format, or contain an invalid timestamp, are skipped and counted. Every command ends its output with `Skipped malformed lines: N`, where `N` is the number of skipped entries.

Log entries are parsed one at a time as the file is streamed; the entire log file is not read into memory.

## Requirements

Only Python 3 is required; the tool uses only the Python standard library.

## Tests

Run the test suite with:

```sh
python3 -m unittest
```
