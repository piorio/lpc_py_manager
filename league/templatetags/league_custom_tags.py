from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from league.league_utils import user_manage_at_least_a_league

register = template.Library()


@register.filter()
def enable_league_admin(user):
    flag = user_manage_at_least_a_league(user)
    if flag:
        return mark_safe('<a class="collapse-item" href="' + reverse('league:league_i_manage')
                         + '">Leagues I manage</a>')
    else:
        return ''
