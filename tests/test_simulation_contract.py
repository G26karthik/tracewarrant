import json
import subprocess
import sys
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from workload_lab.cli import main
from workload_lab.ingest import _decode
from workload_lab.ir import ValidationError
from workload_lab.simulation import scenario_from_dict

EXAMPLE = Path(__file__).parents[1] / "examples/scenario.json"


def test_simulation_cli_reproducible_and_exclusive(tmp_path):
    command = [sys.executable, "-m", "workload_lab", "simulate", str(EXAMPLE)]
    first = subprocess.run(command, capture_output=True, text=True, check=True)
    second = subprocess.run(command, capture_output=True, text=True, check=True)
    assert first.stdout == second.stdout
    data = json.loads(first.stdout)
    assert data["provenance"] == "SIMULATED" and data["offered"] == 3
    assert data["outcomes"]["completed"] == 3
    path = tmp_path / "result.json"
    assert main(["simulate", str(EXAMPLE), "--output", str(path)]) == 0
    previous = path.read_bytes()
    assert main(["simulate", str(EXAMPLE), "--output", str(path)]) == 2
    assert path.read_bytes() == previous


@pytest.mark.parametrize(
    "key,value",
    [
        ("horizon_ns", True),
        ("seed", -1),
        ("schema_version", "2"),
        ("tasks", None),
        ("arrivals", [{"id": "a", "at_ns": 1.1}]),
        ("plugin", "execute-private-payload"),
    ],
)
def test_scenario_rejects_untrusted_shapes(key, value):
    data = json.loads(EXAMPLE.read_text())
    data[key] = value
    with pytest.raises(ValidationError):
        scenario_from_dict(data)


@given(
    st.recursive(
        st.none() | st.booleans() | st.integers() | st.text(max_size=20),
        lambda children: (
            st.lists(children, max_size=5)
            | st.dictionaries(st.text(max_size=12), children, max_size=5)
        ),
        max_leaves=30,
    )
)
def test_bounded_random_json_parser_never_executes_or_leaks(data):
    raw = json.dumps(data)
    try:
        decoded = _decode(raw)
    except ValidationError as error:
        assert "must be an object" in str(error)
    else:
        assert isinstance(decoded, dict) and decoded == data
