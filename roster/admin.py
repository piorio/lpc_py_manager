from django.contrib import admin
from .models import Race, Skill, Trait, RosterPlayer, RosterTeam


# Register your models here.
@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    ordering = ('name', 'category')
    search_fields = ('name', 'category')


@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(RosterTeam)
class RosterTeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'race', 'tier')
    list_filter = ('tier', 'race')
    raw_id_fields = ('race',)
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(RosterPlayer)
class RosterPlayerAdmin(admin.ModelAdmin):
    list_display = ('position', 'roster_team', 'movement_allowance', 'agility', 'strength', 'armor_value', 'cost')
    list_filter = ('roster_team', 'cost')
    ordering = ('roster_team', 'position')
    raw_id_fields = ('roster_team', 'skills', 'traits', 'primary_skills', 'secondary_skills')
    search_fields = ('position',)
