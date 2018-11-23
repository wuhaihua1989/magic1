from rest_framework import serializers
from django.utils import timezone
from django_redis import get_redis_connection
from django.db import transaction
from apps.config.models import FreightCarrier
from apps.electron.models import Electron
from apps.users.models import User
from apps.order.models import OrderInfo,OrderElectron
from decimal import Decimal
from django_redis import get_redis_connection

class Cartserializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = Electron
        fields = ('id', 'model_name', 'platform_price', 'factory', 'count')


class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    eletrons = Cartserializer(many=True, read_only=True)


class SaveOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        # 设置order_id为只读字段
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        # 获取收货地址和支付方式
        address = validated_data['address']
        pay_method = validated_data['pay_method']
        receipt = validated_data['receipt']

        if address[0:3] =='广东省':
            freight = FreightCarrier.objects.get(id=1).another_freight
        else:
            freight = FreightCarrier.objects.get(id=1).gd_freight
        # 获取当前下单用户
        user = self.context["request"].user
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        with transaction.atomic():
            save_id = transaction.savepoint()
            # 创建订单信息
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=0,  # 订单商品总数
                total_amount=Decimal(0),  # 订单商品总金额
                freight=freight,
                pay_method=pay_method,
                status=status,
                receipt= receipt,
            )


            redis_conn = get_redis_connection("cart")
            redis_cart = redis_conn.hgetall("cart_%s" % user.id)
            redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
            # 将bytes类型转换为int类型
            cart = {}
            for ele_id in redis_cart_selected:
                cart[int(ele_id)] = int(redis_cart[ele_id])


            total_amount = Decimal("0")
            total_count = 0

            # 遍历结算商品：
            for ele_id in cart.keys():
              while True:
                  # 每次进行都要查询当前sku商品最新库存
                  sku = Electron.objects.get(id=ele_id)
                  # 保存原始库存和销量
                  origin_stock = sku.platform_stock  # 15
                  print(origin_stock)
                  # 判断商品库存是否充足
                  sku_count = cart[sku.id]  # 本次购买当前sku商品的数量
                  if sku.stock < sku_count:
                      # 事务回滚
                      transaction.savepoint_rollback(save_id)
                      raise serializers.ValidationError({"message": "商品库存不足"})


                  # 减少库存
                  new_stock = origin_stock - sku_count

                  # 使用乐观锁更新库存
                  # update 的返回值当前修改的受影响行数
                  ret = Electron.objects.filter(
                      id=sku.id,
                      stock=origin_stock  # 数据库的库存变成10, 还在认为是15
                  ).update(
                      stock=new_stock,
                  )

                  if ret == 0:  # 如果不能更新，则表示库存发生变化，让程序再次检查库存
                      continue
                  else:
                      break  # 如果能更新，则跳出循环

              # 保存订单商品
              OrderElectron.objects.create(
                  order=order,
                  sku=sku,
                  count=sku_count,
                  price=sku.platform_price,
              )

              # 增加订单总金额和订单商品数量
              sku_amount = sku.platform_price * sku_count  # 单个sku商品的金额
              total_amount += sku_amount  # 累计总金额
              total_count += sku_count  # 累计总额

            # 更新订单的金额数量信息
            if order.total_amount > FreightCarrier.objects.get(id=1).max_money:
                order.freight = Decimal(0)
            order.total_amount = total_amount
            order.total_amount += order.freight  # 加运费
            order.total_count = total_count
            order.save()

            # 提交事务
            transaction.savepoint_commit(save_id)

            # 在redis购物车中删除已计算商品数据
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, *cart.keys())
            pl.srem('cart_selected_%s' % user.id, *cart.keys())
            pl.execute()

            return order


class ElectronInfoserializer(serializers.ModelSerializer):
    class Meta:
        model = OrderElectron
        filed = '__all__'


class FrontOrderInfoSerializer(serializers.ModelSerializer):
    eles = ElectronInfoserializer(many=True,read_only=True)

    class Meta:
        model = OrderInfo
        fields = ['order_id','total_count','total_amount','freight','status','eles','create_at']


class FrontOrderDetailInfoSerializer(serializers.ModelSerializer):
    eles = ElectronInfoserializer(many=True, read_only=True)
    receipt_info = serializers.SerializerMethodField()
    class Meta:
        model = OrderInfo
        fields = '__all__'

    def get_receipt_info(self,obj):
        dict = {}
        order = OrderInfo.objects.filter(order_id=obj)
        user_info = User.objects.filter(id=order.user)
        if order.receipt == 1:
            return dict
        elif order.receipt == 2:
            dict['name'] = user_info.name
            return dict
        else:
            dict['company_name'] = user_info.company_name
            dict['company_tel_number'] = user_info.company_tel_number
            dict['company_fax_number'] = user_info.company_fax_number
            dict['company_address'] = user_info.company_address
            dict['company_tax_number'] = user_info.company_tax_number
            dict['bank_name'] = user_info.bank_name
            dict['bank_account'] = user_info.bank_account
            dict['signer_name'] = user_info.signer_name
            dict['signer_mobile'] =user_info. signer_mobile
            dict['send_address'] = user_info.send_address
            return dict
