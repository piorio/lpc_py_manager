from django.contrib import admin
from .models import League, Season, Tournament


# Register your models here.
@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    list_filter = ('name', 'status')
    search_fields = ('name',)
    raw_id_fields = ('managers',)
    ordering = ('name',)
    autocomplete_fields = ('managers',)


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    list_filter = ('name', 'status', 'league__name')
    search_fields = ('name',)
    raw_id_fields = ('league',)
    ordering = ('name',)
    autocomplete_fields = ('league',)


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    list_filter = ('name', 'status', 'season__name')
    search_fields = ('name',)
    raw_id_fields = ('season',)
    ordering = ('name',)
    autocomplete_fields = ('season',)
