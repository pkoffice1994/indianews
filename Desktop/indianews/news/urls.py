from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.home,          name='home'),
    path('search/',               views.search_view,   name='search'),
    path('epaper/',               views.epaper_view,   name='epaper'),
    path('videos/',               views.videos_view,   name='videos'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('tag/<slug:slug>/',      views.tag_view,      name='tag'),
    path('page/<slug:slug>/',     views.page_view,     name='page'),
    path('api/weather/',          views.weather_api,   name='weather_api'),
    path('api/ad-click/<int:ad_id>/', views.ad_click,  name='ad_click'),
    path('<slug:slug>/',           views.news_detail,   name='news_detail'),
]
