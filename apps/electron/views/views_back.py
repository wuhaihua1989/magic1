from rest_framework import (viewsets, status, generics)

from apps.electron.serializer.serializers_back import *
from apps.electron.pagination import *
from rest_framework import filters
from rest_framework.decorators import action
from django.db import transaction

# --------用户界面----------


class FrontElectronDetailViewSet(viewsets.GenericViewSet):
    queryset = Electron.objects.all()
    serializers_class = ElectronSerializer

    def get_serializer_class(self):
        if self.action == 'supplier':
            return FrontElectronSerializer
        return ElectronSerializer

    @action(['get'], detail=False)
    def supplier(self, request, *args, **kwargs):
        try:
            electron = request.query_params['model_name']
            queryset = Electron.objects.filter(model_name=electron)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)


# --------管理界面----------


# Create your views here.
# 元器件分类
class ElectronCategoryViewSet(viewsets.ModelViewSet):
    """
        retrieve:
           元器件分类详情
        list:
           元器件分类列表（无子类）
        categories_list:
           元器件分类列表（有子类）
        categories_list_level:
           元器件分类列表（最多二级子类）
        kwargs:
           分类元器件参数列表
        create:
           元器件分类新增
        delete:
           元器件分类删除
        update:
           元器件分类更新
    """
    queryset = ElectronCategory.objects.all()
    serializer_class = ElectronCategoryListSerializer

    @action(['get'], detail=True)
    def kwargs(self, request, *args, **kwargs):
        try:
            # electron_category_id = request.query_params['id']
            electon_category = self.get_object()
            kwargs = ElectronKwargs.objects.filter(category=electon_category)
            page = self.paginate_queryset(kwargs)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        except ElectronCategory.DoesNotExist:
            return Response({"count": 0, "links": {"next": "null", "previous": "null"}, "results": []}, status=status.HTTP_200_OK)

    @action(['get'], detail=False)
    def categories_list(self, request):
        electron_categories = ElectronCategory.objects.filter(parent=None)
        serializer = ElectronCategoryListSerializer(electron_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['get'], detail=False)
    def categories_list_level(self, request):
        electron_categories = ElectronCategory.objects.filter(parent=None)
        serializer = ElectronCategorySerializer2(electron_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == 'categories_list':
            return ElectronBackListSerializer
        return ElectronCategorySerializer


# 元器件
class ElectronViewSet(generics.RetrieveUpdateAPIView, generics.ListAPIView, generics.DestroyAPIView, viewsets.GenericViewSet):
    """
        list:
           产品列表
        update:
           产品修改
        retrieve:
           产品详情
        delete:
           产品删除
        hot_electron:
           热门元器件
        apply:
           应用支持（提交）
        applys:
           应用支持（获取）
        videos:
           产品对应的视图
        schemes:
           产品参考设计
        plist:
           pintopin产品列表
        psearch:
           PinToPin搜索匹配
        slist:
            可替换产品列表
        ssearch:
            可替换产品搜索匹配
    """
    queryset = Electron.objects.all()
    serializer_class = ElectronSerializer
    pagination_class = ElectronPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['model_name', 'factory', 'category__name', 'source_web']

    def get_serializer_class(self):
        if self.action == 'list':
            return ElectronBackListSerializer
        elif self.action == 'retrieve' or self.action == 'update':
            return ElectronDetailSerializer
        elif self.action == 'apply' or self.action == 'applys':
            return ElectronApplySerializer
        elif self.action == 'supplier':
            return ElectronSupplierListSerializer
        elif self.action == 'videos':
            return ElectronVideoSerializer
        elif self.action == 'schemes':
            return ElectronSchemeSerializer
        elif self.action in ['psearch', 'ssearch']:
            return ElectronModelSerializer
        elif self.action == 'plist':
            return ElectronPlistSerializer
        elif self.action == 'slist':
            return ElectronSlistSerializer
        else:
            return ElectronSerializer

    @action(['get'], detail=False)
    def hot_electron(self, request):
        """热搜产品配置"""
        try:
            model_name = request.query_params['model_name']
            electron = Electron.objects.get(model_name=model_name)
            electron.is_hot = (not electron.is_hot)
            electron.save()
            return Response({'message': 'ok'}, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)

    # detail=True 需要指定  *args, **kwargs 参数
    @action(['post'], detail=True)
    def apply(self, request, *args, **kwargs):
        """应用支持（提交）"""
        try:
            electron = self.get_object()
            factory_link = request.data['factory_link']
            electron.factory_link = factory_link
            electron.save()
            return Response({"message": "ok"}, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({"message": '没查找到元器件'}, status=status.HTTP_400_BAD_REQUEST)

    @action(['get'], detail=True)
    def applys(self, request, *args, **kwargs):
        """应用支持（获取）"""
        try:
            electron = self.get_object()
            serializer = self.get_serializer(electron)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({"message": '没查找到元器件'}, status=status.HTTP_400_BAD_REQUEST)

    @action(['get'], detail=True)
    def supplier(self, request, *args, **kwargs):
        """获取元器件对应的供应商列表"""
        try:
            electron = self.get_object()
            queryset = ElectronSupplier.objects.filter(electron=electron)
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        except Electron.DoesNotExist:
            message = {"count": 0, "links": {"next": "null", "previous": "null"}, "results": []}
            return Response(message, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def videos(self, request, *args, **kwargs):
        """元器件对应的视频"""
        try:
            electron = self.get_object()
            queryset = ElectronVideo.objects.filter(electron=electron)
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        except Electron.DoesNotExist:
            message = {"count": 0, "links": {"next": "null", "previous": "null"}, "results": []}
            return Response(message, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def schemes(self, request, *args, **kwargs):
        """元器件方案列表（参考设计）"""
        try:
            electron = self.get_object()
            scheme_electrons = Scheme.objects.filter(electrons__model_name__model_name=electron, is_reference=True)
            queryset = [scheme_electron for scheme_electron in scheme_electrons]
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        except SchemeElectron.DoesNotExist:
            message = {"count": 0, "results": []}
            return Response(message, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def plist(self, request, *args, **kwargs):
        """pin_to_pin产品列表"""
        try:
            electron = self.get_object()
            queryset = PinToPin.objects.filter(electron=electron)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def psearch(self, request, *args, **kwargs):
        """pin_to_pin搜索匹配"""
        try:
            model_name = request.query_params['model_name']
            electron = self.get_object()
            pintopins = [p.pin_to_pin for p in PinToPin.objects.filter(electron=electron)]
            electrons = list(Electron.objects.filter(model_name__istartswith=model_name))
            if len(pintopins) == 0:
                serializer = self.get_serializer(electrons, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            electrons = list(set(electrons).difference(set(pintopins)))[:10]
            serializer = self.get_serializer(electrons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({}, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def slist(self, request, *args, **kwargs):
        """可替换产品列表"""
        try:
            electron = self.get_object()
            queryset = SimilarElectron.objects.filter(electron=electron)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def alist(self, request, *args, **kwargs):
        try:
            electron = self.get_object()
            queryset = SimilarElectron.objects.filter(electron=electron)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def ssearch(self, request, *args, **kwargs):
        """可替换产品搜索匹配"""
        try:
            model_name = request.query_params['model_name']
            electron = self.get_object()
            similars = [p.similar for p in SimilarElectron.objects.filter(electron=electron)]
            electrons = Electron.objects.filter(model_name__istartswith=model_name)
            if len(similars) == 0:
                serializer = self.get_serializer(electrons, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            electrons = list(set(electrons).difference(set(similars)))[:10]
            serializer = self.get_serializer(electrons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({}, status=status.HTTP_200_OK)


class FileStorageViewSet(viewsets.ModelViewSet):
    """文件上传接口"""
    queryset = Electron.objects.all()
    serializer_class = FileSerializer


# 可替代产品
class SimilarElectronViewSet(generics.CreateAPIView, generics.DestroyAPIView, viewsets.GenericViewSet):
    """
        create:
            可替换产品新增
        delete:
            可替换产品删除
    """
    queryset = SimilarElectron.objects.all()
    serializer_class = SimilarElectronSerializer

    @action(['get'], detail=True)
    def similar_list(self, request):
        """获取元器件对应的可替换器件列表"""
        try:
            electron_id = request.query_params.get('id', None)
            electron = Electron.objects.get(pk=electron_id)
            similar_electrons = SimilarElectron.objects.filter(electron=electron)
            electrons = [similar.electron for similar in similar_electrons]
            serializer = ElectronSerializer(data=electrons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({"message": '暂无元器件供应商'}, status=status.HTTP_400_BAD_REQUEST)

    @action(['get'], detail=True)
    def similar_add_list(self, request):
        """查询可添加的可替换器件列表"""
        try:
            electron_id = request.query_params.get('id', None)
            electron = Electron.objects.get(pk=electron_id)
            similars = [similar.electron for similar in SimilarElectron.objects.filter(electron=electron)]
            electrons = Electron.objects.all()
            electrons = list(set(electrons).difference(set(similars)))
            serializer = ElectronModelSerializer(electrons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            pass

    @action(['get'], detail=True)
    def del_similar_electron(self, request):
        """可替代元器件删除"""
        try:
            similar_id = request.query_params['id']
            similar_electron = SimilarElectron.objects.get(id=similar_id)
            similar_electron.delete()
            return Response({'message': 'ok'}, status=status.HTTP_200_OK)
        except SimilarElectron.DoesNotExist:
            return Response({'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)


# 供应商信息
class SupplierListViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()
    pagination_class = SupplierPagination


class EletronSupplierViewSet(viewsets.ModelViewSet):
    serializer_class = ElectronSupplierSerializer
    queryset =ElectronSupplier.objects.all()
    pagination_class = SupplierPagination


# 元器件电路图
class ElectronCircuitDiagramViewSet(generics.ListCreateAPIView, viewsets.GenericViewSet):
    queryset = ElectronCircuitDiagram.objects.all()
    serializer_class = ElectronCircuitDiagramSerializer

    def electron_list(self, request, *args, **kwargs):
        """元器件对应的原理图"""
        electron_id = request.query_parmas.get('electron_id', None)
        if electron_id:
            electron = Electron.objects.get(id=electron_id)
            electron_diagrams = ElectronCircuitDiagram.objects.filter(electron=electron)
            serializer = ElectronCircuitDiagramSerializer(electron_diagrams, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)


# 元器件类型参数
class ElectronKwargsViewSet(viewsets.ModelViewSet):
    """
        retrieve:
           元器件参数详情
        list:
           元器件参数列表
        electons_kwargs_list:
           元器件类型参数列表（同类型）
        create:
           元器件参数新增
        delete:
           元器件参数删除
        update:
           元器件更新更新
    """

    queryset = ElectronKwargs.objects.all()
    serializer_class = ElectronKwargsSerializer
    pagination_class = KwargsPagination

    def create(self, request, *args, **kwargs):
        values = request.data['values']
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                # 开启事务批量新增操作
                with transaction.atomic():
                    kwargs = serializer.save()
                    for value in values.split(','):
                        kv = ElectronKwargsValue(kwargs=kwargs, value=value)
                        kv.save()
                return Response({'message': 'ok'}, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                Response({'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                self.perform_update(serializer)
                values = request.data['values']
                ElectronKwargsValue.objects.filter(kwargs=instance).delete()
                for value in values.split(','):
                    kv = ElectronKwargsValue(kwargs=instance, value=value)
                    kv.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(['get'], detail=False)
    def electons_kwargs_list(self, request):
        try:
            electron_category_id = request.query_params['id']
            electon_category = ElectronCategory.objects.get(id=electron_category_id)
            kwargs = ElectronKwargs.objects.filter(category=electon_category)

            page = self.paginate_queryset(kwargs)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        except ElectronCategory.DoesNotExist:
            return Response({"count": 0, "links": {"next": "null", "previous": "null"}, "results": []}, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == 'list':
            return ElectronKwargsSerializer
        elif self.action == 'create':
            return ElectronKwargsValueSerializer
        else:
            return ElectronKwargsSerializer


# 元器件视频
class ElectronVideoViewSet(viewsets.GenericViewSet):
    """
        primary:
        设为主视频
    """
    queryset = ElectronVideo.objects.all()
    serializer_class = ElectronVideoSerializer

    @action(['get'], detail=True)
    def primary(self, request, *args, **kwargs):
        electron_video = self.get_object()
        try:
            primary_electron = ElectronVideo.objects.get(electron=electron_video.electron, is_primary=True)
            primary_electron.is_primary = False
            primary_electron.save()
        except Exception as e:
            print(e)
        electron_video.is_primary = True
        electron_video.save()
        return Response({'message': 'ok'}, status=status.HTTP_200_OK)


# PinToPo元器件消费者
class ElectronConsumerViewSet(viewsets.ModelViewSet):
    queryset = ElectronConsumer.objects.all()
    serializer_class = ElectronConsumerSerializer


# PinToPin元器件
class PinToPinViewSet(generics.DestroyAPIView, generics.CreateAPIView, viewsets.GenericViewSet):
    """
        destory:
        PintoPin产品删除
        create:
        PintoPin产品新增
    """
    queryset = PinToPin.objects.all()
    serializer_class = PinToPinCreateSerializer



