from django import template
from django.utils.safestring import mark_safe
from django.db.models import F
from news.models import AdSpace
from django.utils import timezone

register = template.Library()


def render_single_ad(ad):
    """Render one ad as HTML"""
    # Track impression
    AdSpace.objects.filter(pk=ad.pk).update(impressions=F('impressions') + 1)

    # If custom HTML/AdSense code — use it directly
    if ad.html_code.strip():
        return f'''
        <div class="ad-unit ad-{ad.position}" style="text-align:center;margin:12px 0">
            <div style="font-size:9px;color:#aaa;text-align:center;letter-spacing:.1em;text-transform:uppercase;margin-bottom:3px">Advertisement</div>
            {ad.html_code}
        </div>'''

    # Image ad
    img_src = ad.image.url if ad.image else ad.image_url
    if img_src:
        click_url = f'/api/ad-click/{ad.pk}/' if ad.link_url else '#'
        return f'''
        <div class="ad-unit ad-{ad.position}" style="text-align:center;margin:12px 0">
            <div style="font-size:9px;color:#aaa;text-align:center;letter-spacing:.1em;text-transform:uppercase;margin-bottom:3px">Advertisement</div>
            <a href="{click_url}" target="_blank" rel="noopener nofollow">
                <img src="{img_src}" alt="Advertisement"
                     style="max-width:100%;border-radius:4px;display:inline-block">
            </a>
        </div>'''

    return ''


@register.simple_tag(takes_context=True)
def show_ad(context, position):
    """
    Usage in template: {% show_ad 'header' %}
    Shows first active ad for given position.
    """
    ads = context.get('ads', {})
    ad_list = ads.get(position, [])
    if not ad_list:
        return mark_safe('')
    html = render_single_ad(ad_list[0])
    return mark_safe(html)


@register.simple_tag(takes_context=True)
def show_all_ads(context, position):
    """
    Usage: {% show_all_ads 'sidebar_top' %}
    Shows ALL active ads for a position (useful for sidebar).
    """
    ads = context.get('ads', {})
    ad_list = ads.get(position, [])
    if not ad_list:
        return mark_safe('')
    html = ''.join(render_single_ad(ad) for ad in ad_list)
    return mark_safe(html)


@register.inclusion_tag('news/_ad_placeholder.html', takes_context=True)
def ad_slot(context, position, label=None):
    """
    Shows ad if exists, otherwise shows placeholder in DEBUG mode.
    Usage: {% ad_slot 'sidebar_top' %}
    """
    from django.conf import settings
    ads = context.get('ads', {})
    ad_list = ads.get(position, [])
    return {
        'ad_list': ad_list,
        'position': position,
        'label': label or position.replace('_', ' ').title(),
        'debug': settings.DEBUG,
    }
