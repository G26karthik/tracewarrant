# Security and privacy

Report security vulnerabilities through [GitHub private vulnerability reporting](https://github.com/G26karthik/tracewarrant/security/advisories/new). This channel is enabled for the public repository. Include the affected version, impact and a minimal synthetic reproduction; keep sensitive evidence in the private report.

This experimental tool analyzes local untrusted telemetry. It performs no remote upload and executes no traced tools. The default importer discards span names, prompts, messages, arguments, outputs, URLs, SQL, exceptions and events. Selected service/model/tool labels and structural IDs remain and can contain sensitive data; this is not an anonymization guarantee.

Input byte/span limits and a predecode nesting limit of 64 bound accepted telemetry. Simulation additionally bounds node/session/state counts and processed events, rejects unknown scenario fields and never loads plugins. Parsing still uses memory proportional to accepted input; use smaller batches on constrained systems. Example measurement applications execute only when explicitly run; the local model example is separate from the offline importer/simulator. Do not publish private traces in public issues. No hosted service or security support SLA exists.
