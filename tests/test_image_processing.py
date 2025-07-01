import hashlib
from hashlib import sha256
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from tasks.image_processing import compute_sha256
from tasks.image_processing import get_existing_image_hashes


@pytest.mark.django_db
def test_get_existing_image_hashes_returns_valid_hashes():
    content = b"fake image content"
    hash_val = sha256(content).hexdigest()

    product = baker.make("main.Product", feed_source__name="Test Feed")

    image_file = SimpleUploadedFile("test.jpg", content, content_type="image/jpeg")
    baker.make("main.ProductImage", product=product, image=image_file)

    result = get_existing_image_hashes(product)

    assert isinstance(result, set)
    assert hash_val in result


@patch("tasks.image_processing.fetch_image_bytes")
def test_compute_sha256_returns_correct_hash(mock_fetch):
    mock_fetch.return_value = b"test data"
    result = compute_sha256("http://example.com/image.jpg")
    expected = hashlib.sha256(b"test data").hexdigest()
    assert result == expected


@patch("tasks.image_processing.fetch_image_bytes", side_effect=Exception("fail"))
def test_compute_sha256_handles_failure(mock_fetch):
    result = compute_sha256("http://fail.com/image.jpg")
    assert result == ""
