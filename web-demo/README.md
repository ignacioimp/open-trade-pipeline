# Browser demo — commercial and execution workflows

Open [index.html](index.html) in a modern browser after cloning/downloading the repository. No packages, backend or external services are needed. The browser demo is inspired by two earlier standalone HTML applications: a commercial Kanban and a separate execution Kanban. The original private files are not included. This new implementation uses generalized task labels and fictional records only; it is independent from the Python CLI and its JSON format.

## Features

- Two boards, sequential stages and explicit handoff after Closed Won.
- Operator-confirmed payment gate before costing; no arbitrary stage jumps.
- Per-stage task checklists, task owners, case owner, follow-up date, blockers and activity history.
- Temporary return to Intake to resolve missing information; validation and restoration of the prior phase's checklist.
- Local browser persistence, search, JSON export and reset.

## Verification and limitations

Ten model-level JavaScript checks executed during development and passed: initial stage, task gate, payment blocked/allowed, handoff blocked/allowed, closed-lost terminal state, return from intake retaining tasks, nested request rejection, and terminal execution stage. Browser rendering and end-to-end UI interactions were not independently tested. The demo intentionally omits the original detailed company-specific task lists, regulatory conditions, personal/customer fields, actual records, internal URLs, integrations, and JSON import. No payment is processed or verified. Local storage is not encrypted; exported JSON is not a secure backup. Do not enter real customer information. No production security, concurrency support, browser compatibility benchmark or measured commercial outcomes are claimed.

## Architecture

The domain model enforces transitions and is separate from the DOM rendering layer inside the self-contained HTML. The browser storage adapter persists demo cases. The original Python engine remains unchanged.
