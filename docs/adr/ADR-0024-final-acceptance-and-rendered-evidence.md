# ADR-0024: finite acceptance and rendered evidence replay

Date: 2026-10-14. Status: accepted.

The maintainer requested autonomous continuation until no stages remain. All
previous bounded phases are closed, and the original pivot explicitly allows
honest completion without complex-model superiority. Repeated version increments
are not themselves a product requirement. Map the ten original acceptance
criteria and V4–V8 deliverables, close demonstrated defects and verify one final
patch. Completion of this scope leaves zero required engineering stages.

The audit reproduced a performance-bundle discrepancy: JSON was recomputed, but
HTML was only checksummed. A caller could change HTML and update its checksum.
Require byte-exact HTML against rendering of the recomputed captured evidence,
before adding verification annotations. Quality bundles already follow this
principle. Regression and fresh installed/public bundle replay cover the defect.

Keep wire formats, policies, original freezes and decision semantics unchanged.
Use the exporting package version for replay; a renderer change may require a
new export. Checksums and consistent replay still cannot authenticate authors,
grading, collection or chronology. A caller can replace an entire evidence set.

Alternative: trust checksummed HTML as a separate presentation. Rejected because
users review that report as part of the verified evidence. Alternative: add
signing/services or new research until a model wins. Not required by the agreed
scope and cannot substitute for honest results. Any further integration, study
or production requirement must have its own concrete purpose and evidence gates.

Consequences: publish experimental patch 0.7.1, preserve all earlier releases and
negative studies, record final acceptance, then stop adding stages. Future bug
maintenance remains possible without treating the original project as unfinished.
