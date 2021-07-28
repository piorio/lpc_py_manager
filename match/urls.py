from django.urls import path
from .views import (
    AllMatchesListView,
    MyMatchesListView,
    close_match,
)


app_name = 'match'

urlpatterns = [
    path('', AllMatchesListView.as_view(), name='all_matches'),
    path('my_matches/', MyMatchesListView.as_view(), name='my_matches'),
    path('close/<int:match_id>/', close_match, name='close_match'),
]
