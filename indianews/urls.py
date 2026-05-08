from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header  = "इंडिया न्यूज़ — Admin"
admin.site.site_title   = "India News"
admin.site.index_title  = "Admin Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('news.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
