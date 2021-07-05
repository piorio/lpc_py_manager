from django.contrib import admin
from .models import Race, Skill, Trait, RosterPlayer, RosterTeam


# Register your models here.
admin.site.register(Race)
admin.site.register(Skill)
admin.site.register(Trait)
admin.site.register(RosterPlayer)
admin.site.register(RosterTeam)
