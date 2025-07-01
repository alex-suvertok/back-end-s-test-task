import logging
import tempfile
from datetime import timedelta
from typing import List, Tuple
from urllib.request import urlopen

from django.core.files import File
from django.db import transaction
from django.utils import timezone

from main.models import (
    Attribute,
    AttributeValue,
    Category,
    FeedParsingReport,
    FeedSource,
    Product,
    ProductAttribute,
    ProductImage,
)
from main.models.store.feed import FeedParsingReportItem
from services.feed.exceptions import FeedDownloadError, FeedParsingError
from services.feed.feed_downloader import FeedDownloader
from services.feed.parser.rozetka import RozetkaFeedParser
from services.feed.parser.types import FeedCategory, FeedOffer, ShopInfo
from services.product.attribute_matcher import AttributeMatcher
from services.product.category_matcher import CategoryMatcher

logger = logging.getLogger(__name__)


class FeedManager:
    def __init__(self, feed_source: FeedSource):
        self.feed_source = feed_source
        self.stats = {
            "total_products": 0,
            "products_added": 0,
            "products_updated": 0,
            "products_failed": 0,
            "products_unpublished": 0,
        }
        self.attribute_matcher = AttributeMatcher()
        self.categories = []
        self.current_report = None

    def process_feed(self) -> FeedParsingReport:
        report = FeedParsingReport.objects.create(
            feed=self.feed_source,
            status=FeedParsingReport.Status.STARTED,
            started_at=timezone.now(),
        )
        logger.info(
            f"Starting feed processing: {self.feed_source.name} (ID: {self.feed_source.id})"
        )
        try:
            content = self._download_feed()
            logger.info(f"Downloaded feed: {self.feed_source.xml_url}")
            shop_info, self.categories, offers = self._parse_feed(content)
            logger.info(f"Parsed {len(offers)} offers from feed")
            with transaction.atomic():
                self.current_report = report
                self._process_offers(offers)
                new_ids = {offer.external_id for offer in offers}

                archived_count = (
                    Product.objects.filter(
                        feed_source=self.feed_source,
                        is_active=True,
                    )
                    .exclude(external_id__in=new_ids)
                    .update(status=Product.Status.ARCHIVED)
                )

                logger.info(
                    f"Archived {archived_count} products that were missing in the feed."
                )

            self._update_next_sync()
            self._complete_report(report)
            logger.info(f"Completed feed processing: {self.feed_source.name}")
            return report
        except (FeedDownloadError, FeedParsingError) as e:
            logger.error(f"Error processing feed {self.feed_source.id}: {str(e)}")
            self._fail_report(report, str(e))
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error processing feed {self.feed_source.id}: {str(e)}"
            )
            self._fail_report(report, str(e))
            raise

    def _download_feed(self) -> str:
        downloader = FeedDownloader(self.feed_source.xml_url)
        return downloader.download()

    def _parse_feed(
        self, content: str
    ) -> Tuple[ShopInfo, List[FeedCategory], List[FeedOffer]]:
        parser = RozetkaFeedParser(content)
        return parser.parse()

    def _update_next_sync(self):
        self.feed_source.last_update = timezone.now()
        self.feed_source.next_update = timezone.now() + timedelta(
            hours=self.feed_source.frequency
        )
        self.feed_source.save()

    def _complete_report(self, report: FeedParsingReport):
        report.status = FeedParsingReport.Status.SUCCESS
        report.finished_at = timezone.now()
        report.total_products = self.stats["total_products"]
        report.products_added = self.stats["products_added"]
        report.products_updated = self.stats["products_updated"]
        report.products_failed = self.stats["products_failed"]
        report.products_unpublished = self.stats["products_unpublished"]
        report.save()

    def _fail_report(self, report: FeedParsingReport, error: str):
        report.status = FeedParsingReport.Status.ERROR
        report.finished_at = timezone.now()
        report.parsing_error = error
        report.save()

    def _process_offers(self, offers: List[FeedOffer]):
        for offer in offers:
            self._process_offer(offer)
        self.stats["total_products"] = len(offers)

    def _process_offer(self, offer: FeedOffer) -> None:
        self.stats["total_products"] += 1

        logger.info(f"Processing offer {offer.external_id}")
        try:
            with transaction.atomic():
                defaults = {
                    "name": offer.name or "",
                    "vendor": offer.vendor or "",
                    "article": offer.article or "",
                    "description": offer.description or "",
                    "price": offer.price,
                    "currency": offer.currency or "UAH",
                    "stock_quantity": offer.stock_quantity,
                    "available": offer.available,
                    "url": offer.url or "",
                    "status": Product.Status.DRAFT,
                }

                product_qs = Product.objects.select_for_update().filter(
                    feed_source=self.feed_source, external_id=offer.external_id
                )
                if product_qs.exists():
                    product = product_qs.first()
                    created = False
                else:
                    product = Product.objects.create(
                        feed_source=self.feed_source,
                        external_id=offer.external_id,
                        **defaults,
                    )
                    created = True

                if not created:
                    for key, value in defaults.items():
                        setattr(product, key, value)
                    self.stats["products_updated"] += 1
                else:
                    self.stats["products_added"] += 1

                if not hasattr(self, "category_map"):
                    self.category_map = {c.external_id: c.name for c in self.categories}

                category_name = self.category_map.get(offer.category_id)
                category = CategoryMatcher().find_category(category_name, offer.name)

                if not category and category_name:
                    category, created = Category.objects.get_or_create(
                        title=category_name.strip(), defaults={"is_active": True}
                    )
                    if created:
                        logger.info(
                            f"Created fallback category '{category.title}' from feed"
                        )

                if not category:
                    logger.warning(
                        f"Skipping product {offer.external_id} due to missing category"
                    )
                    self.stats["products_unpublished"] += 1
                    return

                product.category = category

                if (
                    product.name
                    and product.price > 0
                    and offer.pictures
                    and product.category
                ):
                    if product.status != Product.Status.ACTIVE:
                        product.published_at = timezone.now()
                    product.status = Product.Status.ACTIVE
                else:
                    product.status = Product.Status.DRAFT

                if not product.available and product.status == Product.Status.ACTIVE:
                    product.status = Product.Status.ARCHIVED
                    self.stats["products_unpublished"] += 1

                self._process_attributes(product, offer.attributes)

                product.save()

                if offer.pictures:
                    logger.info(f"Processing offer {offer.external_id} images")
                    transaction.on_commit(
                        lambda: self._process_images(product, offer.pictures)
                    )

        except Exception as e:
            logger.error(f"Failed to process offer {offer.external_id}: {str(e)}")

            FeedParsingReportItem.objects.create(
                report=self.current_report,
                product_external_id=offer.external_id,
                success=False,
                error_message=str(e),
            )
            self.stats["products_failed"] += 1

    def _process_attributes(self, product: Product, attributes: dict) -> None:
        if not attributes:
            return

        for attr_name, attr_values in attributes.items():
            try:
                attr_match = self.attribute_matcher.find_attribute(attr_name)
                if not attr_match:
                    logger.warning(f"Attribute '{attr_name}' not matched.")
                    continue

                try:
                    attribute = Attribute.objects.select_for_update().get(
                        id=attr_match["attribute_id"]
                    )
                except Attribute.DoesNotExist:
                    logger.warning(
                        f"Attribute with ID {attr_match['attribute_id']} not found in DB"
                    )
                    continue

                values_list = (
                    attr_values if isinstance(attr_values, list) else [attr_values]
                )

                for single_value in values_list:
                    try:
                        value_match = self.attribute_matcher.find_or_create_value(
                            attribute, single_value
                        )
                        if not value_match:
                            logger.warning(
                                f"Value '{single_value}' for attribute '{attr_name}' not matched or created."
                            )
                            continue

                        attribute_value = (
                            AttributeValue.objects.select_for_update().get(
                                id=value_match["value_id"]
                            )
                        )

                        ProductAttribute.objects.update_or_create(
                            product=product,
                            attribute=attribute,
                            value=attribute_value,
                            defaults={"raw_value": str(single_value)},
                        )
                    except Exception as e:
                        logger.error(
                            f"[ValueError] '{single_value}' in '{attr_name}' → {str(e)}"
                        )

            except Exception as e:
                logger.error(f"[AttributeError] '{attr_name}' → {str(e)}")

    def _process_images(self, product: Product, image_urls: List[str]) -> None:
        from tasks.image_processing import download_product_images

        download_product_images.delay(product.id, image_urls)

        existing_urls = sorted(
            [img.image.url for img in product.images.all() if img.image]
        )
        new_urls = sorted(image_urls)

        if existing_urls == new_urls:
            logger.info(
                f"Skipping image update for product {product.id}, no changes detected."
            )
            return

        ProductImage.objects.filter(product=product).delete()

        for i, image_url in enumerate(image_urls):
            try:
                temp_image = tempfile.NamedTemporaryFile(
                    delete=True, dir=tempfile.gettempdir()
                )
                temp_image.write(urlopen(image_url).read())
                temp_image.flush()

                product_image = ProductImage(product=product, position=i)
                product_image.image.save(
                    f"{product.external_id}_{i}.jpg", File(temp_image)
                )
                product_image.save()

            except Exception as e:
                logger.warning(
                    f"Failed to download or save image {image_url}: {str(e)}"
                )

    def _deserialize_offer(self, offer_data: dict) -> FeedOffer:
        return FeedOffer(**offer_data)
