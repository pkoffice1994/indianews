from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'india-news-secret-key-2024-change-in-prod')
DEBUG = os.environ.get("DEBUG", "False").lower() in ("1", "true", "yes", "on")
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost,.onrender.com'
).split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'news',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'indianews.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'news.context_processors.global_context',
    ]},
}]

WSGI_APPLICATION = 'indianews.wsgi.application'

database_url = os.environ.get('DATABASE_URL')
if database_url:
    DATABASES = {
        'default': dj_database_url.parse(database_url, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = False
USE_TZ = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JAZZMIN_SETTINGS = {
    "site_title": "India News",
    "site_header": "India News",
    "site_brand": "🇮🇳 India News",
    "site_logo": None,
    "site_logo_classes": "img-circle",
    "welcome_sign": "Welcome back! Publish great news today.",
    "copyright": "India News © 2026",
    "search_model": ["news.News", "auth.User"],

    "topmenu_links": [
        {"name": "📊 Dashboard",   "url": "/dashboard/"},
        {"name": "🌐 Live Site",   "url": "/", "new_window": True},
        {"name": "➕ Add News",    "url": "admin:news_news_add"},
        {"name": "⚡ Short News",  "url": "admin:news_shortnews_add"},
        {"name": "📰 E-Paper",     "url": "admin:news_epaper_add"},
    ],

    "usermenu_links": [
        {"name": "🌐 View Site", "url": "/", "new_window": True},
        {"name": "📊 Dashboard", "url": "/dashboard/"},
    ],

    "show_sidebar": True,
    "navigation_expanded": False,

    "hide_apps": [],
    "hide_models": [],

    "order_with_respect_to": [
        "news.News", "news.ShortNews", "news.Category",
        "news.Tag", "news.EPaper", "news.AdSpace",
        "news.AdBooking", "news.FeaturedSection",
        "news.SystemSetting", "news.Page",
        "news.Comment", "auth",
    ],

    "icons": {
        "auth":                 "fas fa-shield-alt",
        "auth.user":            "fas fa-user",
        "auth.group":           "fas fa-users",
        "news.News":            "fas fa-newspaper",
        "news.ShortNews":       "fas fa-bolt",
        "news.Category":        "fas fa-layer-group",
        "news.SubCategory":     "fas fa-sitemap",
        "news.Tag":             "fas fa-hashtag",
        "news.EPaper":          "fas fa-file-pdf",
        "news.FeaturedSection": "fas fa-star",
        "news.AdSpace":         "fas fa-rectangle-ad",
        "news.AdBooking":       "fas fa-handshake",
        "news.SiteUser":        "fas fa-user-circle",
        "news.Comment":         "fas fa-comments",
        "news.CommentFlag":     "fas fa-flag",
        "news.Page":            "fas fa-file-alt",
        "news.Role":            "fas fa-user-shield",
        "news.StaffMember":     "fas fa-id-badge",
        "news.SystemSetting":   "fas fa-sliders-h",
    },

    "default_icon_parents":  "fas fa-folder",
    "default_icon_children": "fas fa-circle-dot",
    "related_modal_active":  True,
    "show_ui_builder":       False,
    "changeform_format":     "horizontal_tabs",
    "language_chooser":      False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "body_small_text": False,
    "brand_colour": "navbar-danger",
    "accent": "accent-danger",
    "navbar": "navbar-white navbar-light",
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-danger",
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "theme": "flatly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
