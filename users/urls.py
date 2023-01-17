from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter(trailing_slash=False)

router.register(r'auth', views.AuthenticationViewSet, basename='auth')
router.register(r'users', views.UserViewSet, basename='users')

urlpatterns = router.urls
