from rest_framework import serializers

from apps.product.serializer.serializers_back import ProductListSerializers
from apps.scheme.models import *



# 方案类型序列化（三级目录）
class SchemeCategorySerializer3(serializers.ModelSerializer):
    """三级分类"""
    class Meta:
        model = SchemeCategory
        fields = '__all__'


# 方案类型序列化（二级目录）
class SchemeCategorySerializer2(serializers.ModelSerializer):
    """二级分类"""
    children = SchemeCategorySerializer3(many=True)

    class Meta:
        model = SchemeCategory
        fields = '__all__'


# 方案类型序列化（一级目录）
class SchemeCategoryListSerializer(serializers.ModelSerializer):
    """一级分类"""
    children = SchemeCategorySerializer2(many=True)

    class Meta:
        model = SchemeCategory
        fields = '__all__'


# 方案序列化
class SchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = '__all__'


class SchemeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        exclude = ['views', 'download_count', 'source_web']


# 方案列表
class SchemeListSerializer(serializers.ModelSerializer):
    similarschemes = serializers.SerializerMethodField()

    def get_similarschemes(self, obj):  # 自定义的字段实现
        schemes_repl = [similars.scheme for similars in SimilarScheme.objects.filter(scheme=obj)]
        schemes = Scheme.objects.filter(category=obj.category)
        # for scheme in schemes:
        #     # tags = scheme.tags.split(';')
        #     if len(set(tags) & set(obj.tags)) > 0:
        #         schemes_repl.append(scheme)
        return len(schemes_repl)

    class Meta:
        model = Scheme
        fields = ['id', 'title', 'similarschemes', 'source_web', 'create_at']


# 方案视频
class SchemeVideoListSerializer(serializers.ModelSerializer):

    class Meta:
        model = SchemeVideo
        exclude = ['scheme', 'create_at']


# 方案Bom清单
class SchemeBomListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemeElectron
        fields = ['id', 'model_name', 'model_des', 'is_key']


# 方案系统设计图序列化
class SchemeDesignListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemeSystemDesign
        exclude = ['download_count', 'scheme']


# 方案详情    改
class SchemeDetailSerializer(serializers.ModelSerializer):
    videos = SchemeVideoListSerializer(many=True, read_only=True)
    designs = SchemeDesignListSerializer(many=True, read_only=True)
    electrons = serializers.SerializerMethodField()

    class Meta:
        model = Scheme
        exclude = ['views', 'download_count', 'consumer','contact_email','scheme_user']
        depth = 1

    def get_electrons(self, obj):
        electrons = SchemeElectron.objects.filter(scheme=obj).order_by('-is_key')
        serializer = SchemeBomListSerializer(electrons, many=True)
        return serializer.data

    def update(self, instance, validated_data):
        electrons = validated_data.pop['electrons']
        scheme = Scheme.objects.update(**validated_data)
        for electron in electrons:
            SchemeElectron.objects.update_or_create(scheme=scheme, **electron)
        return scheme


# 元器件DataSheet文件
class SchemeDataSheetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Scheme
        fields = ['id', 'source_code']



# # 元器件Image文件
# class SchemeUploadImageSerializer(serializers.ModelSerializer):
#     # image_file = serializers.FileField(allow_null=True, label='图片', max_length=388, required=False)
#
#     class Meta:
#         model = Scheme
#         fields = ['id', 'images']
#
#     def validate_images(self, images):
#         images.name = get_prefix_filename() + images.name
#         return images
#
#
# # 方案系统设计图序列化
# class SchemeSystemDesignSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SchemeSystemDesign
#         exclude = ['download_count', ]


# 方案消费者序列化
class SchemeConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemeConsumer
        fields = '__all__'


# 方案元器件序列化
class SchemeElectronSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemeElectron
        fields = '__all__'


# 方案视频序列化
class SchemeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemeVideo
        exclude = ['create_at', ]


# 可替换方案列表
class SimilarSchemeListSerializer(serializers.ModelSerializer):
    # scheme = SchemeListSerializer(many=True, read_only=True)

    class Meta:
        model = Scheme
        fields = ['id', 'title', 'source_web', 'create_at']
        # fields = ['id', 'scheme']


# 可替代方案
class SimilarSchemeSerializer(serializers.ModelSerializer):
    similar = SimilarSchemeListSerializer()

    class Meta:
        model = SimilarScheme
        fields = '__all__'


# 可替代方案新增
class SimilarSchemeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimilarScheme
        fields = '__all__'









