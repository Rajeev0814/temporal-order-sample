"""Activities: the side-effecting steps of the order workflow.

Activities are plain functions where real-world work happens (DB calls, payment
APIs, sending emails). Temporal automatically retries them on failure according
to the retry policy configured in the workflow.
"""
from __future__ import annotations

import asyncio

from temporalio import activity
from temporalio.exceptions import ApplicationError

from shared import OrderInput


@activity.defn
async def validate_order(order: OrderInput) -> float:
    """Validate the order and return its total. Raises if the order is invalid."""
    activity.logger.info("Validating order %s", order.order_id)
    if not order.items:
        # Non-retryable: retrying an empty order will never succeed.
        raise ApplicationError("Order has no items", non_retryable=True)

    total = sum(item.unit_price * item.quantity for item in order.items)
    if total <= 0:
        raise ApplicationError("Order total must be positive", non_retryable=True)

    await asyncio.sleep(0.5)  # simulate work
    activity.logger.info("Order %s validated, total=%.2f", order.order_id, total)
    return round(total, 2)


@activity.defn
async def charge_payment(order: OrderInput, amount: float) -> str:
    """Charge the customer and return a payment id."""
    activity.logger.info("Charging %.2f for order %s", amount, order.order_id)
    await asyncio.sleep(1)  # simulate calling a payment gateway
    payment_id = f"pay_{order.order_id}"
    activity.logger.info("Payment %s succeeded", payment_id)
    return payment_id


@activity.defn
async def ship_order(order: OrderInput) -> str:
    """Hand the order to the warehouse and return a tracking id."""
    activity.logger.info("Shipping order %s", order.order_id)
    await asyncio.sleep(1)  # simulate warehouse/carrier call
    tracking_id = f"trk_{order.order_id}"
    activity.logger.info("Order %s shipped, tracking=%s", order.order_id, tracking_id)
    return tracking_id


@activity.defn
async def refund_payment(payment_id: str) -> None:
    """Compensation step: refund a payment if a later step fails."""
    activity.logger.info("Refunding payment %s", payment_id)
    await asyncio.sleep(0.5)
    activity.logger.info("Payment %s refunded", payment_id)
