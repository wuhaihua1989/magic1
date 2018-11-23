import django_filters
from apps.order.models import OrderInfo



# 自定义过滤类
class OrderFilter(django_filters.rest_framework.FilterSet):
    status = django_filters.ChoiceFilter(choices=OrderInfo.ORDER_STATUS_CHOICES)

    class Meta:
        model = OrderInfo
        fields = ['status']
