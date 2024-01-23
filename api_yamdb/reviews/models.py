from django.db import models
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .validators import validate_year_release

from .validators import validate_year_release


TITLE_DATA = '{name}, {year}, {description}, {category}, {genre}'


class User(AbstractUser):

    class Role(models.TextChoices):
        USER = 'user', _('User')
        MODERATOR = 'moderator', _('Moderator')
        ADMIN = 'admin', _('Admin')

    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )
    email = models.EmailField(
        _('email address'), blank=False, unique=True, max_length=254
    )
    bio = models.TextField(blank=True)

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.USER,
    )
    confirmation_code = models.CharField(max_length=100, blank=True, )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_moderator(self):
        return self.role == "moderator"

    @property
    def is_admin(self):
        return self.role == "admin" or self.is_superuser or self.is_staff


class Categorie(models.Model):
    """Категория произведения."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название категории',
        help_text='Введите название категории'
    )
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Метка')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Жанр произведения."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра',
        help_text='Введите название жанра'
    )
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Метка')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Название произведения."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения',
    )
    year = models.PositiveIntegerField(
        verbose_name='Год выпуска', validators=[validate_year_release]
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name='Описание произведения'
    )
    category = models.ForeignKey(
        Categorie,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        help_text='Категория, к которому относится произведение'
    )
    genre = models.ManyToManyField(
        Genre, through='GenreTitle',
        verbose_name='Жанр',
        help_text='Жанры, к которым относится произведение'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return TITLE_DATA.format(
            name=self.name,
            year=self.year,
            description=self.description,
            category=self.category,
            genre=self.genre
        )


class GenreTitle(models.Model):
    """Модель связи id произведения и id жанра."""
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    """Отзывы."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    score = models.IntegerField(
        validators=[
            MinValueValidator(1, 'Не меньше 1'),
            MaxValueValidator(10, 'Не больше 10')
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата отзыва',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            ),
        )


class Comment(models.Model):
    """Комментарии."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        verbose_name='Дата комментария',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
