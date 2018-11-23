from django.conf.urls import (include, url)
from apps.order.views import views_front,views_back
from rest_framework import routers
from magic.settings import PREFIX, PREFIX_BACK


router = routers.DefaultRouter()
router.register(r'ic/backend/order', views_back.AllOrderInfoViewset)
router.register(r'ic/orders/info', views_front.OrderInfoViewset)


urlpatterns = [
    url('', include(router.urls)),
    url(r"ic/orders/settlement/$", views_front.OrderSettlementView.as_view()),
    url(r"ic/orders/save$", views_front.SaveOrderView.as_view()),
    url('ic/order/(?P<order_id>)/payment/', views_front.PaymentViewset.as_view()),

]




