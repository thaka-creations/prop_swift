from rest_framework.routers import DefaultRouter
from . import views, owner_views

router = DefaultRouter(trailing_slash=False)

router.register(r'auth', views.AuthenticationViewSet, basename='auth')
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'owners', owner_views.OwnerViewSet, basename='owners')

urlpatterns = router.urls
