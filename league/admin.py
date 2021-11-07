from django.contrib import admin
from .models import League, Season, Tournament, TournamentTeamResult


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


@admin.register(TournamentTeamResult)
class TournamentTeamResult(admin.ModelAdmin):
    list_display = ('team', 'tournament')
    list_filter = ('team', 'tournament')
    search_fields = ('team', ' tournament')
    raw_id_fields = ('tournament',)
    ordering = ('team',)
    autocomplete_fields = ('tournament',)
