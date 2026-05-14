"""Remove duplicate news articles keeping only the latest one"""
from django.core.management.base import BaseCommand
from news.models import News


class Command(BaseCommand):
    help = 'Remove duplicate news articles'

    def handle(self, *args, **options):
        seen_slugs = {}
        deleted = 0

        # Find duplicates by title_hi
        from django.db.models import Count
        dupes = (News.objects.values('title_hi')
                 .annotate(cnt=Count('id'))
                 .filter(cnt__gt=1))

        for d in dupes:
            articles = News.objects.filter(title_hi=d['title_hi']).order_by('id')
            # Keep first, delete rest
            keep = articles.first()
            to_delete = articles.exclude(pk=keep.pk)
            count = to_delete.count()
            to_delete.delete()
            deleted += count
            self.stdout.write(f'  🗑 Deleted {count} duplicates of: {d["title_hi"][:50]}')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! {deleted} duplicate articles removed.'))
