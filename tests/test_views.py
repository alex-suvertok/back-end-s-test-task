import pytest
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_product_list_view():
    baker.make("main.Product", _quantity=3, is_active=True)
    client = APIClient()
    response = client.get("/uk/api/v1/products/")
    assert response.status_code == 200
    assert "results" in response.data


@pytest.mark.django_db
def test_category_list_view():
    baker.make("main.Category", _quantity=2)
    client = APIClient()
    response = client.get("/uk/api/v1/categories/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_detail_view_without_attributes():
    product = baker.make("main.Product", is_active=True)
    client = APIClient()
    response = client.get(f"/uk/api/v1/products/{product.id}/")
    assert response.status_code == 200
    assert response.data["id"] == product.id


@pytest.mark.django_db
def test_popular_categories_view_returns_sorted_results():
    category1 = baker.make("main.Category", title="Телефони")
    category2 = baker.make("main.Category", title="Ноутбуки")

    baker.make("main.Product", category=category1, is_active=True, views_count=100)
    baker.make("main.Product", category=category1, is_active=True, views_count=200)
    baker.make("main.Product", category=category2, is_active=True, views_count=50)

    client = APIClient()
    response = client.get("/uk/api/v1/stats/categories/popular/")

    assert response.status_code == 200
    data = response.data

    assert len(data) == 2
    assert data == [
        {"id": category1.id, "title": category1.title, "product_count": 2},
        {"id": category2.id, "title": category2.title, "product_count": 1},
    ]
