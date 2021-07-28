from django.urls import path
from .views import (
    AllMatchesListView,
    MyMatchesListView,
)


app_name = 'match'

urlpatterns = [
    path('', AllMatchesListView.as_view(), name='all_matches'),
    path('my_matches', MyMatchesListView.as_view(), name='my_matches'),
]
