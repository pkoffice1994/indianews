from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import News, Category, Tag, Page, EPaper, ShortNews, SystemSetting, Comment


def home(request):
    s = SystemSetting.get_settings()
    cats = Category.objects.filter(is_active=True, show_in_nav=True).order_by('order')
    pub  = News.objects.filter(status='published').select_related('category', 'author')

    breaking  = pub.filter(is_breaking=True).order_by('-published_at')[:8]
    top_story = pub.filter(is_top_story=True).order_by('-published_at').first() or pub.order_by('-published_at').first()
    featured  = pub.filter(is_featured=True).order_by('-published_at')[:4]
    latest    = pub.order_by('-published_at')[:15]
    videos    = pub.filter(is_video_news=True).order_by('-published_at')[:4]

    cat_sections = []
    for cat in cats[:7]:
        cn = pub.filter(category=cat).order_by('-published_at')[:6]
        if cn.exists():
            cat_sections.append({'category': cat, 'news': cn})

    epaper  = EPaper.objects.filter(is_active=True).order_by('-publish_date').first()
    shorts  = ShortNews.objects.filter(is_active=True).order_by('-created_at')[:6]
    popular = pub.order_by('-views')[:6]

    return render(request, 'news/home.html', {
        'site': s, 'categories': cats,
        'breaking': breaking, 'top_story': top_story,
        'featured': featured, 'latest': latest,
        'videos': videos, 'cat_sections': cat_sections,
        'epaper_latest': epaper, 'shorts': shorts, 'popular': popular,
    })


def news_detail(request, slug):
    article = get_object_or_404(News, slug=slug, status='published')
    News.objects.filter(pk=article.pk).update(views=F('views') + 1)
    related    = News.objects.filter(category=article.category, status='published').exclude(pk=article.pk).order_by('-published_at')[:4]
    comments   = article.comments.filter(is_approved=True, parent=None)
    s          = SystemSetting.get_settings()

    if request.method == 'POST' and s.enable_comments:
        name    = request.POST.get('name', '').strip()
        content = request.POST.get('content', '').strip()
        email   = request.POST.get('email', '').strip()
        if name and content:
            Comment.objects.create(
                news=article, name=name, email=email, content=content,
                user=request.user if request.user.is_authenticated else None,
            )
            return redirect(request.path + '#comments')

    return render(request, 'news/detail.html', {
        'article': article, 'related': related,
        'comments': comments, 'site': s,
    })


def category_view(request, slug):
    cat     = get_object_or_404(Category, slug=slug, is_active=True)
    sub_slug = request.GET.get('sub')
    qs      = News.objects.filter(category=cat, status='published').order_by('-published_at')
    subcategory = None
    if sub_slug:
        from .models import SubCategory
        subcategory = get_object_or_404(SubCategory, slug=sub_slug, category=cat)
        qs = qs.filter(subcategory=subcategory)
    paged = Paginator(qs, SystemSetting.get_settings().items_per_page).get_page(request.GET.get('page'))
    return render(request, 'news/category.html', {
        'category': cat, 'subcategory': subcategory,
        'page_obj': paged, 'site': SystemSetting.get_settings(),
    })


def tag_view(request, slug):
    tag  = get_object_or_404(Tag, slug=slug)
    qs   = News.objects.filter(tags=tag, status='published').order_by('-published_at')
    paged = Paginator(qs, 12).get_page(request.GET.get('page'))
    return render(request, 'news/tag.html', {'tag': tag, 'page_obj': paged, 'site': SystemSetting.get_settings()})


def search_view(request):
    q = request.GET.get('q', '').strip()
    qs = News.objects.none()
    if q:
        qs = News.objects.filter(
            Q(title_hi__icontains=q)|Q(title_en__icontains=q)|
            Q(content_hi__icontains=q)|Q(tags__name__icontains=q),
            status='published'
        ).distinct().order_by('-published_at')
    paged = Paginator(qs, 12).get_page(request.GET.get('page'))
    return render(request, 'news/search.html', {'query': q, 'page_obj': paged, 'site': SystemSetting.get_settings()})


def epaper_view(request):
    epapers = EPaper.objects.filter(is_active=True).order_by('-publish_date')
    return render(request, 'news/epaper.html', {'epapers': epapers, 'site': SystemSetting.get_settings()})


def videos_view(request):
    qs = News.objects.filter(status='published', is_video_news=True).order_by('-published_at')
    paged = Paginator(qs, 12).get_page(request.GET.get('page'))
    return render(request, 'news/videos.html', {
        'page_obj': paged,
        'site': SystemSetting.get_settings(),
    })


def page_view(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    return render(request, 'pages/page.html', {'page': page, 'site': SystemSetting.get_settings()})


@require_GET
def ad_click(request, ad_id):
    """Track ad click and redirect"""
    from .models import AdSpace
    try:
        ad = AdSpace.objects.get(pk=ad_id, is_active=True)
        AdSpace.objects.filter(pk=ad_id).update(clicks=F('clicks') + 1)
        if ad.link_url:
            return redirect(ad.link_url)
    except AdSpace.DoesNotExist:
        pass
    return redirect('/')


@require_GET
def weather_api(request):
    import requests as req
    s = SystemSetting.get_settings()
    if not s.openweather_key:
        return JsonResponse({'city': 'New Delhi', 'temp': '—', 'desc': 'Add API key in settings', 'icon': '☀'})
    try:
        r = req.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={s.weather_city}&appid={s.openweather_key}&units=metric',
            timeout=5
        )
        d = r.json()
        return JsonResponse({
            'city': d['name'], 'temp': round(d['main']['temp']),
            'temp_max': round(d['main']['temp_max']), 'temp_min': round(d['main']['temp_min']),
            'desc': d['weather'][0]['description'], 'humidity': d['main']['humidity'],
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
