from rest_framework import serializers
from apps.electron.models import *
from rest_framework.validators import UniqueValidator
from apps.scheme.models import SchemeElectron, Scheme

# ---------客户端界面------------
class FelectronSupplierSerializer(serializers.ModelSerializer):

    class Meta:
            model = Supplier
            fields = '__all__'


class SupplierDetailSerializer(serializers.ModelSerializer):
    mes =  FelectronSupplierSerializer(many=True,read_only=True)
    class Meta:
            model = Supplier
            fields = ['mes']

class FrontElectronSerializer(serializers.ModelSerializer):
    supplier = SupplierDetailSerializer(many=True)

    class Meta:
        model = Electron
        fields = ['supplier']


#-----------
# from rest_framework.validators import UniqueValidator
# 元器件序列化
class ElectronSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electron
        fields = '__all__'


# 元器件列表
class ElectronBackListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Electron
        fields = ['id', 'model_name', 'factory', 'category', 'source_web', 'is_supply']


# 元器件详情
class ElectronDetailSerializer(serializers.ModelSerializer):
    kwargs_value = serializers.SerializerMethodField(label='参数列表')

    class Meta:
        model = Electron
        fields = ['id', 'category', 'model_name', 'images',
                  'is_supply', 'data_sheet', 'desc_specific', 'kwargs_value', 'origin', 'market_date_at', 'supplier']
        # exclude = ['is_hot', 'views', 'kwargs', 'kwargs_values', ]

    def get_kwargs_value(self, obj):
        # 获得参数ID
        try:
            kwargs_ids = obj.kwargs.split(',')
            print(kwargs_ids)
            if len(kwargs_ids) == 0 or len(kwargs_ids) == 1:
                return []

            if len(kwargs_ids) == 1:
                if kwargs_ids[0] == "":
                    return []

            kwargs = []
            for k_id in kwargs_ids:
                kwargs.append(ElectronKwargs.objects.get(id=k_id))

            # 获得参数值ID
            kwargs_values = obj.kwargs_values.split(',')
            data = []
            for i in range(len(kwargs)):
                data.append({'id': kwargs[i].id, 'cname': kwargs[i].cname, 'kwarg_value': kwargs_values[i]})
            return data
        except Exception as e:
            print(e)
            return []


# 元器件修改
class ElectronUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electron
        fields = ['id', 'category', 'model_name',
                  'is_supply', 'desc_specific', 'kwargs_values', 'origin', 'market_date_at']




# 元器件应用支持
class ElectronApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Electron
        fields = ['id', 'factory_link']


# 元器件分类（三级目录）
class ElectronCategorySerializer3(serializers.ModelSerializer):
    """三级分类"""
    class Meta:
        model = ElectronCategory
        fields = '__all__'


# 元器件分类（二级目录）
class ElectronCategorySerializer2(serializers.ModelSerializer):
    """二级分类"""
    children = ElectronCategorySerializer3(many=True)

    class Meta:
        model = ElectronCategory
        fields = '__all__'


# 元器件分类（一级目录）
class ElectronCategoryListSerializer(serializers.ModelSerializer):
    """一级分类"""
    children = ElectronCategorySerializer2(many=True)

    class Meta:
        model = ElectronCategory
        fields = '__all__'


# 元器件分类
class ElectronCategorySerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(label='ID', read_only=True)
    # level = serializers.ChoiceField(choices=((0, '一级类目'), (1, '二级类目'), (2, '三级类目')), label='类型级别', required=False)
    # name = serializers.CharField(label='类目描述', max_length=188)
    # image = serializers.ImageField(allow_null=True, label='类型图片', max_length=100, required=False)
    # parent = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=ElectronCategory.objects.all(), required=False)

    class Meta:
        model = ElectronCategory
        fields = '__all__'


# 元器件参考设计
class ElectronSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = ['id', 'title', 'desc_specific']


# 可替代元器件
class SimilarElectronSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimilarElectron
        fields = '__all__'


# 供应商
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


# 元器件供应商
class ElectronSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectronSupplier
        fields ='__all__'


# 元器件供应商列表
class ElectronSupplierListSerializer(serializers.ModelSerializer):
    supplier = serializers.SlugRelatedField(read_only=True, slug_field='name')
    phone = serializers.SerializerMethodField()

    class Meta:
        model = ElectronSupplier
        fields = ['supplier', 'inventory', 'price', 'batch_no', 'phone',]

    # def get_supplier_name(self, obj):
    #     return obj.supplier.name

    def get_phone(self, obj):
        return obj.supplier.phone_number


# 元器件原理图
class ElectronCircuitDiagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectronCircuitDiagram
        fields = '__all__'


# 元器件参数
class ElectronKwargsSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField(label='参数值', help_text='参数值')

    def get_values(self, obj):
        kwargs_value = ElectronKwargsValue.objects.filter(kwargs=obj)
        values = [kwarg.value for kwarg in kwargs_value]
        return ",".join(values)
    #
    # def validate(self, attrs):
    #     del attrs['values']
    #     return attrs

    class Meta:
        model = ElectronKwargs
        fields = '__all__'


# 元器件参数值详情
class ElectronKVDetailSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField(label='参数值', help_text='参数值')

    def get_values(self, obj):
        kwargs_value = ElectronKwargsValue.objects.filter(kwargs=obj)
        values = [kwarg.value for kwarg in kwargs_value]
        return values

    class Meta:
        model = ElectronKwargs
        fields = '__all__'


# 元器件参数值
class ElectronKwargsValueSerializer(serializers.ModelSerializer):
    values = serializers.CharField(max_length=188, label='参数值', help_text='参数值')

    def validate(self, attrs):
        del attrs['values']
        return attrs

    def create(self, validated_data):
        print(validated_data)
        user = super(ElectronKwargsValueSerializer, self).create(validated_data=validated_data)
        return user

    class Meta:
        model = ElectronKwargs
        fields = '__all__'


# 元器件视频
class ElectronVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ElectronVideo
        fields = '__all__'


# 元器件消费者
class ElectronConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectronConsumer
        fields = '__all__'


# 元器件模型
class ElectronModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electron
        fields = ['id', 'model_name']


# PintoPin元器件列表
class ElectronPlistSerializer(serializers.ModelSerializer):
    pin_to_pin = serializers.SlugRelatedField(read_only=True, slug_field='model_name')

    class Meta:
        model = PinToPin
        exclude = ['electron', 'create_at']


# 可替换元器件列表
class ElectronSlistSerializer(serializers.ModelSerializer):
    similar = serializers.SlugRelatedField(read_only=True, slug_field='model_name')

    class Meta:
        model = SimilarElectron
        exclude = ['electron', 'create_at']


# PinToPin 器件新增
class PinToPinCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PinToPin
        fields = '__all__'


# # 通用视频
# class UniversalVideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UniversalVideo
#         fields = '__all__'


# 评论用户
class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'icon', 'rel_name']





