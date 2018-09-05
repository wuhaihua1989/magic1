from django.conf.urls import (include, url)
from .views import *
from rest_framework import routers
from magic.settings import PREFIX, PREFIX_BACK

router = routers.DefaultRouter()
router.register(PREFIX_BACK + 'electrons/electron', ElectronViewSet)
router.register(PREFIX_BACK + 'electrons/categories', ElectronCategoryViewSet)
router.register(PREFIX_BACK + 'electrons/kwargs', ElectronKwargsViewSet)
# router.register(PREFIX_BACK + 'electrons/datasheet', ElectronDataSheetViewSet)
# router.register(PREFIX_BACK + 'electrons/images', ElectronImageViewSet)
# router.register(PREFIX_BACK + 'electrons/video', ElectronVideoViewSet)
# router.register(PREFIX_BACK + 'electrons/pelectron', PinToPinViewSet)
# router.register(PREFIX_BACK + 'electrons/selectron', SimilarElectronViewSet)

router.register(PREFIX_BACK + 'electrons/suppliers', SupplierListViewSet)
router.register(PREFIX_BACK + 'electrons/circuit_diagrams', ElectronCircuitDiagramViewSet)
router.register(PREFIX_BACK + 'electrons/detail', FrontElectronDetailViewSet)



urlpatterns = [
    # url(r'^' + PREFIX_BACK + 'electrons/suppliers/(?P<pk>[^/.]+)/?$', supplier_list, name='供应商列表'),
    url('', include(router.urls)),
]
