"""Bounded offline snapshots for application quality; integrity is not authenticity."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from .artifacts import canonical_bytes
from .ir import ValidationError
from .jobs import _write_directory
from .qualification import (
    MAX_PLAN_BYTES,
    MAX_POLICY_BYTES,
    MAX_SAMPLE_BYTES,
    qualification_html,
    qualify_application,
)

# Fixed flat names avoid arbitrary paths, manifests or archive extraction.
LIMITS = {
    "sample.json": MAX_SAMPLE_BYTES,
    "policy.json": MAX_POLICY_BYTES,
    "plan.json": MAX_PLAN_BYTES,
    "freeze.json": MAX_POLICY_BYTES,
    "report.json": 16 * 1024 * 1024,
    "report.html": 16 * 1024 * 1024,
}
REQUIRED = {"sample.json", "policy.json", "report.json", "report.html"}


def _read(path: Path, limit: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValidationError("quality bundle inputs must be regular local files")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValidationError("quality bundle file exceeds byte budget")
    return raw


def _replay(files: dict[str, bytes]) -> dict:
    with tempfile.TemporaryDirectory(prefix="tracewarrant-quality-") as folder:
        root = Path(folder)
        for name, raw in files.items():
            if name in ("sample.json", "policy.json", "plan.json", "freeze.json"):
                (root / name).write_bytes(raw)
        bound = "plan.json" in files
        return qualify_application(
            root / "sample.json",
            root / "policy.json",
            plan_path=root / "plan.json" if bound else None,
            freeze_path=root / "freeze.json" if bound else None,
        )


def _reports(report: dict) -> dict[str, bytes]:
    files = {
        "report.json": canonical_bytes(report),
        "report.html": qualification_html(report).encode("utf-8"),
    }
    if any(len(raw) > LIMITS[name] for name, raw in files.items()):
        raise ValidationError("quality bundle report exceeds byte budget")
    return files


def bundle_quality(sample_path, policy_path, output, *, plan_path=None, freeze_path=None):
    """Capture each input once, qualify the snapshot and export exact bytes exclusively."""
    if (plan_path is None) != (freeze_path is None):
        raise ValidationError("quality bundle requires both plan and freeze")
    paths = {"sample.json": sample_path, "policy.json": policy_path}
    if plan_path is not None:
        paths.update({"plan.json": plan_path, "freeze.json": freeze_path})
    files = {name: _read(Path(path), LIMITS[name]) for name, path in paths.items()}
    report = _replay(files)
    files.update(_reports(report))
    files["SHA256SUMS"] = "".join(
        f"{hashlib.sha256(raw).hexdigest()}  {name}\n" for name, raw in sorted(files.items())
    ).encode("ascii")
    _write_directory(Path(output), files)
    return report


def verify_quality_bundle(path) -> dict:
    """Check exact membership, hashes and both rendered reports against private replay."""
    root = Path(path)
    if root.is_symlink() or not root.is_dir():
        raise ValidationError("quality bundle must be a local directory")
    sums = _read(root / "SHA256SUMS", 1024)
    try:
        lines = sums.decode("ascii").splitlines()
    except UnicodeError:
        raise ValidationError("quality bundle checksums must be ASCII") from None
    if len(lines) not in (4, 6):
        raise ValidationError("invalid quality bundle entry count")
    files = {}
    for line in lines:
        digest, separator, name = line.partition("  ")
        if (
            not separator
            or name not in LIMITS
            or name in files
            or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
        ):
            raise ValidationError("invalid quality bundle checksum entry")
        raw = _read(root / name, LIMITS[name])
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValidationError("quality bundle checksum mismatch")
        files[name] = raw
    if set(files) not in (REQUIRED, set(LIMITS)):
        raise ValidationError("quality bundle has missing inputs or incomplete binding")
    actual = set()
    for index, entry in enumerate(root.iterdir()):
        if index >= 7:
            raise ValidationError("quality bundle has too many entries")
        actual.add(entry.name)
    if actual != set(files) | {"SHA256SUMS"}:
        raise ValidationError("quality bundle has missing or unlisted entries")
    report = _replay(files)
    if any(files[name] != raw for name, raw in _reports(report).items()):
        raise ValidationError("quality bundle reports disagree with evidence")
    report["bundle_checksums_verified"] = True
    report["bundle_checksums_sha256"] = hashlib.sha256(sums).hexdigest()
    report["limitations"].append("bundle_checksums_do_not_authenticate_author")
    return report
