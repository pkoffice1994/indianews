from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import News, Category, Tag, Page, EPaper, ShortNews, SystemSetting, Comment


def get_ads_context():
    """Get all active ads grouped by position for template context."""
    from .models import AdSpace
    from django.utils import timezone
    now = timezone.now()
    active_ads = AdSpace.objects.filter(
        is_active=True
    ).filter(
        models.Q(starts_at__isnull=True) | models.Q(starts_at__lte=now)
    ).filter(
        models.Q(ends_at__isnull=True) | models.Q(ends_at__gte=now)
    )
    ads = {}
    for ad in active_ads:
        ads.setdefault(ad.position, []).append(ad)
    return ads


def home(request):
    # Language from URL param or session
    lang = request.GET.get('lang', request.session.get('lang', 'hi'))
    if lang not in ('hi', 'en'):
        lang = 'hi'
    request.session['lang'] = lang

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
        'ads': get_ads_context(),
        'lang': lang,
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
        'comments': comments, 'site': s, 'ads': get_ads_context(),
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
        'page_obj': paged, 'site': SystemSetting.get_settings(), 'ads': get_ads_context(),
    })


def tag_view(request, slug):
    tag  = get_object_or_404(Tag, slug=slug)
    qs   = News.objects.filter(tags=tag, status='published').order_by('-published_at')
    paged = Paginator(qs, 12).get_page(request.GET.get('page'))
    return render(request, 'news/tag.html', {'tag': tag, 'page_obj': paged, 'site': SystemSetting.get_settings(), 'ads': get_ads_context()})


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
    return render(request, 'news/search.html', {'query': q, 'page_obj': paged, 'site': SystemSetting.get_settings(), 'ads': get_ads_context()})


def epaper_view(request):
    epapers = EPaper.objects.filter(is_active=True).order_by('-publish_date')
    return render(request, 'news/epaper.html', {'epapers': epapers, 'site': SystemSetting.get_settings(), 'ads': get_ads_context()})


def videos_view(request):
    from .models import ShortNews
    shorts = ShortNews.objects.filter(is_active=True, news_type='video').order_by('-created_at')
    videos = News.objects.filter(status='published', is_video_news=True).order_by('-published_at')[:12]
    return render(request, 'news/videos.html', {
        'shorts': shorts,
        'videos': videos,
        'site': SystemSetting.get_settings(),
        'ads': get_ads_context(),
    })


def page_view(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    return render(request, 'pages/page.html', {'page': page, 'site': SystemSetting.get_settings(), 'ads': get_ads_context()})


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


def dashboard_view(request):
    from django.contrib.admin.views.decorators import staff_member_required
    if not request.user.is_staff:
        from django.shortcuts import redirect
        return redirect('/admin/login/?next=/dashboard/')
    
    from django.db.models import Count, Sum
    from django.utils import timezone
    import datetime

    total_news = News.objects.count()
    published = News.objects.filter(status='published').count()
    draft = News.objects.filter(status='draft').count()
    pending = News.objects.filter(status='pending').count()
    breaking = News.objects.filter(is_breaking=True).count()
    featured = News.objects.filter(is_featured=True).count()
    total_views = News.objects.aggregate(t=Sum('views'))['t'] or 0
    total_comments = Comment.objects.count()
    
    categories = Category.objects.filter(is_active=True).annotate(
        article_count=Count('news', filter=models.Q(news__status='published'))
    ).order_by('-article_count')
    
    recent_news = News.objects.select_related('category', 'author').order_by('-created_at')[:10]
    
    # Last 7 days daily count
    today = timezone.now().date()
    daily_data = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        count = News.objects.filter(
            created_at__date=day, status='published'
        ).count()
        daily_data.append({'day': day.strftime('%b %d'), 'count': count})

    return render(request, 'news/dashboard.html', {
        'total_news': total_news,
        'published': published,
        'draft': draft,
        'pending': pending,
        'breaking': breaking,
        'featured': featured,
        'total_views': total_views,
        'total_comments': total_comments,
        'categories': categories,
        'recent_news': recent_news,
        'daily_data': daily_data,
        'ads': get_ads_context(),
    })


def advertise_view(request):
    from .models import AdBooking
    success = False
    if request.method == 'POST':
        AdBooking.objects.create(
            client_name=request.POST.get('client_name',''),
            client_email=request.POST.get('client_email',''),
            client_phone=request.POST.get('client_phone',''),
            company_name=request.POST.get('company_name',''),
            position=request.POST.get('position','header'),
            duration_days=int(request.POST.get('duration_days',30)),
            banner_image=request.FILES.get('banner_image'),
            banner_url=request.POST.get('banner_url',''),
            website_url=request.POST.get('website_url',''),
            ad_title=request.POST.get('ad_title',''),
            message=request.POST.get('message',''),
            total_price=int(request.POST.get('total_price',0) or 0),
        )
        success = True

    packages = [
        {'position':'header',        'name':'Header Banner',    'size':'728×90',  'price_30':15000,'preview_h':40, 'impressions':'5,000+'},
        {'position':'home_top',      'name':'Home Top Banner',  'size':'970×90',  'price_30':12000,'preview_h':40, 'impressions':'4,000+'},
        {'position':'sidebar_top',   'name':'Sidebar Box',      'size':'300×250', 'price_30':8000, 'preview_h':60, 'impressions':'3,000+'},
        {'position':'sidebar_bottom','name':'Sidebar Tall',     'size':'300×600', 'price_30':10000,'preview_h':80, 'impressions':'3,500+'},
        {'position':'in_content',    'name':'Article Mid',      'size':'336×280', 'price_30':6000, 'preview_h':60, 'impressions':'2,500+'},
        {'position':'footer',        'name':'Footer Banner',    'size':'728×90',  'price_30':5000, 'preview_h':40, 'impressions':'2,000+'},
    ]

    return render(request, 'news/advertise.html', {
        'packages': packages,
        'success': success,
        'site': SystemSetting.get_settings(),
        'ads': get_ads_context(),
    })


def chatbot_api(request):
    """Simple chatbot that answers news-related questions"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    import json
    data = json.loads(request.body)
    question = data.get('message', '').strip()
    
    if not question:
        return JsonResponse({'reply': 'Please ask a question!'})
    
    q_lower = question.lower()
    
    # Search news matching the question
    from .models import News
    news_qs = News.objects.filter(status='published')
    
    # Try to find relevant news
    words = [w for w in q_lower.split() if len(w) > 3]
    matched = None
    for word in words:
        results = news_qs.filter(
            Q(title_hi__icontains=word) |
            Q(title_en__icontains=word) |
            Q(content_hi__icontains=word)
        ).first()
        if results:
            matched = results
            break
    
    if matched:
        reply = f"📰 **{matched.title_hi}**\n\n{matched.summary_hi or matched.content_hi[:200]}...\n\n[Read more](/{matched.slug}/)"
    else:
        # General responses
        if any(w in q_lower for w in ['hello', 'hi', 'hey', 'namaste', 'नमस्ते']):
            reply = "नमस्ते! 🙏 मैं India News का AI Assistant हूं। आप मुझसे कोई भी खबर के बारे में पूछ सकते हैं!"
        elif any(w in q_lower for w in ['latest', 'new', 'today', 'aaj', 'आज']):
            latest = news_qs.order_by('-published_at').first()
            if latest:
                reply = f"📰 आज की ताज़ा खबर:\n\n**{latest.title_hi}**\n\n[पढ़ें](/{latest.slug}/)"
            else:
                reply = "अभी कोई खबर उपलब्ध नहीं है।"
        elif any(w in q_lower for w in ['breaking', 'ब्रेकिंग']):
            brk = news_qs.filter(is_breaking=True).first()
            if brk:
                reply = f"🔴 Breaking News:\n\n**{brk.title_hi}**\n\n[पढ़ें](/{brk.slug}/)"
            else:
                reply = "अभी कोई Breaking News नहीं है।"
        elif any(w in q_lower for w in ['sport', 'cricket', 'ipl', 'खेल']):
            sp = news_qs.filter(category__slug='khel').first()
            reply = f"⚽ खेल खबर: **{sp.title_hi}**" if sp else "खेल की कोई खबर नहीं मिली।"
        elif any(w in q_lower for w in ['weather', 'mausam', 'मौसम']):
            reply = "🌤️ मौसम की जानकारी के लिए हमारा वेबसाइट देखें। ताज़ा मौसम अपडेट टॉपबार में दिखता है!"
        else:
            total = news_qs.count()
            reply = f"मुझे '{question}' के बारे में कोई खबर नहीं मिली। आप और specific keyword try करें!\n\nहमारे पास अभी **{total}** खबरें हैं। 📰"
    
    return JsonResponse({'reply': reply})
