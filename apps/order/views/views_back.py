from django_filters.rest_framework import DjangoFilterBackend
from apps.order.pagination import OrderPagination

from apps.order.serializer.serializers_back import *
from apps.order.serializer.serializers_front import *
from rest_framework import viewsets, mixins, generics
from rest_framework.viewsets import GenericViewSet
from rest_framework import filters
from apps.order.filters import OrderFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

# class AllOrderInfoViewsets(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
#                            mixins.ListModelMixin, GenericViewSet):

class AllOrderInfoViewset(viewsets.ModelViewSet):
    queryset = OrderInfo.objects.all()
    serializer_class = OrderInfoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OrderPagination
    filter_backends = (DjangoFilterBackend,filters.SearchFilter)
    filter_class = OrderFilter


    def get_serializer_class(self):

        if action == 'update':
            return CourierInfoSerializer
        elif action == 'retrieve':
            return OrderDetailInfoSerializer
        else:
            return OrderInfoSerializer

    def update(self, request, *args, **kwargs):

        data = request.data
        order_id = self.kwargs['pk']
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['UNRECEIVED'])
        return Response(serializer.data)



