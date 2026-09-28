import json
import subprocess
import sys
from pathlib import Path

from workload_lab.cli import main

EXAMPLE = Path(__file__).parents[1] / "examples/research-workflow.otlp.json"


def test_cli_json_is_deterministic_and_complete():
    command = [sys.executable, "-m", "workload_lab", "analyze", str(EXAMPLE), "--format", "json"]
    first = subprocess.run(command, check=True, text=True, capture_output=True)
    second = subprocess.run(command, check=True, text=True, capture_output=True)
    assert first.stdout == second.stdout
    assert first.stderr == ""
    data = json.loads(first.stdout)
    assert data["schema_version"] == "0.2"
    assert data["reports"][0]["critical_path_elapsed"]["value"] == 11_000_000_000


def test_ingest_output_does_not_overwrite(tmp_path, capsys):
    output = tmp_path / "ir.json"
    assert main(["ingest", str(EXAMPLE), "--output", str(output)]) == 0
    first = output.read_bytes()
    assert json.loads(first)["artifact_type"] == "execution_ir"
    assert main(["ingest", str(EXAMPLE), "--output", str(output)]) == 2
    assert output.read_bytes() == first
    assert "FileExistsError" in capsys.readouterr().err


def test_cli_invalid_input_error_has_no_payload(tmp_path, capsys):
    path = tmp_path / "private-secret.json"
    path.write_text('{"secret":"do-not-echo",broken}')
    assert main(["analyze", str(path)]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert "invalid" in output.err
    assert "do-not-echo" not in output.err and "private-secret" not in output.err
