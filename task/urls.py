from rest_framework.routers import DefaultRouter
from . import views as task_views

router = DefaultRouter(trailing_slash=False)
router.register(r'tasks', task_views.TaskViewSet, basename='tasks')

urlpatterns = router.urls
