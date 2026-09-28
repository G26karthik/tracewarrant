# Dependency and license inventory

Continuation update: optional `integration` pins pydantic-ai-slim 2.51.0 (MIT) and opentelemetry-sdk 1.45.0 (Apache-2.0); `validation` pins SimPy 4.1.1 (MIT). Transitive installed metadata is preserved in [integration-license-evidence.json](integration-license-evidence.json). These groups do not become runtime wheel dependencies. Local Ollama/model weights are external user-installed software and are neither downloaded nor redistributed by this repository. The model probe does not confer rights to redistribute cached weights.

Recorded 2026-09-29 from the resolved `uv.lock` and installed distribution metadata. Runtime third-party dependencies: **none**. Python's standard library is supplied by the Python installation, not vendored. The current wheel contains this project's code only. Research repositories are not installed, linked or copied into the product.

New code/docs: Apache-2.0, selected over MIT because an explicit patent grant is useful for an infrastructure library while keeping adoption permissive. Terms: [Apache Software Foundation](https://www.apache.org/licenses/LICENSE-2.0). The original handoffs retain their original contents/attribution. No trademark rights or public package name are asserted.

| Installed build/dev package | Version | Metadata license | Purpose / alternative |
| --- | --- | --- | --- |
| hatchling | 1.27.0 | MIT | Small pure-Python package build; setuptools alternative |
| pytest | 8.4.2 | MIT | Parametrized contracts and CLI tests; unittest alternative |
| hypothesis | 6.168.3 | MPL-2.0 | Shrinking property tests; hand-written random tests lack shrinking |
| ruff | 0.16.9 | MIT | Unified lint/format; separate flake8/Black adds tooling |
| colorama | 0.4.6 | BSD (classifier; see installed license) | pytest Windows console dependency |
| iniconfig | 2.3.0 | MIT | pytest transitive dependency |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | pytest/build transitive dependency |
| pathspec | 1.1.1 | MPL-2.0 | build transitive dependency |
| pluggy | 1.6.0 | MIT | pytest/build transitive dependency |
| Pygments | 2.21.0 | BSD-2-Clause | pytest formatting dependency |
| sortedcontainers | 2.4.0 | Apache-2.0 | Hypothesis dependency |
| trove-classifiers | 2026.9.21.13 | Apache (classifier) | build metadata dependency |

Tooling is not bundled into the runtime wheel. Its licenses remain relevant if redistributing dev environments or modified tool source. Exact metadata is in [dependency-license-evidence.json](dependency-license-evidence.json); refresh after lock changes and inspect license files for redistributions. `uv` 0.9.26 is the environment/CI tool (MIT OR Apache-2.0), outside Python project dependencies. GitHub Actions are CI integrations; checkout/setup-python use their own MIT licenses. No container images are distributed.

Integration cautions: PerfSim GPL-2.0, WRENCH/WfCommons LGPL-3.0, Phoenix ELv2, Grafana/k6 AGPL-3.0 and Langfuse enterprise exclusions must not be treated as uniformly permissive. These are reviewed precedents, not approved dependencies. No competitor implementation or third-party dataset was imported. Recheck exact revisions and notices when an integration is selected.
