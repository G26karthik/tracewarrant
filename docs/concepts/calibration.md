# Calibration — proposed, not implemented

The identification problem comes first: response time mixes service, queueing, network and orchestration. A trace collected at one load cannot uniquely recover capacities. Require pool sizes, enqueue/start/end signals and measured intervention anchors before capacity claims. Store unresolved components as unknown.

Group by application/model version, request shape, backend/hardware, cache state and load regime. Compare empirical resampling with parametric fits; preserve correlated within-session samples and shared slowdowns. Estimate retry and branch probabilities with denominators including failures/censoring. Keep branch semantics independent from source code/framework names.

Split whole sessions and time/configuration cells into calibration/validation sets. Record fitting procedure, seeds, sample counts, quantiles, rejected/missing records, validity envelope and software hashes. Use held-out loads and changed resources, not random spans from the same session, to test intervention predictions. Measure instrumentation overhead and calibration effort. Tail accuracy is underpowered when tail samples are sparse.

Hardware profiles later include exact SKU/VRAM, CPU/RAM, clocks/power, OS/driver/compiler/CUDA, input shapes, precision, repetitions and raw curves. Measured real-serving anchors override synthetic approximations where applicable. Profiles from community contributors retain source and envelope; never silently transfer them between GPUs. No sample file named after an RTX GPU is created until actual measurements exist.
