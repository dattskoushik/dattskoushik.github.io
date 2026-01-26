# Designing Reliable Batch Data Pipelines

**Date:** September 2023
**Category:** Architecture

---

Building a script to move data from A to B is easy. Building a system that moves data from A to B *reliably*, at scale, while handling network failures, bad data, and restarts without corruption? That is engineering.

In the world of batch processing (ETL), "Reliability" usually boils down to two properties: **Resilience** (not crashing when things go wrong) and **Correctness** (not duplicating or losing data when things go wrong).

This article explores the patterns required to sleep well at night while your pipelines run.

## The Fallacy of "Retry Loop"

The naive approach to reliability is the retry loop.

```python
def process_data(batch):
    try:
        insert_to_db(batch)
    except Exception:
        time.sleep(5)
        process_data(batch)  # Retry
```

This works for transient network blips. But what if the failure is caused by a "Poison Pill"—a specific record that triggers a parser error? Infinite retries. The pipeline stalls.

What if the failure happens *after* insertion but *before* acknowledgement? You retry and insert the data twice. Duplicate data.

## 1. Idempotency: The Golden Rule

**Idempotency** means that applying an operation multiple times has the same result as applying it once. `f(f(x)) = f(x)`.

In data pipelines, this allows us to "replay" failed batches safely.

### Database Level Idempotency
The most robust way to ensure idempotency is relying on the destination's primary key constraints.

```sql
INSERT INTO daily_metrics (date, metric_id, value)
VALUES ('2023-10-27', 'active_users', 4500)
ON CONFLICT (date, metric_id)
DO UPDATE SET value = EXCLUDED.value;
```

This "Upsert" ensures that if we re-run the job for '2023-10-27', we verify the state rather than blindly appending.

### File Level Idempotency
When writing to object storage (S3), we cannot "update" files. We must rely on deterministic naming.

**Bad:** `s3://bucket/data/upload_timestamp.json` (Non-deterministic)
**Good:** `s3://bucket/data/partition_date/batch_id.json` (Deterministic)

## 2. Checkpointing and State Management

For long-running batch jobs (e.g., processing a huge log file), you cannot afford to restart from line 1 if it fails at line 999,999. You need **Checkpointing**.

We can maintain a separate state store (Redis, DynamoDB, or a Postgres table) to track progress.

```python
# Simplified Logic
last_processed_id = get_checkpoint("job_123")
records = fetch_source(after=last_processed_id)

for batch in chunk(records):
    process(batch)
    save_checkpoint("job_123", batch.last_id)
```

However, there is a race condition here. If `process(batch)` succeeds (writes to DB) but `save_checkpoint` fails (network error), the next run will re-process the batch.
**Solution:** Atomic Commit. If the destination supports transactions (like Postgres), write the data AND the checkpoint in the same transaction.

## 3. The Dead Letter Queue (DLQ)

What do you do with bad data? If 1 row in a batch of 10,000 is malformed, should you fail the whole batch? Usually, no.

The pattern is to **quarantine** the bad data.

```python
def process_batch(records):
    valid_records = []
    failed_records = []

    for record in records:
        try:
            validate(record)
            valid_records.append(record)
        except ValidationError as e:
            failed_records.append({"data": record, "error": str(e)})

    bulk_insert(valid_records)
    send_to_dlq(failed_records)
```

The DLQ (Dead Letter Queue) can be an S3 bucket or a separate queue. It allows the pipeline to proceed while preserving the evidence for debugging.

## Code Example: Robust Log Ingestion

Let's look at a snippet inspired by a log ingestion system I built (see full code in `assets/code_reference/log-parser`).

We use **Pydantic** for strict validation at the edge. This ensures that "poison pills" are caught early, before they enter the database.

```python
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from enum import Enum

class LogSeverity(str, Enum):
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'

class LogEntry(BaseModel):
    timestamp: datetime
    severity: LogSeverity
    module: str = Field(min_length=1)
    message: str

def parse_and_quarantine(raw_logs):
    valid = []
    quarantine = []

    for log_line in raw_logs:
        try:
            # Pydantic handles type coercion and validation
            parsed = parse_regex(log_line)
            entry = LogEntry(**parsed)
            valid.append(entry.dict())
        except ValidationError as e:
            quarantine.append({"raw": log_line, "error": e.errors()})

    return valid, quarantine
```

By segregating the data immediately, we protect the downstream analytical storage (Warehouse) from schema violations.

## 4. Backfilling: The Time Travel Problem

Pipelines don't just process *new* data. Often, business logic changes ("We need to calculate the metric differently"). You need to **Backfill** historical data.

This is where Idempotency pays off. If your pipeline is idempotent, a backfill is just "running the job for past dates".

**Key Strategy:** Decouple "Execution Time" from "Data Time".
Never use `datetime.now()` inside your transformation logic. Always pass the `data_date` as a parameter.

```python
# BAD
def calculate_daily_revenue():
    today = datetime.now().date()
    ...

# GOOD
def calculate_daily_revenue(target_date: date):
    ...
```

This allows you to run `calculate_daily_revenue('2023-01-01')` regardless of the actual wall-clock time.

## Conclusion

Reliable pipelines are boring. They don't crash on bad input; they just sidebar it. They don't double-count data on retries; they upsert. They don't fear restarts; they checkpoint.

As engineers, our job is to anticipate failure. By designing for idempotency and observability (DLQs), we build systems that recover automatically, allowing us to focus on the next interesting problem.
