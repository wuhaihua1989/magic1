from rest_framework import viewsets, status, filters, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from apps.product.pagination import Pagination
from ..filters import ProductFilter, CustomUserFilter

from apps.electron.models import Electron
from apps.scheme.models import Scheme
from apps.product.models import ProductCategory, Product, CustomProduct

from apps.product.serializer.serializers_back import ProductCategorySerializers, ProductCategorySerializers1
from apps.product.serializer.serializers_back import ProductListSerializers, ProductDetailSerializers
from apps.product.serializer.serializers_back import ProductSchemeListSerializers, ProductElectronDetailSerializers
from apps.product.serializer.serializers_back import CustomProductListSerializers, CustomProductDetailSerializer


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


class ProductViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    成品
        list:
            成品列表
        update:
            成品修改
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
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductFilter
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializers
        else:
            return ProductDetailSerializers

    @action(['get'], detail=True)
    def sschemes(self, request, *args, **kwargs):
        """成品方案搜索"""
        try:
            product = self.get_object()
            product_schemes = set(product.scheme.all())
            scheme_title = request.query_params['title']
            schemes = set(Scheme.objects.filter(title__istartswith=scheme_title))
            difference_schemes = list(schemes.difference(product_schemes))[:10]
            serializer = ProductSchemeListSerializers(difference_schemes, many=True)
            if serializer.data:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"fail": "数据库未收录该方案", "status": 1001}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': e}, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def selectron(self, request, *args, **kwargs):
        """成品BOM器件搜索"""
        try:
            product = self.get_object()
            model_name = request.query_params['model_name']
            product_electrons = set(Electron.objects.filter(pro_electrons__product=product))
            electrons = set(Electron.objects.filter(model_name__istartswith=model_name))
            difference_electrons = list(electrons.difference(product_electrons))[:10]
            serializer = ProductElectronDetailSerializers(difference_electrons, many=True)
            if serializer.data:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"fail": "数据库未收录该元器件", "status": 1001}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': e}, status=status.HTTP_200_OK)


class CustomProductViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    成品定制
        list:
            成品定制列表
        retrieve:
            成品定制详情
        destroy:
            成品定制删除
    """
    queryset = CustomProduct.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filter_class = CustomUserFilter
    search_fields = ['consumer__username']
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomProductListSerializers
        else:
            return CustomProductDetailSerializer

