from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('',                          views.home,              name='home'),
    path('dashboard/',                login_required(views.dashboard_view), name='dashboard'),
    path('search/',                   views.search_view,       name='search'),
    path('epaper/',                   views.epaper_view,       name='epaper'),
    path('videos/',                   views.videos_view,       name='videos'),
    path('category/<slug:slug>/',     views.category_view,     name='category'),
    path('tag/<slug:slug>/',          views.tag_view,          name='tag'),
    path('page/<slug:slug>/',         views.page_view,         name='page'),
    path('api/weather/',              views.weather_api,       name='weather_api'),
    path('api/ad-click/<int:ad_id>/', views.ad_click,          name='ad_click'),
    path('advertise/',                views.advertise_view,    name='advertise'),
    path('publish-epaper/',           views.epaper_publish_view, name='epaper_publish'),
    path('<slug:slug>/',              views.news_detail,       name='news_detail'),
]
