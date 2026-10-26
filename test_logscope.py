import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "logscope.py"
LOG = ROOT / "sample.log"


class LogscopeCommandTests(unittest.TestCase):
    def run_command(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_skipped_line_count(self, output):
        self.assertEqual(output.splitlines()[-1], "Skipped malformed lines: 6")

    def test_top_reports_verified_counts_and_first_occurrence(self):
        result = self.run_command("top", str(LOG))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("  ERROR: 350", result.stdout)
        self.assertIn("  INFO: 5004", result.stdout)
        self.assertIn("  WARN: 640", result.stdout)
        self.assertIn("  DB_TIMEOUT: 148", result.stdout)
        self.assertIn("  DB_TIMEOUT: line 13", result.stdout)

    def test_trend_reports_verified_daily_and_hourly_errors(self):
        result = self.run_command("trend", str(LOG))
        self.assertEqual(result.returncode, 0, result.stderr)
        counts = {
            int(line.split(":", 1)[0]): int(line.split(":", 1)[1].strip())
            for line in result.stdout.splitlines()
            if ":" in line and line.split(":", 1)[0].isdigit()
        }
        self.assertEqual(sum(counts.values()), 350)
        self.assertEqual(counts[20], 138)

    def test_window_reports_verified_range_counts(self):
        result = self.run_command(
            "window",
            str(LOG),
            "2026-10-21 20:00:00",
            "2026-10-21 21:00:00",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("  DB_TIMEOUT: 59", result.stdout)
        self.assertIn("  ERROR: 138", result.stdout)

    def test_top_ends_with_skipped_malformed_line_count(self):
        result = self.run_command("top", str(LOG))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_skipped_line_count(result.stdout)

    def test_trend_ends_with_skipped_malformed_line_count(self):
        result = self.run_command("trend", str(LOG))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_skipped_line_count(result.stdout)

    def test_window_ends_with_skipped_malformed_line_count(self):
        result = self.run_command(
            "window",
            str(LOG),
            "2026-10-21 20:00:00",
            "2026-10-21 21:00:00",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_skipped_line_count(result.stdout)


if __name__ == "__main__":
    unittest.main()
