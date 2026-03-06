from pathlib import Path

from devguard_ai_validator.cli import main


def test_ai_validator_cli_writes_sarif(monkeypatch, tmp_path):
    sample = Path(__file__).resolve().parents[3] / "examples" / "sample_insecure.py"
    output = tmp_path / "report.sarif"

    argv = [
        "devguard_ai_validator",
        str(sample),
        "--format",
        "sarif",
        "--output",
        str(output),
    ]
    monkeypatch.setattr("sys.argv", argv)

    exit_code = main()
    assert exit_code == 1
    assert output.exists()
    body = output.read_text(encoding="utf-8")
    assert '"version": "2.1.0"' in body
