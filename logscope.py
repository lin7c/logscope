#!/usr/bin/env python3
"""Analyze structured server logs."""

import argparse
from collections import Counter
from datetime import datetime
import re
import sys

# Timestamp, uppercase level, [module], then a non-empty message. The first
# message token is the error code for ERROR records.
LOG_LINE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"([A-Z]+) +\[[^\]\s]+\] +\S(?:.*\S)?$"
)
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def analyze(path):
    levels = Counter()
    errors = Counter()
    first_seen = {}
    skipped = 0
    with open(path, encoding="utf-8") as log_file:
        for line_number, raw_line in enumerate(log_file, 1):
            line = raw_line.rstrip("\r\n")
            match = LOG_LINE.fullmatch(line)
            if match is None:
                skipped += 1
                continue
            try:
                datetime.strptime(match.group(1), TIMESTAMP_FORMAT)
            except ValueError:
                skipped += 1
                continue
            level = match.group(2)
            levels[level] += 1
            if level == "ERROR":
                # The format's final message starts after the closing module
                # bracket. Split at that delimiter to get its first token.
                message = line.split("]", 1)[1].strip()
                code = message.split(None, 1)[0]
                errors[code] += 1
                first_seen.setdefault(code, line_number)
    return levels, errors, first_seen, skipped


def iter_records(path):
    """Yield valid (timestamp, level, error_code) records one line at a time."""
    with open(path, encoding="utf-8") as log_file:
        for raw_line in log_file:
            line = raw_line.rstrip("\r\n")
            match = LOG_LINE.fullmatch(line)
            if match is None:
                continue
            try:
                timestamp = datetime.strptime(match.group(1), TIMESTAMP_FORMAT)
            except ValueError:
                continue
            level = match.group(2)
            error_code = None
            if level == "ERROR":
                message = line.split("]", 1)[1].strip()
                error_code = message.split(None, 1)[0]
            yield timestamp, level, error_code


def trend(path):
    error_counts = [0] * 24
    skipped = 0
    with open(path, encoding="utf-8") as log_file:
        for raw_line in log_file:
            line = raw_line.rstrip("\r\n")
            match = LOG_LINE.fullmatch(line)
            if match is None:
                skipped += 1
                continue
            try:
                timestamp = datetime.strptime(match.group(1), TIMESTAMP_FORMAT)
            except ValueError:
                skipped += 1
                continue
            if match.group(2) == "ERROR":
                error_counts[timestamp.hour] += 1
    return error_counts, skipped


def window(path, start, end):
    levels = Counter()
    errors = Counter()
    skipped = 0
    with open(path, encoding="utf-8") as log_file:
        for raw_line in log_file:
            line = raw_line.rstrip("\r\n")
            match = LOG_LINE.fullmatch(line)
            if match is None:
                skipped += 1
                continue
            try:
                timestamp = datetime.strptime(match.group(1), TIMESTAMP_FORMAT)
            except ValueError:
                skipped += 1
                continue
            level = match.group(2)
            if start <= timestamp < end:
                levels[level] += 1
                if level == "ERROR":
                    message = line.split("]", 1)[1].strip()
                    errors[message.split(None, 1)[0]] += 1
    return levels, errors, skipped


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Summarize structured server logs.",
        epilog=(
            "Three questions this tool answers:\n"
            "  top: Where are errors concentrated? Counts by level and error code, "
            "and the first line where each error code appears.\n"
            "  trend: During which time period are errors most severe? Aggregated by hour.\n"
            "  window: What happened during a specified time period? Start is inclusive; end is exclusive.\n"
            "\n"
            "Examples:\n"
            "  python3 logscope.py top sample.log\n"
            "  python3 logscope.py trend sample.log\n"
            "  python3 logscope.py window sample.log \"2026-10-21 20:00:00\" \"2026-10-21 21:00:00\""
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    top_parser = subparsers.add_parser(
        "top",
        help="show level and ERROR summaries",
        description=(
            "Show counts by log level and ERROR code, including the first occurrence "
            "(line number) of each ERROR code."
        ),
    )
    top_parser.add_argument("logfile", help="path to the log file")
    trend_parser = subparsers.add_parser(
        "trend",
        help="show hourly ERROR counts",
        description="Show ERROR counts aggregated hourly across the log.",
    )
    trend_parser.add_argument("logfile", help="path to the log file")
    window_parser = subparsers.add_parser(
        "window",
        help="summarize a time window",
        description=(
            "Summarize log records in the specified time window. The start is "
            "inclusive and the end is exclusive."
        ),
    )
    window_parser.add_argument("logfile", help="path to the log file")
    window_parser.add_argument("start", help="window start (YYYY-MM-DD HH:MM:SS)")
    window_parser.add_argument("end", help="window end, exclusive (YYYY-MM-DD HH:MM:SS)")
    args = parser.parse_args(argv)

    if args.command == "window":
        try:
            start = datetime.strptime(args.start, TIMESTAMP_FORMAT)
            end = datetime.strptime(args.end, TIMESTAMP_FORMAT)
        except ValueError:
            parser.error("window boundaries must use YYYY-MM-DD HH:MM:SS")
        if end <= start:
            parser.error("window end must be later than start")

    try:
        if args.command == "top":
            levels, errors, first_seen, skipped = analyze(args.logfile)
        elif args.command == "trend":
            error_counts, skipped = trend(args.logfile)
        else:
            levels, errors, skipped = window(args.logfile, start, end)
    except (OSError, UnicodeError) as exc:
        print(f"logscope: {exc}", file=sys.stderr)
        return 2

    if args.command == "top":
        print("Level counts:")
        for level in sorted(levels):
            print(f"  {level}: {levels[level]}")
        print("\nERROR counts by code:")
        for code, count in sorted(errors.items(), key=lambda item: (-item[1], item[0])):
            print(f"  {code}: {count}")
        print("\nFirst occurrence (line number) by ERROR code:")
        for code in sorted(first_seen):
            print(f"  {code}: {first_seen[code]}")
        print(f"Skipped malformed lines: {skipped}")
    elif args.command == "trend":
        for hour, count in enumerate(error_counts):
            print(f"{hour:02d}: {count}")
        print(f"Skipped malformed lines: {skipped}")
    else:
        print("Level counts:")
        for level in sorted(levels):
            print(f"  {level}: {levels[level]}")
        print("\nERROR counts by code:")
        for code, count in sorted(errors.items(), key=lambda item: (-item[1], item[0])):
            print(f"  {code}: {count}")
        print(f"Skipped malformed lines: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
