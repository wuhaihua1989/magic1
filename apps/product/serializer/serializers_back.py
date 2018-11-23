from rest_framework import serializers

from apps.product.models import ProductCategory, Product, ProductVideo, ProductElectron
from apps.product.models import CustomProduct, CustomProductElectron, CustomProductScheme
from apps.electron.models import Electron
from apps.scheme.models import Scheme
from apps.users.models import User
from ..validationerror import ValidationError


class ProductCategorySerializers(serializers.ModelSerializer):
    """三级分类"""
    class Meta:
        model = ProductCategory
        fields = "__all__"


class ProductCategorySerializer2(serializers.ModelSerializer):
    """二级分类"""
    children = ProductCategorySerializers(many=True)

    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductCategorySerializers1(serializers.ModelSerializer):
    """一级分类"""
    children = ProductCategorySerializer2(many=True)

    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductListSerializers(serializers.ModelSerializer):
    """后台成品列表序列化"""
    class Meta:
        model = Product
        fields = ['id', 'name', 'source_web', 'create_at']


class ProductVideoListSerializers(serializers.ModelSerializer):
    """成品详情-（视频列表序列化）"""
    class Meta:
        model = ProductVideo
        exclude = ['product', 'name', 'create_at', 'update_at']


class ProductElectronDetailSerializers(serializers.ModelSerializer):
    """成品详情-（元器件详情序列化）"""
    category = serializers.CharField(source='category.name', read_only=True)
    model_name = serializers.CharField(read_only=True)

    class Meta:
        model = Electron
        fields = ['id', 'model_name', 'category']
        # error_messages = {"model_name": {"required": "元器件型号不能为空!"}}


class ProductElectronListSerializers(serializers.ModelSerializer):
    """成品详情-（BOM清单序列化）"""
    model_name = ProductElectronDetailSerializers()

    class Meta:
        model = ProductElectron
        exclude = ['product', 'create_at', 'update_at']


class ProductSchemeListSerializers(serializers.ModelSerializer):
    """成品详情- (方案列表序列化)"""
    class Meta:
        model = Scheme
        fields = ['id', 'title']


class ProductDetailSerializers(serializers.ModelSerializer):
    """后台成品详情/修改序列化"""
    electrons = ProductElectronListSerializers(many=True)
    videos = ProductVideoListSerializers(many=True)
    scheme = ProductSchemeListSerializers(many=True)

    class Meta:
        model = Product
        fields = ['name', 'price', 'images', 'videos', 'electrons', 'scheme', 'desc']

    def validate_electrons(self, electrons):
        post_electrons = self.context['request'].data['electrons']
        if post_electrons:
            for electron in post_electrons:
                if electron['model_name']['id'] == '':
                    raise ValidationError({"fail": "数据库未收录该元器件,无法完成提交"})

    def validate_scheme(self, scheme):
        post_schemes = self.context['request'].data['scheme']
        if post_schemes:
            for single_scheme in post_schemes:
                if single_scheme['id'] == '':
                    raise ValidationError({"fail": "数据库未收录该方案,无法完成提交"})

    def update(self, instance, validated_data):

        electrons = self.context['request'].data['electrons']
        videos = self.context['request'].data['videos']
        schemes = self.context['request'].data['scheme']

        instance.name = validated_data['name']
        instance.price = validated_data['price']
        instance.images = validated_data['images']
        instance.desc = validated_data['desc']

        if schemes:
            old_product_schemes = instance.scheme.all()
            if old_product_schemes:
                old_product_scheme_id = []
                for old_single_scheme in old_product_schemes:
                    old_product_scheme_id.append(old_single_scheme.id)
                new_product_scheme_id = []
                for new_single_scheme in schemes:
                    new_product_scheme_id.append(new_single_scheme['id'])
                remove_scheme = list(set(old_product_scheme_id).difference(set(new_product_scheme_id)))
                for remove_scheme_id in remove_scheme:
                    delete_scheme = Scheme.objects.get(id=remove_scheme_id)
                    instance.scheme.remove(delete_scheme)
                    instance.save()
                add_scheme = list(set(new_product_scheme_id).difference(set(old_product_scheme_id)))
                for add_scheme_id in add_scheme:
                    scheme = Scheme.objects.get(id=add_scheme_id)
                    instance.scheme.add(scheme)
                    instance.save()
            else:
                for scheme in schemes:
                    scheme = Scheme.objects.get(id=scheme['id'])
                    instance.scheme.add(scheme)
                    instance.save()
        else:
            old_product_schemes = instance.scheme.all()
            if old_product_schemes:
                for old_single_scheme in old_product_schemes:
                    delete_scheme = Scheme.objects.get(id=old_single_scheme.id)
                    instance.scheme.remove(delete_scheme)
                    instance.save()
        instance.save()

        if electrons:
            old_product_electrons = instance.electrons.all()
            if old_product_electrons:
                old_product_electrons_id = []
                for old_product_electron in old_product_electrons:
                    old_product_electrons_id.append(old_product_electron.id)
                new_product_electrons_id = []
                for new_product_electron in electrons:
                    if new_product_electron['id'] != '':
                        new_product_electrons_id.append(new_product_electron['id'])
                remove_product_electron = list(set(old_product_electrons_id).difference(set(new_product_electrons_id)))
                if remove_product_electron:
                    ProductElectron.objects.filter(id__in=remove_product_electron).delete()
                for electron in electrons:
                    if electron['id'] == '':
                        product_electron = ProductElectron()
                        product_electron.product = instance
                        product_electron.model_name_id = electron['model_name']['id']
                        product_electron.model_desc = electron['model_desc']
                        product_electron.is_key = electron['is_key']
                        product_electron.save()
                    else:
                        product_electron = ProductElectron.objects.get(id=electron['id'])
                        product_electron.product = instance
                        product_electron.model_name_id = electron['model_name']['id']
                        product_electron.model_desc = electron['model_desc']
                        product_electron.is_key = electron['is_key']
                        product_electron.save()
            else:
                for electron in electrons:
                    product_electron = ProductElectron()
                    product_electron.product = instance
                    product_electron.model_name_id = electron['model_name']['id']
                    product_electron.model_desc = electron['model_desc']
                    product_electron.is_key = electron['is_key']
                    product_electron.save()
        else:
            old_product_electrons = instance.electrons.all()
            if old_product_electrons:
                for old_product_electron in old_product_electrons:
                    ProductElectron.objects.filter(id=old_product_electron.id).delete()
        if videos:
            old_videos = instance.videos.all()
            if old_videos:
                old_videos_id = []
                for old_video in old_videos:
                    old_videos_id.append(old_video.id)
                new_videos_id = []
                for new_video in videos:
                    if new_video['id'] != '':
                        new_videos_id.append(new_video['id'])
                remove_video_id = list(set(old_videos_id).difference(set(new_videos_id)))
                if remove_video_id:
                    ProductVideo.objects.filter(id__in=remove_video_id).delete()
                for video in videos:
                    if new_video['id'] == '':
                        product_video = ProductVideo()
                        product_video.product = instance
                        product_video.url = video['url']
                        product_video.is_key = video['is_key']
                        product_video.save()
                    else:
                        product_video = ProductVideo.objects.get(id=video['id'])
                        product_video.product = instance
                        product_video.url = video['url']
                        product_video.is_key = video['is_key']
                        product_video.save()
            else:
                for video in videos:
                    product_video = ProductVideo()
                    product_video.product = instance
                    product_video.url = video['url']
                    product_video.is_key = video['is_key']
                    product_video.save()
        else:
            old_videos = instance.videos.all()
            if old_videos:
                for old_video in old_videos:
                    ProductVideo.objects.filter(id=old_video.id).delete()
        return instance


class CustomProductListUserSerializer(serializers.ModelSerializer):
    """成品定制列表-用户信息-序列化"""
    class Meta:
        model = User
        fields = ['id', 'username']


class CustomProductListSerializers(serializers.ModelSerializer):
    """成品定制列表-序列化"""
    consumer = CustomProductListUserSerializer()
    product = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = CustomProduct
        fields = ['id', 'product', 'consumer', 'create_at']


class CustomProductDetailUserSerializer(serializers.ModelSerializer):
    """成品定制详情-用户信息-序列化"""
    class Meta:
        model = User
        fields = ['rel_name', 'mobile']


class CustomProductSchemeDetailSerializers(serializers.ModelSerializer):
    """成品定制详情-方案定制-方案详情-序列化"""
    class Meta:
        model = Scheme
        fields = ['id', 'title']


class CustomProductElectronDetailSerializers(serializers.ModelSerializer):
    """成品定制详情-元器件定制-元器件详情-序列化"""
    class Meta:
        model = Electron
        fields = ['id', 'model_name']


class CustomProductSchemeSerializers(serializers.ModelSerializer):
    """成品定制详情-方案定制-序列化"""
    scheme = CustomProductSchemeDetailSerializers()

    class Meta:
        model = CustomProductScheme
        fields = ['scheme']


class CustomProductElectronSerializers(serializers.ModelSerializer):
    """成品定制详情-元器件定制-序列化"""
    electron = CustomProductElectronDetailSerializers()

    class Meta:
        model = CustomProductElectron
        fields = ['electron']


class CustomProductDetailSerializer(serializers.ModelSerializer):
    """成品定制详情-序列化"""
    product = serializers.SlugRelatedField(read_only=True, slug_field='name')
    consumer = CustomProductDetailUserSerializer()
    schemes_custom = CustomProductSchemeSerializers(many=True, read_only=True)
    electrons_custom = CustomProductElectronSerializers(many=True, read_only=True)

    class Meta:
        model = CustomProduct
        fields = ['id', 'product', 'consumer', 'electrons_custom', 'schemes_custom', 'appearance', 'factory']
