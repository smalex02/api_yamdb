from django.core import mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail

from api_yamdb.settings import NOREPLY_YAMDB_EMAIL


def email_is_valid(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def generate_mail(to_email, code):
    subject = 'Confirmation code для YaMDB'
    to = to_email
    text_content = f'''Вы запросили confirmation code для работы с API YaMDB.\n
                        Внимание, храните его в тайне {code}'''
    mail.send_mail(
        subject, text_content,
        NOREPLY_YAMDB_EMAIL, [to],
        fail_silently=False
    )


def send_confirmation_code(email, confirmation_code):
    EMAIL_YAMDB = 'registration_YaMDb@mail.com'
    """Oтправляет на почту пользователя код подтверждения."""
    send_mail(
        subject='Код подтверждения',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=EMAIL_YAMDB,
        recipient_list=(email,),
        fail_silently=False,
    )
