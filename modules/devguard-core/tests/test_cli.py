from __future__ import annotations

import json
from pathlib import Path

import pytest

from devguard_core.cli import main


def test_cli_min_severity_filters_to_high(monkeypatch, tmp_path, capsys):
    sample = Path(__file__).resolve().parents[3] / "examples" / "sample_insecure.py"
    argv = [
        "devguard_core",
        "scan",
        str(sample),
        "--format",
        "json",
        "--min-severity",
        "high",
    ]
    monkeypatch.setattr("sys.argv", argv)

    exit_code = main()
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert exit_code == 1
    assert payload["total"] == 3
    assert all(item["severity"] == "high" for item in payload["findings"])


def test_cli_invalid_baseline_is_user_error(monkeypatch, tmp_path):
    sample = Path(__file__).resolve().parents[3] / "examples" / "sample_insecure.py"
    baseline = tmp_path / "bad-baseline.json"
    baseline.write_text("not-json", encoding="utf-8")

    argv = [
        "devguard_core",
        "scan",
        str(sample),
        "--baseline-in",
        str(baseline),
    ]
    monkeypatch.setattr("sys.argv", argv)

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 2


def test_cli_filters_by_rule_and_confidence(monkeypatch, capsys):
    sample = Path(__file__).resolve().parents[3] / "examples" / "sample_insecure.py"
    argv = [
        "devguard_core",
        "scan",
        str(sample),
        "--format",
        "json",
        "--include-rule",
        "DG003",
        "--min-confidence",
        "0.9",
    ]
    monkeypatch.setattr("sys.argv", argv)

    exit_code = main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["total"] == 1
    assert payload["findings"][0]["rule_id"] == "DG003"


def test_cli_reads_dot_devguard_config(monkeypatch, tmp_path, capsys):
    target = tmp_path / "src"
    target.mkdir(parents=True)
    sample = target / "code.py"
    sample.write_text("token = 'verysecretvalue'\n", encoding="utf-8")

    config = target / ".devguard.json"
    config.write_text(
        json.dumps(
            {
                "min_severity": "high",
                "min_confidence": 0.9,
                "include_rule": ["DG003"],
                "workers": 1,
            }
        ),
        encoding="utf-8",
    )

    argv = ["devguard_core", "scan", str(target), "--format", "json"]
    monkeypatch.setattr("sys.argv", argv)

    exit_code = main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["total"] == 1
    assert payload["findings"][0]["rule_id"] == "DG003"


def test_cli_file_list_scans_only_listed_files(monkeypatch, tmp_path, capsys):
    src = tmp_path / "src"
    src.mkdir(parents=True)
    a = src / "a.py"
    b = src / "b.py"
    a.write_text("token = 'verysecretvalue'\n", encoding="utf-8")
    b.write_text("token = 'anothersecretvalue'\n", encoding="utf-8")

    file_list = tmp_path / "changed.txt"
    file_list.write_text(str(a) + "\n", encoding="utf-8")

    argv = [
        "devguard_core",
        "scan",
        str(src),
        "--file-list",
        str(file_list),
        "--format",
        "json",
    ]
    monkeypatch.setattr("sys.argv", argv)

    exit_code = main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["total"] == 1
    assert payload["findings"][0]["file_path"].endswith("a.py")


def test_cli_missing_file_list_is_user_error(monkeypatch, tmp_path):
    src = tmp_path / "src"
    src.mkdir(parents=True)
    (src / "a.py").write_text("print('ok')\n", encoding="utf-8")

    argv = [
        "devguard_core",
        "scan",
        str(src),
        "--file-list",
        str(tmp_path / "missing.txt"),
    ]
    monkeypatch.setattr("sys.argv", argv)

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
