from datetime import datetime
from typing import List, Dict, Any
from xml.etree import ElementTree

from .base import BaseFeedParser
from .types import ShopInfo, FeedCategory, FeedOffer
from ..exceptions import FeedParsingError
import logging

logger = logging.getLogger(__name__)


class RozetkaFeedParser(BaseFeedParser):
    def _get_shop_element(self) -> ElementTree.Element:
        shop = self._tree.find(".//shop")
        if shop is None:
            raise FeedParsingError("Required <shop> element not found")
        return shop

    def parse_shop_info(self) -> ShopInfo:
        date_str = self._tree.get("date", "")
        try:
            date = (
                datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                if date_str
                else datetime.now()
            )
        except ValueError:
            logger.warning(f"Invalid date format {date_str}, using current time")
            date = datetime.now()

        return ShopInfo(
            name=self._get_text(self._shop, "name", ""),
            company=self._get_text(self._shop, "company", ""),
            url=self._get_text(self._shop, "url", ""),
            date=date,
        )

    def parse_categories(self) -> List[FeedCategory]:
        categories = []
        categories_node = self._shop.find(".//categories")
        if categories_node is None:
            return categories

        for category in categories_node.findall("category"):
            category_id = category.get("id")
            if not category_id:
                logger.warning("Category without ID skipped")
                continue

            categories.append(
                FeedCategory(
                    external_id=category_id,
                    name=self._get_text(category, ".", ""),
                    rozetka_id=category.get("rz_id"),
                )
            )
        return categories

    def parse_offers(self) -> List[FeedOffer]:
        offers = []
        offers_node = self._shop.find(".//offers")
        if offers_node is None:
            return offers

        for offer in offers_node.findall("offer"):
            try:
                offer_data = self._parse_offer(offer)
                offers.append(offer_data)
            except (ValueError, TypeError, FeedParsingError) as e:
                logger.warning(
                    f"Skipping invalid offer {offer.get('id', 'unknown')}: {str(e)}"
                )
                continue
        return offers

    def _parse_offer(self, offer: ElementTree.Element) -> FeedOffer:
        external_id = offer.get("id")
        if not external_id:
            raise ValueError("Offer must have ID")

        price = self._get_decimal(offer, "price")
        if not price or price <= 0:
            raise ValueError(f"Offer {external_id} must have a valid positive price")

        name = self._get_text(offer, "name")
        if not name:
            raise ValueError(f"Offer {external_id} is missing <name>")

        pictures = [
            p.text.strip()
            for p in offer.findall("picture")
            if p.text and p.text.strip()
        ]

        return FeedOffer(
            external_id=external_id,
            available=self._get_bool(offer, "available"),
            url=self._get_text(offer, "url", ""),
            price=price,
            currency=self._get_text(offer, "currencyId", "UAH"),
            category_id=self._get_text(offer, "categoryId", ""),
            name=name,
            pictures=pictures,
            vendor=self._get_text(offer, "vendor"),
            description=self._get_text(offer, "description"),
            article=self._get_text(offer, "article"),
            attributes=self._parse_attributes(offer),
            stock_quantity=self._get_int(offer, "stock_quantity"),
        )

    def _parse_attributes(self, offer: ElementTree.Element) -> Dict[str, Any]:
        attributes = {}
        for param in offer.findall("param"):
            name = param.get("name")
            if name and param.text:
                if name in attributes:
                    if isinstance(attributes[name], list):
                        attributes[name].append(param.text)
                    else:
                        attributes[name] = [attributes[name], param.text]
                else:
                    attributes[name] = param.text
        return attributes
