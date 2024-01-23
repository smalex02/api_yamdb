from datetime import datetime

from django.forms import ValidationError


def validate_year_release(value):
    """Год выпуска не может быть больше текущего."""
    if value > datetime.now().year:
        raise ValidationError(
            ('Год выпуска не может быть больше текущего'),
            params={'value': value},
        )
    if value < 0:
        raise ValidationError(
            ('Год выпуска не может быть отрицательным'),
            params={'value': value},
        )
