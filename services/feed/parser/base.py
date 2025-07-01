from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from xml.etree import ElementTree
from .types import ShopInfo, FeedCategory, FeedOffer
from ..exceptions import FeedParsingError
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class BaseFeedParser(ABC):
    def __init__(self, xml_content: str):
        self.xml_content = xml_content
        self._tree: Optional[ElementTree.Element] = None
        self._shop: Optional[ElementTree.Element] = None

    def parse(self) -> Tuple[ShopInfo, List[FeedCategory], List[FeedOffer]]:
        try:
            self._tree = ElementTree.fromstring(self.xml_content)
            self._shop = self._get_shop_element()

            shop_info = self.parse_shop_info()
            categories = self.parse_categories()
            offers = self.parse_offers()

            return shop_info, categories, offers

        except ElementTree.ParseError as e:
            raise FeedParsingError(f"Invalid XML format: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing feed: {str(e)}")
            raise FeedParsingError(f"Error parsing feed: {str(e)}")

    @abstractmethod
    def _get_shop_element(self) -> ElementTree.Element:
        pass

    @abstractmethod
    def parse_shop_info(self) -> ShopInfo:
        pass

    @abstractmethod
    def parse_categories(self) -> List[FeedCategory]:
        pass

    @abstractmethod
    def parse_offers(self) -> List[FeedOffer]:
        pass

    def _get_text(
        self,
        node: Optional[ElementTree.Element],
        tag: str,
        default: Optional[str] = None,
    ) -> Optional[str]:
        found = node.find(tag) if node is not None else None
        return found.text.strip() if found is not None and found.text else default

    def _get_decimal(
        self, element: ElementTree.Element, tag: str, default: Decimal = Decimal("0.0")
    ) -> Decimal:
        text = self._get_text(element, tag)
        if not text:
            return default
        try:
            return Decimal(text)
        except Exception as e:
            logger.warning(f"Invalid decimal for <{tag}>: '{text}' — {e}")
            return default

    def _get_int(self, element: ElementTree.Element, tag: str, default: int = 0) -> int:
        text = self._get_text(element, tag)
        if not text:
            return default
        try:
            return int(text)
        except Exception as e:
            logger.warning(f"Invalid integer for <{tag}>: '{text}' — {e}")
            return default

    def _get_bool(
        self, element: ElementTree.Element, attr: str, default: bool = True
    ) -> bool:
        value = element.get(attr)
        if value is None:
            return default
        return value.strip().lower() == "true"
