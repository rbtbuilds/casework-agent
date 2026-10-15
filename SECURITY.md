# Security and operating boundaries

This project is a local fictional simulation. Bind every service to 127.0.0.1. It has no multi-user authentication or production tenant isolation and must not be exposed to a public network.

The model has three bounded read tools. Untrusted source text cannot select a URL, change case scope, grant approval or dispatch writes. Deterministic code validates action, evidence, proposal hash, expiry and source versions. The executor saves the exact operation key/body/hash before sending. Unknown outcomes require journal reconciliation, never a new key to bypass uncertainty.

The mock services retain journals for their database lifetime and commit each domain effect with its journal in one transaction. This proves per-key protection in the simulation, not distributed exactly-once behavior or security of arbitrary third-party services. A cross-service snapshot can change after preflight. A partial pair remains for review; there is no compensation.

No secrets or customer data belong in issues, fixtures, screenshots or traces. Do not upload local model assets. If you discover a vulnerability, retain a minimal synthetic reproduction privately and contact the repository owner through a separately agreed private channel. Use [GitHub private vulnerability reporting](https://github.com/rbtbuilds/casework-agent/security/advisories/new) when enabled. If it is unavailable, do not post sensitive details in a public issue; request a private reporting channel from the maintainer.
