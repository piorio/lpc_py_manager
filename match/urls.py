from django.urls import path
from . import views


app_name = 'match'

urlpatterns = [
    path('', views.AllMatchesToPlayListView.as_view(), name='all_matches'),
    path('played', views.AllMatchesPlayedListView.as_view(), name='all_matches_played'),
    path('my_matches/', views.MyMatchesToPlayListView.as_view(), name='my_matches'),
    path('my_matches/played',views. MyMatchesPlayedListView.as_view(), name='my_matches_played'),
    path('close/<int:match_id>/', views.close_match, name='close_match'),
]
