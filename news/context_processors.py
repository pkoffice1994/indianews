from .models import Category, SystemSetting, Page, AdSpace
from django.utils import timezone

def global_context(request):
    now = timezone.now()
    # Active ads — respect start/end dates if set
    ads_qs = AdSpace.objects.filter(is_active=True)
    active_ads = [
        a for a in ads_qs
        if (a.starts_at is None or a.starts_at <= now)
        and (a.ends_at is None or a.ends_at >= now)
    ]
    # Group by position for easy template access
    ads = {}
    for ad in active_ads:
        ads.setdefault(ad.position, []).append(ad)

    return {
        'nav_categories': Category.objects.filter(is_active=True, show_in_nav=True).order_by('order'),
        'site': SystemSetting.get_settings(),
        'footer_pages': Page.objects.filter(is_active=True, show_in_footer=True),
        'ads': ads,  # dict: {'header': [...], 'sidebar_top': [...], ...}
    }
