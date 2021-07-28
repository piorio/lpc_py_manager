from django.contrib import admin

# Register your models here.
from match.models import Match


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('first_team', 'second_team', 'match_date', 'first_team_td', 'second_team_td')
    ordering = ('first_team', 'second_team', )
    search_fields = ('first_team', 'second_team', )
