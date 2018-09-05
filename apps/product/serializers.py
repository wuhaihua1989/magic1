from rest_framework import serializers
from .models import *


class ProductCategorySerializers(serializers.ModelSerializer):
    """三级分类"""
    class Meta:
        model = ProductCategory
        fields = "__all__"


# 成品分类（三级目录）
class ProductCategorySerializer2(serializers.ModelSerializer):
    """二级分类"""
    children = ProductCategorySerializers(many=True)

    class Meta:
        model = ProductCategory
        fields = '__all__'


# 成品分类（二级目录）
class ProductCategorySerializers1(serializers.ModelSerializer):
    """一级分类"""
    children = ProductCategorySerializer2(many=True)

    class Meta:
        model = ProductCategory
        fields = '__all__'


# 成品列表
class ProductListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'source_web', 'create_at']


# 成品详情-（视频列表）
class ProductVideoListSerializers(serializers.ModelSerializer):

    class Meta:
        model = ProductVideo
        exclude = ['product', 'name']


# 成品详情-（元器件列表）
class ProductElectronListSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductElectron
        exclude = ['product', 'create_at']


# 成品详情- (方案列表)
class ProductSchemeListSerializers(serializers.ModelSerializer):

    class Meta:
        model = Scheme
        fields = ['id', 'title']


# 成品详情
class ProductDetailSerializers(serializers.ModelSerializer):
    electrons = ProductElectronListSerializers(many=True, read_only=True)
    videos = ProductVideoListSerializers(many=True, read_only=True)
    scheme = ProductSchemeListSerializers(many=True, read_only=True)

    class Meta:
        model = Product
        exclude = ['update_at', 'create_at', 'factory']

    def update(self, instance, validated_data):

        electrons = validated_data.pop['electrons']
        videos = validated_data.pop['videos']
        product = Product.objects.update(**validated_data)
        for electron in electrons:
            ProductElectron.objects.update_or_create(product=product, **electron)
        for video in videos:
            ProductVideo.objects.update_or_create(product=product, **video)
        return product


# 成品图片
class ProductUploadImageSerializer(serializers.ModelSerializer):
    class Meat:
        model = Product
        fields = ['id', 'images']


# 自定义成品
class CustomProductListSerializers(serializers.ModelSerializer):
    consumer = serializers.SlugRelatedField(read_only=True, slug_field='username')
    product = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = CustomProduct
        fields = ['id', 'consumer', 'product', 'create_at']


# 自定义成品用户
class CustomProductDetailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['rel_name', 'mobile']


# 自定义成品方案
class CustomProductSchemeSerializers(serializers.ModelSerializer):
    scheme = serializers.SlugRelatedField(read_only=True, slug_field='title')

    class Meta:
        model = CustomProductScheme
        fields = '__all__'


# 自定义成品元器件
class CustomProductElectronSerializers(serializers.ModelSerializer):
    electron = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = CustomProductElectron
        fields = '__all__'


# 自定义成品
class CustomProductDetailSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(read_only=True, slug_field='name')
    consumer = CustomProductDetailUserSerializer()
    schemes = CustomProductSchemeSerializers(many=True, read_only=True)
    electrons = CustomProductElectronSerializers(many=True, read_only=True)

    class Meta:
        model = CustomProduct
        fields = '__all__'
