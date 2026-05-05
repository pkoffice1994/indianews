from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'india-news-secret-key-2024-change-in-prod')
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('1', 'true', 'yes', 'on')
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

LANGUAGE_CODE = 'hi'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
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
    "site_title": "India News Admin",
    "site_header": "इंडिया न्यूज़",
    "site_brand": "India News",
    "welcome_sign": "इंडिया न्यूज़ — Admin Panel में स्वागत है 🇮🇳",
    "copyright": "India News © 2024",
    "search_model": ["news.News", "auth.User"],
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index"},
        {"name": "🌐 Live Website", "url": "/", "new_window": True},
        {"name": "➕ Add News", "url": "admin:news_news_add"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": [
        "news", "news.Category", "news.SubCategory", "news.Tag",
        "news.News", "news.EPaper", "news.ShortNews",
        "news.FeaturedSection", "news.AdSpace", "auth",
        "news.SiteUser", "news.Comment", "news.CommentFlag",
        "news.Page", "news.Role", "news.StaffMember", "news.SystemSetting",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "news.Category": "fas fa-layer-group",
        "news.SubCategory": "fas fa-sitemap",
        "news.Tag": "fas fa-tag",
        "news.News": "fas fa-newspaper",
        "news.EPaper": "fas fa-file-pdf",
        "news.ShortNews": "fas fa-bolt",
        "news.FeaturedSection": "fas fa-star",
        "news.AdSpace": "fas fa-ad",
        "news.SiteUser": "fas fa-user-circle",
        "news.Comment": "fas fa-comment",
        "news.CommentFlag": "fas fa-flag",
        "news.Page": "fas fa-file",
        "news.Role": "fas fa-user-shield",
        "news.StaffMember": "fas fa-id-badge",
        "news.SystemSetting": "fas fa-cog",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "body_small_text": False,
    "brand_colour": "navbar-danger",
    "accent": "accent-danger",
    "navbar": "navbar-dark",
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-danger",
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "theme": "default",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
