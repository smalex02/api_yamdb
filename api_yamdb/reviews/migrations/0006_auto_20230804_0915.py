# Generated by Django 3.2 on 2023-08-04 06:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_auto_20230803_2136'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='user',
            name='unique_user',
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(db_index=True, max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Имя пользователя содержит недопустимый символ', regex='^[\\w.@+-]+$')], verbose_name='Имя пользователя'),
        ),
    ]
