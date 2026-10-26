"""Regression tests for the logscope command-line summaries."""

import contextlib
import io
from pathlib import Path
import re
import unittest

import logscope


SAMPLE_LOG = Path(__file__).with_name("sample.log")


class LogscopeTests(unittest.TestCase):
    def run_command(self, *argv):
        output = io.StringIO()
        errors = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = logscope.main(argv)
        self.assertEqual(errors.getvalue(), "")
        self.assertEqual(status, 0)
        return output.getvalue()

    def test_top_known_counts_and_first_occurrence(self):
        output = self.run_command("top", str(SAMPLE_LOG))
        self.assertRegex(output, r"(?m)^  ERROR: 350$")
        self.assertRegex(output, r"(?m)^  INFO: 5004$")
        self.assertRegex(output, r"(?m)^  WARN: 640$")
        self.assertRegex(output, r"(?m)^  DB_TIMEOUT: 148$")
        self.assertRegex(output, r"(?m)^  DB_TIMEOUT: 13$")

    def test_trend_known_total_and_twenty_hour_count(self):
        output = self.run_command("trend", str(SAMPLE_LOG))
        counts = [int(value) for value in re.findall(r"(?m)^\d{2}: (\d+)$", output)]
        self.assertEqual(len(counts), 24)
        self.assertEqual(sum(counts), 350)
        self.assertEqual(counts[20], 138)

    def test_window_known_counts(self):
        output = self.run_command(
            "window",
            str(SAMPLE_LOG),
            "2026-10-21 20:00:00",
            "2026-10-21 21:00:00",
        )
        self.assertRegex(output, r"(?m)^  ERROR: 138$")
        self.assertRegex(output, r"(?m)^  DB_TIMEOUT: 59$")

    def test_top_reports_skipped_malformed_lines(self):
        output = self.run_command("top", str(SAMPLE_LOG))
        self.assertRegex(output, r"(?m)^Skipped malformed lines: 6$")

    def test_trend_reports_skipped_malformed_lines(self):
        output = self.run_command("trend", str(SAMPLE_LOG))
        self.assertRegex(output, r"(?m)^Skipped malformed lines: 6$")

    def test_window_reports_skipped_malformed_lines(self):
        output = self.run_command(
            "window",
            str(SAMPLE_LOG),
            "2026-10-21 20:00:00",
            "2026-10-21 21:00:00",
        )
        self.assertRegex(output, r"(?m)^Skipped malformed lines: 6$")


if __name__ == "__main__":
    unittest.main()
