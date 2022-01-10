from django.urls import path, include
from rest_framework import routers

from leagueApi.views import LeagueViewSet

router = routers.DefaultRouter()
router.register('leagues', LeagueViewSet)

app_name = 'apiLeague'

urlpatterns = [
    path('', include(router.urls))
]