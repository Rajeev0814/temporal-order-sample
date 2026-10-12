"""Shared data structures and constants for the order processing sample."""
from __future__ import annotations

from dataclasses import dataclass, field

TASK_QUEUE = "order-processing-queue"


@dataclass
class OrderItem:
    sku: str
    name: str
    quantity: int
    unit_price: float


@dataclass
class OrderInput:
    order_id: str
    customer_id: str
    items: list[OrderItem] = field(default_factory=list)


@dataclass
class OrderResult:
    order_id: str
    status: str
    payment_id: str
    tracking_id: str
    total: float
