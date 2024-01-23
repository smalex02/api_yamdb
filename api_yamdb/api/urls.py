from django.urls import include, path
from rest_framework import routers
from .views import (
    CommentViewSet,
    CategorieViewSet, GenreViewset,
    TitleViewSet, ReviewViewSet, UserViewSet,
    GetTokenView, RegistrationView
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
router.register('categories', CategorieViewSet, basename='categories')
router.register('genres', GenreViewset, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('v1/', include(router.urls)),
    path(
        'v1/auth/signup/',
        RegistrationView.as_view({'post': 'create'}),
        name='signup'
    ),
    path(
        'v1/auth/token/',
        GetTokenView.as_view({'post': 'create'}),
        name='token'
    )
]
