# Temporal Order Processing Sample (Python)

A minimal but realistic Temporal sample that processes an order through three
steps — **validate → charge payment → ship** — with automatic retries and a
compensation (saga) step that refunds the payment if shipping fails.

## Files

| File            | Purpose                                                        |
|-----------------|----------------------------------------------------------------|
| `shared.py`     | Dataclasses (`OrderInput`, `OrderResult`) and the task queue name |
| `activities.py` | The side-effecting steps (validate, charge, ship, refund)      |
| `workflows.py`  | `OrderWorkflow` orchestration + a `status` query + saga compensation |
| `worker.py`     | Worker that hosts the workflow and activities                  |
| `starter.py`    | Client that starts a workflow and prints the result           |

## Setup

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Run

1. **Start the Temporal dev server** (bundled with the Temporal CLI):

   ```bash
   temporal server start-dev
   ```

   Web UI: http://localhost:8233  •  gRPC: localhost:7233

2. **Start the worker** (new terminal):

   ```bash
   ./venv/bin/python worker.py
   ```

3. **Kick off a workflow** (new terminal):

   ```bash
   ./venv/bin/python starter.py
   ```

You'll see the order run through each step and a final `COMPLETED` result.
Open the Web UI to inspect the workflow history, activity retries, and queries.

## Concepts demonstrated

- **Workflow / Activity separation** — deterministic orchestration vs. I/O
- **Retry policies** — automatic retries with backoff and `maximum_attempts`
- **Non-retryable errors** — invalid orders fail fast via `ApplicationError`
- **Saga / compensation** — refund payment if shipping fails permanently
- **Queries** — inspect live workflow status without affecting execution
