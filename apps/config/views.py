from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import (generics, status, authentication, permissions, filters, viewsets, routers, mixins)

from rest_framework.viewsets import GenericViewSet
import json
from apps.electron.models import Electron
from apps.electron.serializer.serializers_back import ElectronSerializer
from .serializers import *
from apps.config.models import FreightCarrier, MagicContent, MagicContentCategory


# 运费配置
class FreightViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,GenericViewSet):
    serializer_class = FreightSerializer
    queryset = FreightCarrier.objects.all()

    def list (self, request, *args, **kwargs):
        queryset = self.queryset.order_by('-update_at')
        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            return Response({"message": "无数据"})
        return Response(serializer.data[0])


# 管理添加内容分类
class ContentCategoryViewSet(viewsets.ModelViewSet):
    """
    内容分类
    list ：内容分类列表

    """
    serializer_class = ContentCategorySerializer3
    queryset = MagicContentCategory.objects.all()

    @action(['get'], detail=False)
    def categories_list(self, request):
        scheme_categories = MagicContentCategory.objects.filter(parent=None)
        serializer = ContentCategorySerializer(scheme_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['get'], detail=False)
    def categories_level(self, request):
        electron_categories = MagicContentCategory.objects.filter(parent=None)
        serializer = ContentCategorySerializer2(electron_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 网站基本信息
class WebSetViewSet(viewsets.ModelViewSet):
    queryset = WebSite.objects.all()
    serializer_class = WebSiteSerializer
    permission_classes = [IsAuthenticated]
    #    # def create(self, request, *args, **kwargs):
    #     try:
    #         data = request.data
    #         json.dumps(data['source'])
    #         serializer = self.get_serializer(data= data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #     except Exception as e:
    #         raise e
    #
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('-update_at')
        serializer = self.get_serializer(queryset, many=True)
        print(serializer.data)
        if not serializer.data:
            return Response({"message": "无数据"})
        return Response(serializer.data[0])

    def update(self, request, *args, **kwargs):

        instance = self.get_object()

        data = request.data
        print(data['source'])

        data['source'] = json.dumps(data['source'])
        print(instance.source)
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        redict = serializer.data
        redict['source'] = json.loads(serializer.data['source'])

        print(redict)
        return Response(redict)


# seo
class SEOViewSet(viewsets.ModelViewSet):
    queryset = SEO.objects.all()
    serializer_class = SEOSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('-update_at')
        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            return Response({"message":"无数据"})
        return Response(serializer.data[0])


# 网站协议
class ProtocolViewSet(viewsets.ModelViewSet):
    """网站协议"""
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer


    def list(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('create_at')
        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            return Response({"message":"无数据"})
        return Response(serializer.data[0])



# 热搜型号
class HotModelViewSet(mixins.CreateModelMixin,mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.ListModelMixin,GenericViewSet):
    """热搜"""
    queryset = Electron.objects.all()
    serializer_class = HotModelSerialier

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ElectronSerializer
        # elif self.action == 'list':
        #     return
        return HotModelSerialier

    @action(['get'], detail=False)
    def hsearch(self, request, *args, **kwargs):
        try:
            model_name = request.query_params['model_name']
            electrons = Electron.objects.filter(model_name__istartswith=model_name)
            if electrons is None:
                return Response({'message':'未找到'},status=status.HTTP_200_OK)
            serializer = self.get_serializer(electrons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:

            return Response({'message': '查询失败'}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        # hot_name = HotModel.objects.filter(is_delete=False)


        hot_name = Electron.objects.filter(is_hot=True)
        serializer = HotModelSerialier(hot_name, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_hot= False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 内容列表
class MagicContentViewSet(viewsets.ModelViewSet):
    queryset = MagicContent.objects.all()
    serializer_class = MagicContentListSerializer
    def get_serializer_class(self):
        if self.action in ['list','retrieve','update']:
            return MagicContentSerializer
        # elif self.action == 'retrieve' or self.action == 'update':
        return MagicContentListSerializer





class ImageStorageViewSet(mixins.CreateModelMixin,viewsets.GenericViewSet):
    """图片上传接口"""
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]


class VideoStorageViewSet(mixins.CreateModelMixin,viewsets.GenericViewSet):

    queryset = Video.objects.all()
    serializer_class = VedioSerializer


class FileStorageViewSet(mixins.CreateModelMixin,viewsets.GenericViewSet):

    queryset = Files.objects.all()
    serializer_class = FilesSerializer






