from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)


def send_league_creation_request(request_user, league_name, source_mail):
    user = get_user_model()
    all_admin_users = user.objects.filter(is_superuser=True).all()
    all_admin_users_mail = [u.email for u in all_admin_users]

    logger.debug('Send email creation league request to ' + str(all_admin_users_mail))

    message = 'The user ' + str(request_user.username) + ' ask to create a league with the name "' + league_name + '".'
    mail_message = ' Please respond to email ' + source_mail

    send_mail(
        'Request league creation',
        message + mail_message,
        source_mail,
        all_admin_users_mail,
        fail_silently=False,
    )
    print('HELLO')
