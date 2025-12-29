import pytest
from django.core.management import call_command
from content.models import Item

@pytest.mark.django_db
def test_seed_items_command_creates_published_items():
    call_command("seed_items", count=10, published=True)
    assert Item.objects.count() == 10
    assert Item.objects.filter(status=Item.Status.PUBLISHED).count() == 10
    assert Item.objects.filter(published_at__isnull=True).count() == 0
