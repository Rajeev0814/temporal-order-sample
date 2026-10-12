"""The OrderWorkflow orchestrates the order-processing steps.

Workflow code must be deterministic, so all I/O happens inside activities.
This workflow shows:
  * sequential activities with a shared retry policy
  * the saga / compensation pattern (refund payment if shipping fails)
  * a query to inspect progress while the workflow is running
"""
from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import (
        charge_payment,
        refund_payment,
        ship_order,
        validate_order,
    )
    from shared import OrderInput, OrderResult


@workflow.defn
class OrderWorkflow:
    def __init__(self) -> None:
        self._status = "PENDING"

    @workflow.query
    def status(self) -> str:
        """Queryable current status of the order."""
        return self._status

    @workflow.run
    async def run(self, order: OrderInput) -> OrderResult:
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            maximum_attempts=3,
        )
        common = dict(
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy,
        )

        # 1. Validate
        self._status = "VALIDATING"
        total = await workflow.execute_activity(validate_order, order, **common)

        # 2. Charge payment
        self._status = "CHARGING_PAYMENT"
        payment_id = await workflow.execute_activity(
            charge_payment, args=[order, total], **common
        )

        # 3. Ship — compensate (refund) if this fails permanently.
        try:
            self._status = "SHIPPING"
            tracking_id = await workflow.execute_activity(ship_order, order, **common)
        except Exception:
            self._status = "REFUNDING"
            await workflow.execute_activity(refund_payment, payment_id, **common)
            self._status = "FAILED_REFUNDED"
            raise

        self._status = "COMPLETED"
        return OrderResult(
            order_id=order.order_id,
            status=self._status,
            payment_id=payment_id,
            tracking_id=tracking_id,
            total=total,
        )
