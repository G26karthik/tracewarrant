# Recorded local qualification

All three JSON records were generated from clean source commit `ea9ce3abf704f4fb5fa9539b4118f68cd3f25711` before these evidence files were added. They retain their exact build/source/lock/harness digests; subsequent evidence-only commits do not replace them.

- `windows.json`: fresh installed-wheel qualification on Windows Python 3.12.12.
- `linux.json`: fresh installed-wheel qualification on Ubuntu WSL Python 3.12.3.
- `offline-audit.json`: 64 preserved original working files, original pilot tag, 72 FRAMES sessions and byte-exact evaluation.

The two wheels have identical member names and payload bytes, including metadata and license. Their archive SHA-256 values differ because ZIP creator/permission metadata differs between Windows and Linux. Both were installed and verified separately. Do not describe the archive bytes as identical or these local checks as independent maintainer review.

The accompanying regression suite passed 150 tests on Windows Python 3.11, 3.12.12 and 3.13, and Ubuntu Python 3.12.3. Hosted CI has not run. [Full completion report](../completion-0.3.1.md), [rerun instructions](../release-qualification.md).
