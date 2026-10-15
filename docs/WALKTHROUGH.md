# Two-minute walkthrough guide

This is a presenter guide, not a claim that a two-minute recording exists. Real screenshots are in `docs/evidence`.

- 0:00-0:20: Show the Fictional records banner and Fixture workflow label. Open the delayed delivery example. Explain that all integrations use real local HTTP but the business data is fictional.
- 0:20-0:45: Inspect the order, carrier and policy evidence. Expand one source record and show its ID, version and hash. The model can read these records and propose; it cannot write.
- 0:45-1:05: Show the exact note, action, source versions, expiry and proposal hash. Approve using the keyboard. Approval creates durable authority before the first network write.
- 1:05-1:30: Show both confirmed outcomes and the audit timeline. In the browser test configuration, each service drops its first post-commit response; the unknown event is followed by journal confirmation, leaving one effect per key.
- 1:30-1:45: Explain the partial-conflict test: a ticket can exist while the order annotation is rejected. The interface shows review_required instead of pretending both writes completed.
- 1:45-2:00: Compare the frozen fixture and Qwen reports. State the actual model failure and pending human review clearly. This is an engineering simulation, with no measured customer savings or production deployment.
