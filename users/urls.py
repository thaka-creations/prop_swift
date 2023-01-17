from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter(trailing_slash=False)

router.register(r'auth', views.AuthenticationViewSet, basename='auth')

urlpatterns = router.urls
