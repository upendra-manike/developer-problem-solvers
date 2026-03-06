from pathlib import Path

from devguard_core.config import ScanOptions
from devguard_core.scanner import scan_path


def test_scanner_detects_findings():
    sample = Path(__file__).resolve().parents[3] / "examples" / "sample_insecure.py"
    result = scan_path(sample)
    assert result.total >= 5
    rule_ids = {f.rule_id for f in result.findings}
    assert "DG001" in rule_ids
    assert "DG002" in rule_ids
    assert "DG003" in rule_ids
    assert "DG004" in rule_ids
    assert "DG005" in rule_ids


def test_scanner_skips_excluded_directories(tmp_path):
    ignored = tmp_path / "node_modules"
    ignored.mkdir(parents=True)
    tracked = tmp_path / "src"
    tracked.mkdir(parents=True)

    (ignored / "bad.py").write_text("token = 'supersecretvalue'\n", encoding="utf-8")
    (tracked / "good.py").write_text("print('ok')\n", encoding="utf-8")

    result = scan_path(tmp_path)
    assert result.total == 0


def test_scanner_skips_large_files(tmp_path):
    sample = tmp_path / "large.py"
    sample.write_text("token = 'supersecretvalue'\n" + ("#" * 8192), encoding="utf-8")

    options = ScanOptions(max_file_size_bytes=1024)
    result = scan_path(tmp_path, options=options)
    assert result.total == 0


def test_scanner_supports_inline_suppression(tmp_path):
    sample = tmp_path / "suppressed.py"
    sample.write_text("token = 'supersecretvalue'  # devguard-ignore: DG003\n", encoding="utf-8")

    result = scan_path(sample)
    assert result.total == 0


def test_scanner_supports_next_line_suppression(tmp_path):
    sample = tmp_path / "next_line.py"
    sample.write_text(
        "# devguard-ignore-next-line: DG003\n"
        "token = 'supersecretvalue'\n",
        encoding="utf-8",
    )

    result = scan_path(sample)
    assert result.total == 0


def test_scanner_workers_option(tmp_path):
    sample = tmp_path / "multi.py"
    sample.write_text("token = 'supersecretvalue'\n", encoding="utf-8")

    options = ScanOptions(workers=1)
    result = scan_path(tmp_path, options=options)
    assert result.total == 1
