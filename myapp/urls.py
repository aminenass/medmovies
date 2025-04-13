from django.urls import path,re_path
from . import views

urlpatterns = [
    path('', views.hello, name='home'),
    path('movies/', views.movie ,name='movies'),
    path('tvshows/', views.tvshows,name='tvshows'),
    re_path(r'^tvshows/(?P<category>anime|korean|turkish|french)/$',views.tvshows,name='tvshows-category'),    
    path('search/', views.search_results, name='search_results'),
    path('media/<str:types>/<int:item_id>', views.media_detail_view, name='media_detail'),

]  