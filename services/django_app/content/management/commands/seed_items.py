import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from content.models import Item


WORDS = [
    "payments", "fraud", "growth", "market", "cloud", "python", "django", "fastapi",
    "vector", "ranking", "personalization", "feature", "data", "latency", "cache",
]

AUTHORS = ["alice", "bob", "carol", "dave", "eve"]


def make_title(i: int) -> str:
    return f"Post {i}: " + " ".join(random.sample(WORDS, k=3)).title()


def make_body() -> str:
    parts = [
        "This is a sample item used for developing the recommender system.",
        "It includes tags, author, and timestamps to simulate real content.",
        "Later, we will use this data to generate embeddings and train ranking models.",
    ]
    random.shuffle(parts)
    return " ".join(parts)


class Command(BaseCommand):
    help = "Seed the database with demo Items."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=200)
        parser.add_argument("--published", action="store_true", help="Create as published items")

    def handle(self, *args, **options):
        count = options["count"]
        published = options["published"]

        now = timezone.now()
        items = []
        for i in range(1, count + 1):
            status = Item.Status.PUBLISHED if published else Item.Status.DRAFT
            created_at = now - timedelta(minutes=i)
            published_at = created_at if status == Item.Status.PUBLISHED else None

            items.append(
                Item(
                    title=make_title(i),
                    body=make_body(),
                    author=random.choice(AUTHORS),
                    tags=random.sample(WORDS, k=random.randint(1, 5)),
                    status=status,
                    published_at=published_at,
                )
            )

        Item.objects.bulk_create(items)
        self.stdout.write(self.style.SUCCESS(f"Seeded {count} items (published={published})."))
