#!/usr/bin/env python3
"""Summarize structured server logs."""

import argparse
from datetime import datetime
import re
import sys
from collections import Counter
from pathlib import Path

# Timestamp: YYYY-MM-DD HH:MM:SS; level and bracketed module follow.
LOG_LINE = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL) +"
    r"\[(?P<module>[A-Za-z0-9_-]+)\] "
    r"(?P<message>\S(?:.*\S)?)"
)


def analyze(path):
    levels = Counter()
    errors = Counter()
    first_seen = {}
    skipped = 0
    with path.open(encoding="utf-8") as log_file:
        for line_number, raw_line in enumerate(log_file, 1):
            line = raw_line.rstrip("\r\n")
            match = LOG_LINE.fullmatch(line)
            if not match:
                skipped += 1
                continue
            level = match.group("level")
            levels[level] += 1
            if level == "ERROR":
                code = match.group("message").split(maxsplit=1)[0]
                errors[code] += 1
                first_seen.setdefault(code, line_number)
    return levels, errors, first_seen, skipped


def parse_timestamp(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "timestamp must use YYYY-MM-DD HH:MM:SS"
        ) from exc


def analyze_trend(path):
    errors_by_hour = [0] * 24
    skipped = 0
    with path.open(encoding="utf-8") as log_file:
        for raw_line in log_file:
            match = LOG_LINE.fullmatch(raw_line.rstrip("\r\n"))
            if not match:
                skipped += 1
                continue
            try:
                timestamp = datetime.strptime(match.group("timestamp"), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                skipped += 1
                continue
            if match.group("level") == "ERROR":
                errors_by_hour[timestamp.hour] += 1
    return errors_by_hour, skipped


def analyze_window(path, start, end):
    levels = Counter()
    errors = Counter()
    skipped = 0
    with path.open(encoding="utf-8") as log_file:
        for raw_line in log_file:
            match = LOG_LINE.fullmatch(raw_line.rstrip("\r\n"))
            if not match:
                skipped += 1
                continue
            try:
                timestamp = datetime.strptime(match.group("timestamp"), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                skipped += 1
                continue
            if not start <= timestamp < end:
                continue
            level = match.group("level")
            levels[level] += 1
            if level == "ERROR":
                code = match.group("message").split(maxsplit=1)[0]
                errors[code] += 1
    return levels, errors, skipped


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyze structured server logs.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    top_parser = subparsers.add_parser("top", help="show level and ERROR code summaries")
    top_parser.add_argument("logfile", type=Path)
    trend_parser = subparsers.add_parser("trend", help="show ERROR counts by hour")
    trend_parser.add_argument("logfile", type=Path)
    window_parser = subparsers.add_parser("window", help="summarize entries in a time range")
    window_parser.add_argument("logfile", type=Path)
    window_parser.add_argument("start", type=parse_timestamp)
    window_parser.add_argument("end", type=parse_timestamp)
    args = parser.parse_args(argv)

    try:
        if args.command == "trend":
            errors_by_hour, skipped = analyze_trend(args.logfile)
            for hour, count in enumerate(errors_by_hour):
                print(f"{hour:02}: {count}")
            print(f"Skipped malformed lines: {skipped}")
            return 0
        if args.command == "window":
            levels, errors, skipped = analyze_window(args.logfile, args.start, args.end)
            print("Line counts by level:")
            for level in ("DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"):
                if levels[level]:
                    print(f"  {level}: {levels[level]}")
            print("\nERROR counts by code:")
            for code, count in sorted(errors.items(), key=lambda item: (-item[1], item[0])):
                print(f"  {code}: {count}")
            print(f"Skipped malformed lines: {skipped}")
            return 0

        levels, errors, first_seen, skipped = analyze(args.logfile)
    except (OSError, UnicodeError) as exc:
        print(f"logscope: {exc}", file=sys.stderr)
        return 2

    print("Line counts by level:")
    for level in ("DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"):
        if levels[level]:
            print(f"  {level}: {levels[level]}")
    print("\nERROR counts by code:")
    for code, count in sorted(errors.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {code}: {count}")
    print("\nFirst ERROR occurrence by code:")
    for code in sorted(first_seen):
        print(f"  {code}: line {first_seen[code]}")
    print(f"Skipped malformed lines: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
