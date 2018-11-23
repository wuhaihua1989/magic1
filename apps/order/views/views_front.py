import os
from rest_framework.views import APIView
from rest_framework import viewsets,mixins
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView,ListAPIView,UpdateAPIView,RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_redis import get_redis_connection
from rest_framework.decorators import action
from django.conf import settings
from apps.electron.models import Electron
from apps.order.serializer.serializers_front import *
from apps.order.serializer.serializers_back import *
from rest_framework import status
from rest_framework import viewsets, mixins, generics
from wechatpy.pay import WeChatPay
from django_filters.rest_framework import DjangoFilterBackend
from apps.order.pagination import OrderPagination
from apps.order.filters import OrderFilter
from rest_framework import filters

class OrderSettlementView(APIView):
    """
    订单商品
    """
    permission_classes = [IsAuthenticated]

    def get(self,request):
        # 获取当前登陆用户
        user = request.user
        # 从redis中提取购物车数据
        redis_conn = get_redis_connection('cart')
        # hgetall　获取redis中指定hash数据的所有键和值
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        # smembers 获取redis中指定集合的所有成员
        redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
        cart = {}
        for ele_id in redis_cart_selected:
            cart[int(ele_id)] = int( redis_cart[ele_id] )
        electrons = Electron.objects.filter(id__in=cart.keys())

        for electron in electrons:
            electron.count = cart[electron.id]
        address = user.default_address
        if address[0:3] == '广东省':
            freight = FreightCarrier.objects.get(id=1).another_freight
        else:
            freight = FreightCarrier.objects.get(id=1).gd_freight
        serializer = OrderSettlementSerializer({'freight':freight,'electrons': electrons})
        print(serializer.data)
        return Response(serializer.data)

class SaveOrderView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer


class OrderInfoViewset(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):

    queryset = OrderInfo.objects.all()
    serializer_class = OrderInfoSerializer
    pagination_class = OrderPagination
    filter_backends = (DjangoFilterBackend,filters.SearchFilter)
    filter_class = OrderFilter

    def get_serializer_class(self):
        if action=='list':
            return FrontOrderInfoSerializer
        else:
            return FrontOrderDetailInfoSerializer

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = OrderInfo.objects.filter(user=user)
        serializers = FrontOrderInfoSerializer(queryset)
        return Response(serializers.data,status= status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.receive_goods = True
        instance.save()
        OrderInfo.objects.filter(order_id=instance).update(status=OrderInfo.ORDER_STATUS_ENUM['FINISHED'])
        return Response({},status=status.HTTP_200_OK)


class PaymentViewset(APIView):
    """微信支付"""
    permission_classes = [IsAuthenticated]

    def get(self,request,order_id):
        user = request.user
        try:
            order = OrderInfo.objects.filter(order_id=order_id,
                                             user=user,
                                             pay_method=OrderInfo.PAY_METHODS_ENUM['WEIXIN'],
                                             status= OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response({'message':'订单信息有误'},status=status.HTTP_400_BAD_REQUEST)
        wechatpay = WeChatPay(
            appid=settings.APPID,
            sub_appid = settings.sub_appid,
            api_key = settings.api_key,
            mch_id = settings.mch_id,
            mch_cert = os.path.join(os.path.dirname(os.path.abspath()),"keys/"),
            mch_key = os.path.join(os.path.dirname(os.path.abspath()),"keys/"),
            timeout = 300,
            sandbox = True)

        data = wechatpay.order.create(
                trade_type= "NATIVE",
                body= '魔方智能%s'% order_id,
                total_fee = order.total_amount,
                notify_url =None,
                out_trade_no=order_id,)

        return Response(data.url)































