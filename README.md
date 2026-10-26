# logscope

`logscope.py` summarizes structured server logs using only the Python standard library. A line is counted only when it fully matches `YYYY-MM-DD HH:MM:SS LEVEL [module] message`; malformed lines are skipped and counted. Each command prints a final `Skipped malformed lines: N` line.

Run:

```sh
python3 logscope.py top sample.log
```

The `top` report shows valid line counts by level, ERROR counts by the first message word (error code), sorted by descending count (ties alphabetically), and the source line of each code's first ERROR occurrence.

Show ERROR counts for every hour (including hours with no errors):

```sh
python3 logscope.py trend sample.log
```

Each line is printed as `HH: count`, using the hour from each valid log entry's timestamp. Parsing is streaming; malformed lines are skipped and counted in the final `Skipped malformed lines: N` line.

Summarize entries in a time window with start inclusive and end exclusive:

```sh
python3 logscope.py window sample.log "2026-10-21 20:00:00" "2026-10-21 21:00:00"
```

The `window` report shows valid line counts by level and ERROR counts grouped by the first message word (error code), sorted by descending count (ties alphabetically). Both timestamps must use `YYYY-MM-DD HH:MM:SS`; malformed log lines are skipped and counted in the final `Skipped malformed lines: N` line.
