import pytest
from model_bakery import baker

from main.models import Category
from services.product.category_matcher import CategoryMatcher


@pytest.mark.django_db
def test_keyword_matching():
    cat = baker.make(Category, title="Ножиці", keywords=["ножиці кухонні"])
    matcher = CategoryMatcher()
    matched = matcher.find_category("неіснуюча", "Ножиці кухонні з нержавійки")
    assert matched == cat
