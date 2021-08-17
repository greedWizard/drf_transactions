from rest_framework import urlpatterns
from rest_framework.routers import SimpleRouter
from .views import OperationView


router = SimpleRouter()

router.register('operations', OperationView, basename='operations')

urlpatterns = router.urls