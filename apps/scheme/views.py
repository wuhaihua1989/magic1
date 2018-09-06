from rest_framework import (viewsets, status, generics, filters, mixins)
from rest_framework.response import Response
from .pagination import *
# from .serializers import ElectronCategorySerializer, ElectronSerializer
from .serializers import *
from django.db import transaction
from rest_framework.decorators import action

from rest_framework.views import APIView
# ---------用户界面逻辑-------------
class SchemedetailViewSet(viewsets.GenericViewSet):
    """

    slist:相似方案列表
    diagram’：系统框图

    """
    queryset = Scheme.objects.all()
    serializer_class = SchemeSerializer

    def get_serializer_class(self):
        if self.action == 'diagram':
            return FrontSchemeDesignSerializer
        elif self.action == 'slist':
            return SimilarSchemeSerializer
        else:
            return SchemeDetailPageSerializer

    @action(['get'], detail=True)
    def slist(self, request, *args, **kwargs):
        """相似方案列表"""
        try:
            scheme = request.query_params['title']
            queryset = SimilarScheme.objects.filter(scheme=scheme)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def diagram(self, request, *args, **kwargs):
        """系统框图"""
        try:
            scheme = request.query_params['title']
            queryset = SchemeSystemDesign.objects.filter(scheme=scheme)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)



# ---------管理后台界面逻辑------------
# 方案类型
class SchemeCategoryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        retrieve:
           方案分类详情
        list:
           方案分类列表 (无子分类)
        categories_list:
           方案分类列表（有子分类）
        create:
           方案分类新增
        delete:
           方案分类删除
        update:
           方案分类更新
    """
    queryset = SchemeCategory.objects.all()
    serializer_class = SchemeCategorySerializer3

    @action(['get'], detail=False)
    def categories_list(self, request):
        scheme_categories = SchemeCategory.objects.filter(parent=None)
        serializer = SchemeCategoryListSerializer(scheme_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 方案
class SchemeViewSet(mixins.CreateModelMixin,viewsets.GenericViewSet, generics.DestroyAPIView, generics.RetrieveUpdateAPIView, generics.ListAPIView):
    """
        delete:
            方案删除
        update:
            方案更新
        retrieve:
            方案详情
        list:
            方案列表
        selectron:
            详情元器件搜索
        slist:
            可替代方案列表
        similars:
            可替换方案的添加列表： title：标题参数， source_web: 网站来源参数
    """
    queryset = Scheme.objects.all()
    serializer_class = SchemeDetailSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'source_web']
    pagination_class = SchemePagination

    def get_serializer_class(self):
        if self.action == 'list':
            return SchemeListSerializer
        elif self.action in ['retrieve', 'update']:
            return SchemeDetailSerializer
        elif self.action == 'create':
            return SchemeUpdateSerializer
        elif self.action == 'slist':
            return SimilarSchemeSerializer
        elif self.action == 'similars':
            return SimilarSchemeListSerializer
        else:
            return SchemeDetailSerializer

    @action(['get'], detail=True)
    def selectron(self, request, *args, **kwargs):
        try:
            scheme = self.get_object()
            model_name = request.query_params['model_name']
            m_models = [e.model_name for e in SchemeElectron.objects.filter(scheme=scheme, model_name__istartswith=model_name)]
            models = [e.model_name for e in Electron.objects.filter(model_name__istartswith=model_name)]
            models_result = list(set(models).difference(set(m_models)))[:10]
            return Response({'models': models_result}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'models': '未匹配到模型数据'}, status=status.HTTP_400_BAD_REQUEST)

    @action(['get'], detail=True)
    def slist(self, request, *args, **kwargs):
        """相似方案列表"""
        try:
            scheme = self.get_object()
            queryset = SimilarScheme.objects.filter(scheme=scheme)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def similars(self, request, *args, **kwargs):
        """可替换方案的添加列表"""
        scheme = self.get_object()
        similars = [s.similar for s in SimilarScheme.objects.filter(scheme=scheme)]
        schemes = Scheme.objects.all()
        title = request.query_params.get('title', None)
        source_web = request.query_params.get('source_web', None)
        if title:
            schemes = schemes.filter(title=title)
        if source_web:
            schemes = schemes.filter(source_web=source_web)
        queryset = list(set(schemes).difference(set(similars)))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def all_search(self, request, *args, **kwargs):
        try:
            model_name = request.query_params['model_name']
            electrons = list(Electron.objects.filter(model_name__istartswith=model_name))
            serializer = self.get_serializer(electrons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({}, status=status.HTTP_200_OK)



# # 方案DataSheet文件上传
# class ElectronDataSheetViewSet(generics.UpdateAPIView, generics.DestroyAPIView, viewsets.GenericViewSet):
#     """
#         delete:
#            元器件DataSheet文件删除
#         update:
#            元器件DataSheet文件更新
#     """
#     queryset = Scheme.objects.all()
#     serializer_class = SchemeDataSheetSerializer
#
#     def perform_destroy(self, instance):
#         instance.source_code = ""
#         instance.save()
#
#
# # 方案图片
# class SchemeImageViewSet(generics.UpdateAPIView, generics.DestroyAPIView, viewsets.GenericViewSet):
#     """
#         delete:
#            方案Image文件删除
#         update:
#            方案Image文件更新
#     """
#     queryset = Scheme.objects.all()
#     serializer_class = SchemeUploadImageSerializer
#
#     def perform_destroy(self, instance):
#         instance.images = ""
#         instance.save()


# # 方案系统图
# class SchemeSystemDesignViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
#     """
#         create:
#             方案系统图新增
#         update:
#             方案系统图修改
#         destroy:
#             方案系统图删除
#     """
#     queryset = SchemeSystemDesign.objects.all()
#     serializer_class = SchemeSystemDesignSerializer


# 方案视频
# class SchemeVideoViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
#     """
#             create:
#                 方案视频新增
#             update:
#                 方案视频修改
#             destroy:
#                 方案视频删除
#     """
#
#     queryset = SchemeVideo.objects.all()
#     serializer_class = SchemeVideoSerializer


# 方案Bom清单
class SchemeElectronViewSet(viewsets.ModelViewSet):
    """方案Bom清单"""
    queryset = SchemeElectron.objects.all()
    serializer_class = SchemeElectronSerializer
    pagination_class = SchemeElectronPagination

    @action(['get'], detail=False)
    def scheme_list(self, request, *args, **kwargs):
        """元器件方案列表（参考设计）"""
        try:
            model_name = request.query_params['model_name']
            scheme_electrons = SchemeElectron.objects.filter(model_name=model_name)
            schemes = [scheme_electron.scheme for scheme_electron in scheme_electrons]
            reference_schemes = []
            for scheme in schemes:
                if scheme.is_reference:
                    reference_schemes.append(scheme)
            serializer = SchemeSerializer(reference_schemes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SchemeElectron.DoesNotExist:
            return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)

    @action(['get'], detail=False)
    def electron_list(self, request, *args, **kwargs):
        """方案元器件列表"""
        try:
            scheme_id = request.query_params['scheme_id']
            scheme = Scheme.objects.get(id=scheme_id)
            scheme_electrons = SchemeElectron.objects.filter(scheme=scheme)
            schemes = [scheme_electron.scheme for scheme_electron in scheme_electrons]
            serializer = SchemeSerializer(schemes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SchemeElectron.DoesNotExist:
            return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)


# 可替代方案(数据库中已经关联匹配方案)
class SimilarSchemeViewSet(generics.DestroyAPIView, generics.CreateAPIView, viewsets.GenericViewSet):
    queryset = SimilarScheme.objects.all()
    serializer_class = SimilarSchemeSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return SimilarSchemeSerializer
        else:
            return SimilarSchemeCreateSerializer


# 方案消费者
class SchemeConsumerViewSet(viewsets.ModelViewSet):
    queryset = SchemeConsumer.objects.all()
    serializer_class = SchemeConsumerSerializer

    def list(self, request, *args, **kwargs):
        """元器件方案列表"""
        try:
            electron_id = request.query_params['electron_id']
            electron = Electron.objects.get(id=electron_id)
            scheme_electrons = SchemeElectron.objects.filter(electron=electron)
            schemes = [scheme_electron.scheme for scheme_electron in scheme_electrons]
            serializer = SchemeSerializer(schemes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SchemeElectron.DoesNotExist:
            return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)

