from rest_framework import serializers
from apps.order.models import *

class ElectronInfoserializer(serializers.ModelSerializer):
    class Meta:
        model = OrderElectron
        filed = '__all__'


class OrderInfoSerializer(serializers.ModelSerializer):
    eles = ElectronInfoserializer(many=True,read_only=True)

    class Meta:
        model = OrderInfo
        fields = ['order_id','total_count','total_amount','freight','status','eles','create_at']
        # fields = ('id', 'model_name', 'platform_price', 'factory', 'count')
# class ElectronInfoserializer(serializers.ModelSerializer):
#     eles = serializers.SlugRelatedField(read_only=True, slug_field='model_name')
#order_id = m

#     class Meta:
#         model = OrderElectron
#         # fields = '__all__'
#         exclude = ['order']

# 快递信息序列
class CourierInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ['order_id','Courier_company','Courier_no']




class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model =User
        fields = ['usename','mobile','default_address','name','company_name','company_tel_number','company_fax_number',
                  'company_address ','company_tax_number','bank_name','bank_account ','signer_name','signer_mobile','send_address']

class OrderDetailInfoSerializer(serializers.ModelSerializer):
    eles = ElectronInfoserializer(many=True, read_only=True)
    class Meta:
        model = OrderInfo
        fields = '__all__'

