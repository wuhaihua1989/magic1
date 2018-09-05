from rest_framework import (viewsets, status, generics, filters, mixins)
from rest_framework.response import Response
from .serializers import *
from rest_framework.decorators import action
from .pagination import ProductPagination
from apps.electron.models import Electron

# -------用户界面------





# ---------管理界面----------
# Create your views here.
class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
        retrieve:
           产品分类详情
        list:
           产品分类列表（无子类）
        create:
           产品分类新增
        categories_list:
           产品分类列表（有子类）
        delete:
           产品分类删除
        update:
           产品分类更新
    """

    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializers

    @action(['get'], detail=False)
    def categories_list(self, request):
        product_categories = ProductCategory.objects.filter(parent=None)
        serializer = ProductCategorySerializers1(product_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 成品
class ProductViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
        list:
            成品列表
        update:
            成品更新
        delete:
            成品删除
        retrieve:
            成品详情
        sschemes:
            成品方案搜索
        selectron:
            成品产品搜索
    """
    queryset = Product.objects.all()
    serializer_class = ProductListSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'source_web']
    pagination_class = ProductPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializers
        else:
            return ProductDetailSerializers

    @action(['get'], detail=True)
    def sschemes(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            scheme_name = request.query_params['name']
            schemes = [e for e in Scheme.objects.filter(name__istartswith=scheme_name)]
            schemes = list(set(schemes).difference(set(product.scheme)))[:10]
            serializer = ProductSchemeListSerializers(schemes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'models': '未匹配到方案数据'}, status=status.HTTP_400_BAD_REQUEST)

    @action(['get'], detail=True)
    def selectron(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            model_name = request.query_params['model_name']
            p_models = [e.model_name for e in ProductElectron.objects.filter(product=product, model_name__istartswith=model_name)]
            models = [e.model_name for e in Electron.objects.filter(model_name__istartswith=model_name)]
            models_result = list(set(models).difference(set(p_models)))[:10]
            return Response({'models': models_result}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'models': '未匹配到模型数据'}, status=status.HTTP_400_BAD_REQUEST)


# 成品图片
class SchemeImageViewSet(generics.UpdateAPIView, generics.DestroyAPIView, viewsets.GenericViewSet):
    """
        delete:
           成品Image文件删除
        update:
           成品Image文件更新
    """
    queryset = Product.objects.all()
    serializer_class = ProductUploadImageSerializer

    def perform_destroy(self, instance):
        instance.images = ""
        instance.save()


# 成品视频
class ProductVideoViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
            create:
                成品视频新增
            update:
                成品视频修改
            destroy:
                成品视频删除
    """
    queryset = ProductVideo.objects.all()
    serializer_class = ProductVideoListSerializers


# 自定义成品
class CustomProductViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
        list:
            自定义成品
        retrieve:
            自定义成品详情
        destroy:
            自定义成品删除
    """
    queryset = CustomProduct.objects.all()
    serializer_class = CustomProductListSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['consumer__username']
    pagination_class = ProductPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomProductListSerializers
        else:
            return CustomProductDetailSerializer


# 自定义产品方案
class CustomProductSchemeViewSet(viewsets.ModelViewSet):
    queryset = CustomProductScheme.objects.all()
    serializer_class = CustomProductSchemeSerializers


# 自定义产品元器件
class CustomProductElectronViewSet(viewsets.ModelViewSet):
    queryset = CustomProductElectron.objects.all()
    serializer_class = CustomProductElectronSerializers

