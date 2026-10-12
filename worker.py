"""The worker polls the task queue and runs workflow + activity code.

Run this in its own terminal and leave it running:
    ./venv/bin/python worker.py
"""
from __future__ import annotations

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activities import charge_payment, refund_payment, ship_order, validate_order
from shared import TASK_QUEUE
from workflows import OrderWorkflow


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[OrderWorkflow],
        activities=[validate_order, charge_payment, ship_order, refund_payment],
    )
    print(f"Worker started, polling task queue '{TASK_QUEUE}'. Ctrl+C to exit.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
