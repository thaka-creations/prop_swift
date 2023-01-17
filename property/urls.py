from rest_framework.routers import DefaultRouter
from . views import PropertyViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'property', PropertyViewSet, basename='property')

urlpatterns = router.urls

