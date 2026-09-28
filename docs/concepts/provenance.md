# Provenance

Every time quantity contains `value`, `unit`, and `evidence`. Evidence contains provenance, origin, method, sources, assumptions and optional uncertainty bounds. UNKNOWN requires a null value; zero requires evidence. Source is a digest plus structural span identity, not a raw file path or payload.

| Category | Meaning |
| --- | --- |
| MEASURED | Reported by an observed source; measurement correctness/representativeness is not guaranteed |
| CALIBRATED | Fitted to a named dataset with envelope and validation |
| INTERPOLATED | Inside a stated calibrated domain |
| EXTRAPOLATED | Outside that domain |
| SIMULATED | Output of a named simulator/model version |
| ESTIMATED | An assumption, synthetic value or unsupported analytical parameter |
| UNKNOWN | No established value |

Origin is independent: observed or synthetic. Derived M1 quantities retain observed MEASURED or synthetic ESTIMATED provenance and state their exact derivation method. That records graph arithmetic, not a capacity prediction. Future simulation must preserve references to all calibration inputs; a single output tag is insufficient for recommendations.

M1 emits no statistical confidence bounds: deterministic graph arithmetic has no sampling interval, and a single trace gives no population confidence. A null uncertainty field states that limitation. Later bounds must specify confidence level, method, cohort/sample size, whether they concern a population parameter or future observation, and whether model discrepancy is included. Never treat a bootstrap interval as protection against extrapolation.
