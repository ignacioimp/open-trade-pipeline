# Open Trade Pipeline

Local Python prototype for managing a trade-service engagement from initial inquiry to commercial handoff and then through execution milestones. It preserves the principle that pipeline stage says where the case is, and tasks say what to do next. Cost estimation starts only after the operator confirms payment.

## Browser demo

A standalone visual version inspired by the original commercial and execution boards is available in [web-demo](web-demo/README.md). Open `web-demo/index.html` locally to explore the two boards with synthetic data. The Python CLI and browser demo use independent state formats.

## Quick start

Python 3.10+, no dependencies or accounts. Run from repository root:

```sh
sh examples/demo.sh /tmp/trade-demo.json
python -m unittest discover -s tests -v
```

Use a new state filename each time. For Windows, run the individual Python commands shown in the example script. `python pipeline.py --help` lists commands.

## Workflow

New Inquiry → Diagnostic Started → Diagnostic Completed → Cost Estimate Started → Cost Estimate Sent → Proposal Accepted → Closed Won. Closed Lost is available from any active stage with a reason. Every active stage begins with a task and a due date. Complete outstanding tasks before advancing; the report flags an active case with no pending task, and highlights overdue work and missing payment. `payment` records an operator-confirmed reference; it does not process or verify a financial transaction. Once won, explicitly start a separate operational handoff and move one milestone at a time with evidence.

The local JSON file acts as a portable backup. Keep it private: no actual case records belong in the public repository. Use synthetic IDs and evidence labels for demos. A local JSON store and single-process writes are intentional; there is no multi-user locking, authentication, encryption or externally verified payment integration. No CRM, WhatsApp or production system is connected.

See [architecture](docs/architecture.md) and [test results](docs/test_results.md). This is a new Python implementation of previously explored workflow concepts, not a copy of the private production system or an earlier HTML app. Portfolio prototype by Ignacio Imperatrice. No open-source license is granted by this repository.
