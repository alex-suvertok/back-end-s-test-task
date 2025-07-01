import logging
from typing import Optional
from django.core.cache import cache
from main.models import Category

logger = logging.getLogger(__name__)


class CategoryMatcher:
    def __init__(self):
        self.cache_ttl = 3600  # 1 hour cache

    def find_category(
        self, category_name: str, product_name: str
    ) -> Optional[Category]:
        logger.info(
            f"Starting category search for category_name='{category_name}', product_name='{product_name}'"
        )

        if not category_name and not product_name:
            logger.warning("Both category_name and product_name are empty")
            return None

        cache_key = f"category_match_{category_name}_{product_name}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(
                f"Found cached category match: {cached_result.title} (ID: {cached_result.id})"
            )
            return cached_result

        if category_name:
            logger.info(f"Attempting exact match by category name: '{category_name}'")
            category = self._match_by_category_name(category_name)
            if category:
                logger.info(
                    f"Found exact category match: {category.title} (ID: {category.id})"
                )
                cache.set(cache_key, category, self.cache_ttl)
                return category
            else:
                logger.info("No exact category match found")

        if product_name:
            logger.info(f"Attempting keyword match by product name: '{product_name}'")
            category = self._match_by_product_name(product_name)
            if category:
                logger.info(
                    f"Found keyword category match: {category.title} (ID: {category.id})"
                )
                cache.set(cache_key, category, self.cache_ttl)
                return category
            else:
                logger.info("No keyword category match found")

        logger.warning(
            f"No category match found for category_name='{category_name}', product_name='{product_name}'"
        )

        return None

    def _match_by_category_name(self, category_name: str) -> Optional[Category]:
        normalized_name = category_name.strip()
        logger.debug(
            f"Searching for exact category match with normalized name: '{normalized_name}'"
        )

        try:
            category = Category.objects.get(
                title__iexact=normalized_name, is_active=True
            )
            logger.debug(
                f"Found exact category match: {category.title} (ID: {category.id})"
            )
            return category

        except Category.DoesNotExist:
            logger.debug(f"No category found with exact name: '{normalized_name}'")
            return None
        except Category.MultipleObjectsReturned:
            logger.warning(
                f"Multiple categories found with name: '{normalized_name}', skipping exact match"
            )
            return None
        except Exception as e:
            logger.error(f"Error during exact category match: {str(e)}")
            return None

    def _match_by_product_name(self, product_name: str) -> Optional[Category]:
        logger.debug(f"Starting keyword matching for product name: '{product_name}'")

        categories = Category.objects.filter(is_active=True, keywords__isnull=False)
        logger.debug(f"Found {categories.count()} active categories with keywords")

        best_match = None
        max_matches = 0

        product_words = set(
            word.lower()
            for word in product_name.split()
            if len(word) > 2 and not word.isdigit() and "test" not in word.lower()
        )
        logger.debug(f"Product words after filtering: {product_words}")

        for category in categories:
            if not category.keywords:
                continue

            logger.debug(
                f"Checking category '{category.title}' (ID: {category.id}) with keywords: {category.keywords}"
            )

            category_matches = 0

            for keyword_phrase in category.keywords:
                if not keyword_phrase:
                    continue

                logger.debug(f"Checking keyword phrase: '{keyword_phrase}'")

                keyword_words = set(
                    word.lower() for word in keyword_phrase.split() if len(word) > 2
                )
                logger.debug(f"Keyword words: {keyword_words}")

                if keyword_phrase.lower() in product_name.lower():
                    logger.info(
                        f"Found exact phrase match with keyword '{keyword_phrase}' in category '{category.title}'"
                    )
                    return category

                current_matches = len(keyword_words.intersection(product_words))

                if current_matches > 0:
                    match_percentage = current_matches / len(keyword_words)
                    if match_percentage >= 0.5:
                        category_matches = max(category_matches, current_matches)

            if category_matches > max_matches:
                max_matches = category_matches
                best_match = category
                logger.debug(
                    f"New best match: {category.title} with {category_matches} matches ({match_percentage * 100}% match)"
                )

        if best_match:
            logger.info(
                f"Best keyword match found: {best_match.title} (ID: {best_match.id}) with {max_matches} matches"
            )
        else:
            logger.info("No keyword matches found")
        return best_match if max_matches >= 2 else None

    def _normalize_text(self, text: str) -> str:
        if not text:
            logger.debug("Empty text provided for normalization")
            return ""
        normalized = text.lower().strip()
        logger.debug(f"Normalized text '{text}' to '{normalized}'")
        return normalized
