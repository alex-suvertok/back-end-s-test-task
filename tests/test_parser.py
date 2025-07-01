import pytest

from services.feed.parser.rozetka import RozetkaFeedParser


@pytest.mark.django_db
def test_rozetka_parser_parses_basic_feed(sample_feed_content):
    parser = RozetkaFeedParser(sample_feed_content)
    shop_info, categories, offers = parser.parse()

    assert shop_info.name
    assert len(categories) > 0
    assert len(offers) > 0


@pytest.fixture
def sample_feed_content():
    return """
    <yml_catalog date="2024-01-01 00:00">
      <shop>
        <name>Test Shop</name>
        <company>Test Company</company>
        <url>http://example.com</url>
        <categories>
          <category id="1">Смартфони</category>
        </categories>
        <offers>
          <offer id="123" available="true">
            <name>Тестовий смартфон</name>
            <price>5000</price>
            <currencyId>UAH</currencyId>
            <categoryId>1</categoryId>
            <url>http://example.com/product</url>
          </offer>
        </offers>
      </shop>
    </yml_catalog>
    """
