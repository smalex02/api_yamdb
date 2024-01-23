from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import filters, viewsets, status
from rest_framework.permissions import (
    AllowAny, IsAuthenticated)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (
    IsAdminOrReadOnly, ReviewCommentPermissions,
    IsSuperUserOrIsAdminOnly
)
from api.serializers import (
    CategorieSerializer, GenreSerializer,
    TitleGetSerializer, TitleSerializer,
    ReviewSerializer, RegistrationSerializer,
    GetTokenSerializer
)
from .serializers import CommentSerializer, UserSerializer
from api.mixins import GetListCreateDeleteMixin
from reviews.models import Categorie, Genre, Title, Review, User


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет модели User"""
    queryset = User.objects.all()
    permission_classes = (IsSuperUserOrIsAdminOnly,)
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['GET', 'PATCH', 'DELETE'],
        url_path=r'(?P<username>[\w.@+-]+)',
        url_name='get_user'
    )
    def username(self, request, username):
        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(role=request.user.role)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(viewsets.ModelViewSet):
    """Регистрация нового пользователя"""
    permission_classes = (AllowAny,)

    def send_reg_mail(self, user):
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject="Conformation code",
            message=confirmation_code,
            from_email=settings.NOREPLY_YAMDB_EMAIL,
            recipient_list=(user.email,),
        )

    def create(self, request):
        serializer = RegistrationSerializer(data=request.data)
        user = User.objects.filter(
            username=request.data.get("username"),
            email=request.data.get("email")
        )
        if user.exists():
            self.send_reg_mail(user.first())
            return Response(serializer.initial_data, status=status.HTTP_200_OK)
        if serializer.is_valid():
            user = User.objects.create(
                username=serializer.validated_data.get("username"),
                email=serializer.validated_data.get("email"),
            )
            self.send_reg_mail(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTokenView(viewsets.ModelViewSet):
    """Получение пользователем JWT токена."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = GetTokenSerializer

    def create(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            message = {'confirmation_code': 'Код подтверждения не верен'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """Получение/создание/удаление/редактирование отзыва."""
    serializer_class = ReviewSerializer
    permission_classes = (ReviewCommentPermissions,)

    @action(
        methods=['GET', 'PATCH', 'POST', 'DELETE'],
        detail=False,
    )
    def get_queryset(self):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CategorieViewSet(GetListCreateDeleteMixin):
    """Получение/создание/удаление категории."""
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'slug')
    lookup_field = 'slug'

    def method_not_allowed(self, request):
        if request.method == 'PUT':
            serializer = UserSerializer(request.user)
            return Response(
                serializer.data,
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )


class GenreViewset(GetListCreateDeleteMixin):
    """Получение/создание/удаление жанра."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'slug')
    lookup_field = 'slug'

    def method_not_allowed(self, request):
        if request.method == 'PUT':
            serializer = UserSerializer(request.user)
            return Response(
                serializer.data,
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )


class TitleViewSet(viewsets.ModelViewSet):
    """Получение/создание/удаление/редактирование произведения."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    @action(
        methods=['GET', 'PATCH', 'POST', 'DELETE'],
        detail=False,
    )
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleGetSerializer
        return TitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Получение/создание/удаление/редактирование комментария."""
    serializer_class = CommentSerializer
    permission_classes = (ReviewCommentPermissions,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
