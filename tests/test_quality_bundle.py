import hashlib
import json
import shutil
from pathlib import Path

import pytest

from workload_lab.artifacts import canonical_bytes
from workload_lab.cli import main
from workload_lab.ir import ValidationError
from workload_lab.quality_bundle import LIMITS, bundle_quality, verify_quality_bundle

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/qualification/hotpot-frozen"


def export(output, bound=True):
    return bundle_quality(
        EXAMPLE / "sample.json",
        EXAMPLE / "policy.json",
        output,
        plan_path=EXAMPLE / "plan.json" if bound else None,
        freeze_path=EXAMPLE / "freeze.json" if bound else None,
    )


def rehash(root):
    names = [line.split("  ")[1] for line in (root / "SHA256SUMS").read_text().splitlines()]
    (root / "SHA256SUMS").write_text(
        "".join(
            f"{hashlib.sha256((root / name).read_bytes()).hexdigest()}  {name}\n" for name in names
        ),
        encoding="ascii",
    )


@pytest.mark.parametrize("bound", [False, True])
def test_exact_bytes_portable_replay_and_retained_failure(tmp_path, bound):
    output = tmp_path / "bundle"
    report = export(output, bound)
    moved = tmp_path / "moved"
    shutil.copytree(output, moved)
    replay = verify_quality_bundle(moved)
    assert replay.pop("bundle_checksums_verified") is True
    assert len(replay.pop("bundle_checksums_sha256")) == 64
    assert replay["limitations"].pop() == "bundle_checksums_do_not_authenticate_author"
    assert replay == report and report["result"] == "failed"
    assert report["counts"]["offered"] == 8
    assert ("binding" in report) == bound
    for name in ("sample.json", "policy.json", "plan.json", "freeze.json"):
        if (output / name).exists():
            assert (output / name).read_bytes() == (EXAMPLE / name).read_bytes()


@pytest.mark.parametrize("name", list(LIMITS))
def test_changed_payload_without_updated_hash_refused(tmp_path, name):
    export(tmp_path / "bundle")
    path = tmp_path / "bundle" / name
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValidationError, match="checksum mismatch"):
        verify_quality_bundle(path.parent)


@pytest.mark.parametrize("target", ["result", "scope", "gate", "limitation", "html"])
def test_rehashed_false_reports_refused(tmp_path, target):
    root = tmp_path / "bundle"
    export(root)
    if target == "html":
        (root / "report.html").write_bytes(b"<h1>passed</h1>")
    else:
        data = json.loads((root / "report.json").read_bytes())
        if target == "result":
            data["result"] = "passed"
        elif target == "scope":
            data["claim_scope"] = "production_certified"
        elif target == "gate":
            data["gates"][2]["status"] = "passed"
        else:
            data["limitations"] = []
        (root / "report.json").write_bytes(canonical_bytes(data))
    rehash(root)
    with pytest.raises(ValidationError, match="reports disagree"):
        verify_quality_bundle(root)


@pytest.mark.parametrize("name", ["../sample.json", "C:sample.json", "unknown.json", "report.json"])
def test_traversal_unknown_and_duplicate_checksum_names_refused(tmp_path, name):
    root = tmp_path / "bundle"
    export(root)
    sums = root / "SHA256SUMS"
    lines = sums.read_text().splitlines()
    lines[0] = "0" * 64 + "  " + name
    sums.write_text("\n".join(lines) + "\n", encoding="ascii")
    with pytest.raises(ValidationError):
        verify_quality_bundle(root)


@pytest.mark.parametrize("alter", ["missing", "extra", "half-binding", "oversized", "bad-ascii"])
def test_missing_extra_incomplete_and_bounded_inputs(tmp_path, alter):
    root = tmp_path / "bundle"
    export(root)
    if alter == "missing":
        (root / "sample.json").unlink()
    elif alter == "extra":
        (root / "extra").mkdir()
    elif alter == "half-binding":
        sums = root / "SHA256SUMS"
        sums.write_text(
            "\n".join(
                line for line in sums.read_text().splitlines() if not line.endswith("plan.json")
            )
            + "\n",
            encoding="ascii",
        )
    elif alter == "oversized":
        (root / "policy.json").write_bytes(b" " * (LIMITS["policy.json"] + 1))
    else:
        (root / "SHA256SUMS").write_bytes(b"\xff")
    with pytest.raises(ValidationError):
        verify_quality_bundle(root)


def test_rehashed_sample_omission_still_refuses_declared_population(tmp_path):
    root = tmp_path / "bundle"
    export(root)
    data = json.loads((root / "sample.json").read_bytes())
    data["rows"].pop()
    (root / "sample.json").write_bytes(canonical_bytes(data))
    rehash(root)
    with pytest.raises(ValidationError, match="population differs"):
        verify_quality_bundle(root)


def test_export_uses_captured_bytes_after_source_changes(tmp_path, monkeypatch):
    from workload_lab import quality_bundle

    sample = tmp_path / "sample.json"
    sample.write_bytes((EXAMPLE / "sample.json").read_bytes())
    replay = quality_bundle._replay

    def mutate_then_replay(files):
        sample.write_bytes(b"invalid changed input")
        return replay(files)

    monkeypatch.setattr(quality_bundle, "_replay", mutate_then_replay)
    root = tmp_path / "bundle"
    bundle_quality(sample, EXAMPLE / "policy.json", root)
    assert (root / "sample.json").read_bytes() == (EXAMPLE / "sample.json").read_bytes()
    assert verify_quality_bundle(root)["result"] == "failed"


def test_write_failure_rolls_back_only_owned_output(tmp_path, monkeypatch):
    original = Path.open

    def fail_html(path, *args, **kwargs):
        if path.name == "report.html" and args == ("xb",):
            raise OSError("simulated disk failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_html)
    with pytest.raises(OSError):
        export(tmp_path / "bundle")
    assert not (tmp_path / "bundle").exists()
    assert (EXAMPLE / "sample.json").is_file()


def test_cli_pass_fail_invalid_and_exclusive_outputs(tmp_path, capsys):
    args = [
        "bundle-quality",
        str(EXAMPLE / "sample.json"),
        "--policy",
        str(EXAMPLE / "policy.json"),
        "--output",
        str(tmp_path / "bundle"),
    ]
    assert main(args) == 1
    original = (tmp_path / "bundle" / "SHA256SUMS").read_bytes()
    assert main(args) == 2
    assert (tmp_path / "bundle" / "SHA256SUMS").read_bytes() == original
    verify = [
        "verify-quality-bundle",
        str(tmp_path / "bundle"),
        "--output",
        str(tmp_path / "verified"),
    ]
    assert main(verify) == 1
    (tmp_path / "bundle" / "report.html").write_bytes(b"forged")
    verify[-1] = str(tmp_path / "invalid")
    assert main(verify) == 2 and not (tmp_path / "invalid").exists()
    policy = json.loads((EXAMPLE / "policy.json").read_bytes())
    for metric in policy["metrics"]:
        metric["minimum_value"] = 0
    (tmp_path / "policy.json").write_bytes(canonical_bytes(policy))
    args[3] = str(tmp_path / "policy.json")
    args[-1] = str(tmp_path / "passing")
    assert main(args) == 0
    verify[1], verify[-1] = str(tmp_path / "passing"), str(tmp_path / "pass-report")
    assert main(verify) == 0
    assert str(tmp_path) not in capsys.readouterr().err


def test_symlink_payload_refused_when_host_supports_it(tmp_path):
    root = tmp_path / "bundle"
    export(root)
    target = root / "policy.json"
    target.unlink()
    try:
        target.symlink_to(EXAMPLE / "policy.json")
    except OSError:
        # Windows may lack symlink privilege. Exercise the same refusal branch
        # through the Path predicate; hosted Linux also exercises a real link.
        from unittest.mock import patch

        with patch.object(Path, "is_symlink", return_value=True):
            with pytest.raises(ValidationError):
                verify_quality_bundle(root)
    else:
        with pytest.raises(ValidationError, match="regular local"):
            verify_quality_bundle(root)


def test_half_binding_export_and_invalid_sample_create_no_output(tmp_path):
    with pytest.raises(ValidationError, match="both plan and freeze"):
        bundle_quality(
            EXAMPLE / "sample.json",
            EXAMPLE / "policy.json",
            tmp_path / "half",
            plan_path=EXAMPLE / "plan.json",
        )
    assert not (tmp_path / "half").exists()
    (tmp_path / "sample.json").write_bytes(b'{"private":"never echo"}')
    with pytest.raises(ValidationError):
        bundle_quality(tmp_path / "sample.json", EXAMPLE / "policy.json", tmp_path / "bad")
    assert not (tmp_path / "bad").exists()
