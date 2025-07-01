import hashlib
import logging
import tempfile
import time

import requests
from celery import shared_task
from django.core.files import File
from django.db.models import Prefetch

from main.models import Product, ProductImage

logger = logging.getLogger(__name__)


def fetch_image_bytes(url: str) -> bytes:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://google.com",
    }
    time.sleep(0.3)
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.content


def compute_sha256(url: str) -> str:
    try:
        content = fetch_image_bytes(url)
        return hashlib.sha256(content).hexdigest()
    except Exception as e:
        logger.warning(f"[HASH] Failed to compute hash for {url}: {str(e)}")
        return ""


def get_existing_image_hashes(product) -> set[str]:
    hashes = set()
    for img in product.images.all():
        try:
            if not img.image:
                continue
            with img.image.open("rb") as f:
                content = f.read()
                hashes.add(hashlib.sha256(content).hexdigest())
        except Exception as e:
            logger.warning(f"[HASH] Failed to read image {img.id}: {str(e)}")
    return hashes


@shared_task
def download_product_images(product_id, image_urls):
    try:
        product = Product.objects.prefetch_related(
            Prefetch("images", ProductImage.objects.only("image"))
        ).get(id=product_id)

        existing_hashes = get_existing_image_hashes(product)
        new_hashes = {compute_sha256(url) for url in image_urls}

        if new_hashes == existing_hashes:
            logger.info(
                f"[SKIP] No image changes for product {product.id} (hash match)"
            )
            return

        ProductImage.objects.filter(product=product).delete()

        for i, image_url in enumerate(image_urls):
            try:
                content = fetch_image_bytes(image_url)
                with tempfile.NamedTemporaryFile(delete=True) as temp_image:
                    temp_image.write(content)
                    temp_image.flush()

                    product_image = ProductImage(product=product, position=i)
                    product_image.image.save(
                        f"{product.external_id}_{i}.jpg", File(temp_image)
                    )
                    product_image.save()
            except Exception as e:
                logger.warning(f"[IMG] Failed to download {image_url}: {str(e)}")

    except Product.DoesNotExist:
        logger.error(f"[IMG] Product with ID {product_id} not found.")
