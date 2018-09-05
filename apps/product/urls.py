from rest_framework import routers
from django.conf.urls import (url, include)
from .views import *
from magic.settings import PREFIX, PREFIX_BACK

router = routers.DefaultRouter()
router.register(PREFIX_BACK + 'products/categories', ProductCategoryViewSet)
router.register(PREFIX_BACK + 'products/product', ProductViewSet)
router.register(PREFIX_BACK + 'products/customs', CustomProductViewSet)
# router.register('product_videos', ProductVideoViewSet)
# router.register('product_electrons', ProductElectronViewSet)
# router.register('product_customs', CustomProductViewSet)
# router.register('product_custom_schemes', CustomProductSchemeViewSet)
# router.register('product_custom_electrons', CustomProductElectronViewSet)

urlpatterns = [
    url('', include(router.urls)),
]
