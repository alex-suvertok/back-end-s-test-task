import logging
import tempfile

import requests
from celery import group, shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

from main.models import FeedSource, Product
from services.feed.core.manager import FeedManager

logger = logging.getLogger(__name__)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_feed(feed_source_id: int):
    try:
        feed_source = FeedSource.objects.get(id=feed_source_id)
        logger.info(f"[Feed {feed_source_id}] Starting processing")
        report = FeedManager(feed_source).process_feed()
        logger.info(f"[Feed {feed_source_id}] Completed with report ID {report.id}")
        return {"status": "success", "report_id": report.id}
    except Exception as e:
        logger.exception(f"[Feed {feed_source_id}] Failed to process: {e}")
        raise e


@shared_task
def process_all_feeds():
    logger.info("Starting batch processing of feeds")
    now = timezone.now()
    feed_sources = FeedSource.objects.filter(is_active=True, next_update__lte=now)

    if not feed_sources.exists():
        logger.info("No feeds to process")
        return {"dispatched_tasks": 0}

    logger.info(f"Found {feed_sources.count()} feeds to process")

    tasks = group(process_feed.s(feed.id) for feed in feed_sources)
    result = tasks.apply_async()

    return {"dispatched_tasks": len(result.results)}
