from rest_framework import serializers
from apps.electron.models import Electron
from apps.electron.serializers import ElectronDetailSerializer
from .models import *


class FreightSerializer(serializers.ModelSerializer):


    class Meta:
        model = FreightCarrier
        fields = '__all__'


class WebSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebSite
        fields = '__all__'


class SEOSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEO
        fields = '__all__'


class ProtocolSerializer(serializers.ModelSerializer):

    class Meta:
        model = Protocol
        fields = '__all__'


class HotModelSerialier(serializers.ModelSerializer):
    class Meta:
        model = Electron
        fields = ['id', 'model_name']


# 分类

class ContentCategorySerializer3(serializers.ModelSerializer):

    class Meta:
        model = MagicContentCategory
        fields = '__all__'


class ContentCategorySerializer2(serializers.ModelSerializer):
    children = ContentCategorySerializer3(many=True,read_only=True)

    class Meta:
        model = MagicContentCategory
        fields = '__all__'


class ContentCategorySerializer(serializers.ModelSerializer):
    children = ContentCategorySerializer2(many=True,read_only=True)

    class Meta:
        model = MagicContentCategory
        fields = '__all__'


#内容列表
class MagicContentListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(read_only=True, slug_field='level')
    class Meta:
        model = MagicContent
        fields = ['title', 'category', 'enable']

        # fields = ['title','category']

# 内容详情
class MagicContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MagicContent
        fields = '__all__'
        depth = 3


class ImageSerializer(serializers.ModelSerializer):
        class Meta:
            model = Image
            fields = '__all__'
