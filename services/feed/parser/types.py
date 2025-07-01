from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional


@dataclass
class ShopInfo:
    name: str
    company: str
    url: str
    date: datetime


@dataclass
class FeedCategory:
    external_id: str
    name: str
    rozetka_id: Optional[str] = None


@dataclass
class FeedOffer:
    external_id: str
    available: bool
    url: str
    price: Decimal
    currency: str
    category_id: str
    name: str

    pictures: List[str] = field(default_factory=list)
    vendor: Optional[str] = None
    description: Optional[str] = None
    article: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    stock_quantity: int = 0
