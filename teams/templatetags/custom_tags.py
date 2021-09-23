from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def add_level_up_action(player):
    if (player.level == 'NONE' and player.spp >= 3) \
            or (player.level == 'EXPERIENCED' and player.spp >= 4)\
            or (player.level == 'VETERAN' and player.spp >= 6)\
            or (player.level == 'EMERGING STAR' and player.spp >= 8)\
            or (player.level == 'STAR' and player.spp >= 10)\
            or (player.level == 'SUPER STAR' and player.spp >= 15):
        return mark_safe('<a href="'
                         + reverse('teams:player_level_up', args=[str(player.id)]) +
                         '" class="btn btn-primary">LEVELUP</a>')
    return ''
