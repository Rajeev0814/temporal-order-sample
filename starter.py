"""Starts an OrderWorkflow execution and waits for the result.

Run this after the worker is up:
    ./venv/bin/python starter.py
"""
from __future__ import annotations

import asyncio
import uuid

from temporalio.client import Client

from shared import TASK_QUEUE, OrderInput, OrderItem
from workflows import OrderWorkflow


async def main() -> None:
    client = await Client.connect("localhost:7233")

    order = OrderInput(
        order_id=f"order-{uuid.uuid4().hex[:8]}",
        customer_id="cust-1001",
        items=[
            OrderItem(sku="SKU-1", name="Mechanical Keyboard", quantity=1, unit_price=89.99),
            OrderItem(sku="SKU-2", name="USB-C Cable", quantity=2, unit_price=9.50),
        ],
    )

    handle = await client.start_workflow(
        OrderWorkflow.run,
        order,
        id=f"order-wf-{order.order_id}",
        task_queue=TASK_QUEUE,
    )
    print(f"Started workflow. id={handle.id} run_id={handle.result_run_id}")

    # Demonstrate a query while the workflow runs.
    status = await handle.query(OrderWorkflow.status)
    print(f"Current status (queried): {status}")

    result = await handle.result()
    print("\n=== Order completed ===")
    print(f"  order_id:   {result.order_id}")
    print(f"  status:     {result.status}")
    print(f"  total:      ${result.total:.2f}")
    print(f"  payment_id: {result.payment_id}")
    print(f"  tracking:   {result.tracking_id}")


if __name__ == "__main__":
    asyncio.run(main())
