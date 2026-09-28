# Security and privacy

This experimental tool analyzes local untrusted telemetry. It performs no remote upload and executes no traced tools. The default importer discards span names, prompts, messages, arguments, outputs, URLs, SQL, exceptions and events. Selected service/model/tool labels and structural IDs remain and can contain sensitive data; this is not an anonymization guarantee.

Input byte/span limits bound the accepted workload; JSON parsing still uses memory proportional to the accepted document. Use smaller batches on constrained systems. Report sensitive issues privately to the repository maintainer once a public repository/contact exists; until then do not publish private traces in issue reports. Use a minimal synthetic reproducer. No hosted service or security support SLA exists.
