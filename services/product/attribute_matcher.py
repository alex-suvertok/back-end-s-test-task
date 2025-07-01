from typing import Optional, Any, TypedDict
from django.core.cache import cache
from main.models import Attribute, AttributeValue
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class AttributeMatch(TypedDict):
    attribute_id: int
    value: str


class ValueMatch(TypedDict):
    value_id: int
    value: str


class AttributeMatcher:
    def __init__(self):
        self.cache_ttl = 3600

    def find_attribute(self, name: str) -> Optional[AttributeMatch]:
        if not name:
            return None

        cache_key = f"attr_match_{name}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        attributes = Attribute.objects.filter(title=name, is_active=True)

        if attributes.exists():
            if attributes.count() > 1:
                attribute = attributes.order_by("id").first()
                logger.warning(
                    f"Found multiple attributes with title '{name}', using ID {attribute.id}"
                )
            else:
                attribute = attributes.first()
        else:
            attribute = Attribute.objects.create(
                title=name, label=name, value_type="text", sort_order=0
            )

        match = AttributeMatch(attribute_id=attribute.id, value=name)
        cache.set(cache_key, match, self.cache_ttl)
        return match

    @transaction.atomic
    def find_or_create_value(
        self, attribute: Attribute, raw_value: Any
    ) -> Optional[ValueMatch]:
        if raw_value is None:
            return None

        value_str = str(raw_value).strip()
        if not value_str:
            return None

        cache_key = f"attr_val_match_{attribute.id}_{value_str}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        values = AttributeValue.objects.filter(
            attribute=attribute, title=value_str, is_active=True
        )

        if values.exists():
            if values.count() > 1:
                value = values.order_by("id").first()
                logger.warning(
                    f"Found multiple values '{value_str}' for attribute {attribute.id}, using ID {value.id}"
                )
            else:
                value = values.first()
        else:
            value = AttributeValue.objects.create(
                attribute=attribute,
                title=value_str,
                label=value_str,
                value_text=value_str,
                sort_order=0,
            )

        match = ValueMatch(value_id=value.id, value=value_str)
        cache.set(cache_key, match, self.cache_ttl)
        return match
