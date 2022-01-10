from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser

# Create your views here.
from league.models import League
from leagueApi.serializers import LeagueSerializer


class LeagueViewSet(viewsets.ModelViewSet):
    serializer_class = LeagueSerializer
    queryset = League.objects.all()
    authentication_classes = (TokenAuthentication, )
    # We can use IsAuthenticated
    permission_classes = (IsAdminUser, )
