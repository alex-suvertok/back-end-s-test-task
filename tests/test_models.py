import pytest
from model_bakery import baker


@pytest.mark.django_db
def test_product_str():
    product = baker.make("main.Product", name="Test Product")
    assert str(product) == "Test Product"


@pytest.mark.django_db
def test_category_str():
    category = baker.make("main.Category", title="Category")
    assert str(category) == "Category"
