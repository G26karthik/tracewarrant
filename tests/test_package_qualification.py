from zipfile import ZipFile

import pytest

from benchmarks.qualify_package import ROOT, qualify


@pytest.mark.parametrize("defect", ["stale", "missing"])
def test_stale_or_incomplete_wheel_refused_before_installation(tmp_path, defect):
    wheel = tmp_path / "tracewarrant-0.3.1-py3-none-any.whl"
    with ZipFile(wheel, "w") as archive:
        for path in (ROOT / "src/workload_lab").rglob("*.py"):
            raw = path.read_bytes()
            if path.name == "validation.py":
                if defect == "missing":
                    continue
                raw += b"\n# obsolete build\n"
            archive.writestr(path.relative_to(ROOT / "src").as_posix(), raw)
    # Neither a source archive nor an installer exists: stale code must be
    # refused before installing or running anything from this distribution.
    with pytest.raises(ValueError, match="wheel code differs from current source checkout"):
        qualify(wheel, tmp_path / "missing.tar.gz", "missing-installer")
