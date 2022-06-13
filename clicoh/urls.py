from rest_framework import routers
from .api import OrderViewSet, ProductViewSet

router = routers.SimpleRouter()
router.register("api/product", ProductViewSet)
router.register("api/order", OrderViewSet)

urlpatterns = router.urls
