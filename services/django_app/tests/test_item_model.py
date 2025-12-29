import pytest
from content.models import Item

@pytest.mark.django_db
def test_item_defaults():
    item = Item.objects.create(title="Hello")
    assert item.status == Item.Status.DRAFT
    assert item.tags == []
    assert item.published_at is None
