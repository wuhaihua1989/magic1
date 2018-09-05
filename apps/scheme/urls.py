from django.conf.urls import (include, url)
from . import views
from rest_framework import routers
from magic.settings import PREFIX, PREFIX_BACK

router = routers.DefaultRouter()
router.register(r'^' + PREFIX_BACK + 'schemes/categories', views.SchemeCategoryViewSet)
router.register(r'^' + PREFIX_BACK + 'schemes/scheme', views.SchemeViewSet)
# router.register(r'^' + PREFIX_BACK + 'schemes/designs', views.SchemeSystemDesignViewSet)
router.register(r'^' + PREFIX_BACK + 'schemes/electrons', views.SchemeElectronViewSet)
# router.register(r'^' + PREFIX_BACK + 'schemes/videos', views.SchemeVideoViewSet)
# router.register(r'^' + PREFIX_BACK + 'schemes/designs', views.SchemeSystemDesignViewSet)
# router.register(r'^' + PREFIX_BACK + 'schemes/images', views.SchemeImageViewSet)
# router.register(r'^' + PREFIX_BACK + 'schemes/code', views.ElectronDataSheetViewSet)
router.register(r'^' + PREFIX_BACK + 'schemes/similar', views.SimilarSchemeViewSet)

# router.register(r'scheme_consumers', views.SchemeConsumerViewSet)
# router.register(r'^' + PREFIX_BACK + 'users/members', UserMemberView)

urlpatterns = [
    url('', include(router.urls)),
]
