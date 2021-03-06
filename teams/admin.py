from django.contrib import admin
from .models import Team, TeamPlayer


# Register your models here.
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'coach', 'roster_team')
    list_filter = ('coach', 'roster_team')
    search_fields = ('name',)
    raw_id_fields = ('coach', 'roster_team')
    ordering = ('name', 'coach')


@admin.register(TeamPlayer)
class TeamPlayerAdmin(admin.ModelAdmin):
    list_filter = ('team', 'team__coach')
    search_fields = ('name',)
    raw_id_fields = ('team', )
    ordering = ('team', 'name',)
