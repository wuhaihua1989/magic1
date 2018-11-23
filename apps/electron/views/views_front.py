from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
import json
import redis

from apps.electron.models import Electron, ElectronSupplier, ElectronVideo
from apps.electron.models import ElectronKwargsValueFront
from apps.electron.models import ElectronCircuitDiagram

from apps.product.models import Product, ProductCategory
from apps.scheme.models import SchemeElectron, SchemeCategory, Scheme
from apps.electron.pagination import Pagination

from apps.electron.serializer.serializers_back import ElectronSupplierListSerializer
from apps.electron.serializer.serializers_back import ElectronApplySerializer
from apps.electron.serializer.serializers_back import ElectronSchemeSerializer

from apps.electron.serializer.serializers_front import ElectronDetailVideoSerializer
from apps.electron.serializer.serializers_front import SkuDetailSerializer
from apps.electron.serializer.serializers_front import HotElectronSerializer
from apps.electron.serializer.serializers_front import ElectronsSerializer
from apps.electron.serializer.serializers_front import PinToPinsElectronSerializer
from apps.electron.serializer.serializers_front import SimiliarElectronSerializer
from apps.electron.serializer.serializers_front import ProductSerializers
from apps.electron.serializer.serializers_front import ElectronDetailsSerializer
from apps.electron.serializer.serializers_front import ElectronContrastSerializer
from apps.electron.serializer.serializers_front import SchemeCategorySerializer
from apps.electron.serializer.serializers_front import ElectronsKwargsSerializer
from apps.electron.serializer.serializers_front import SearchSchemeSerializer
from apps.electron.serializer.serializers_front import CircuitSerializer


class ElectronDetailViewSet(generics.RetrieveUpdateAPIView, generics.ListAPIView,
                            generics.DestroyAPIView, viewsets.GenericViewSet):
    """
        retrieve:
            产品详情
         applys:
            应用支持
         videos:
            产品对应的视频
         schemes:
           产品参考设计
         Kwargs:
             产品参数
         Supplier:
             更多供应商
    """
    queryset = Electron.objects.all()
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action == 'supplier':
            return ElectronSupplierListSerializer
        elif self.action == 'applys':
            return ElectronApplySerializer
        elif self.action == 'videos':
            return ElectronDetailVideoSerializer
        elif self.action == 'schemes':
            return ElectronSchemeSerializer
        elif self.action == 'circuitdiagram':
            return CircuitSerializer

        else:
            return SkuDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # 如果用户登录, 保存用户最后浏览的元器件类型ID
        if self.request.user.username:
            username = self.request.user.username
            conn = redis.Redis(host="127.0.0.1", port=6379, db=6)
            electron = Electron.objects.get(id=int(kwargs['pk']))
            electron_category_id = electron.category_id
            category_id = conn.get("%s_recommend_electron_category_id" % username)
            if not category_id or int(category_id) != electron_category_id:
                conn.set("%s_recommend_electron_category_id" % username, electron_category_id, ex=None)
        return Response(serializer.data)

    @action(['get'], detail=True)
    def applys(self, request, *args, **kwargs):
        """应用支持（获取）"""
        try:
            electron = self.get_object()
            serializer = self.get_serializer(electron)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({"message": ''}, status=status.HTTP_400_BAD_REQUEST)

    @action(['get'], detail=True)
    def circuitdiagram(self, request, *args, **kwargs):
        """获取元器件电路图"""
        try:
            queryset = ElectronCircuitDiagram.objects.filter(electron_id=int(self.kwargs['pk']))
            serializer = CircuitSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": e})

    @action(['get'], detail=True)
    def supplier(self, request, *args, **kwargs):
        """获取元器件对应的供应商列表"""
        try:

            electron = self.get_object()
            queryset = ElectronSupplier.objects.filter(electron=electron)
            serializer = ElectronSupplierListSerializer(queryset, many=True)

            page = self.paginate_queryset(serializer.data)
            if page is not None:
                return self.get_paginated_response(page)

            serializer = ElectronSupplierListSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            message = {"count": 0, "links": {"next": "null", "previous": "null"},"results": []}
            return Response({}, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def videos(self, request, *args, **kwargs):
        """元器件对应的视频"""
        try:
            queryset = ElectronVideo.objects.filter(electron_id=int(self.kwargs['pk']))
            serializer = ElectronDetailVideoSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": e})

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


class ElectronSuppliersViewSet(ListModelMixin, viewsets.GenericViewSet):
    """
    供应商信息表
    """
    queryset = Electron.objects.all()
    serializer_class = ElectronDetailsSerializer

    def list(self, request, *args, **kwargs):
        try:
            electron = request.query_params['electron_id']
            instance = Electron.objects.get(id=electron)
            queryset = ElectronSupplier.objects.filter(electron=instance).order_by('create_at')[:3]
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)


class HotElectronViewSet(ListModelMixin, viewsets.GenericViewSet):
    """
    首页热搜产品
    """
    queryset = Electron.objects.all()
    serializer_class = HotElectronSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = Electron.objects.filter(is_hot=True)[:6]
            serializer = HotElectronSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)


class ElectronsSearchsViewSet(ReadOnlyModelViewSet):
    """
    首页搜索
    """
    queryset = Electron.objects.all()
    serializer_class = ElectronsSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        model_name = request.query_params['model_name']
        try:
            electrons = Electron.objects.filter(model_name__istartswith=model_name)
            serializer = self.get_serializer(electrons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({}, status=status.HTTP_200_OK)


class SimilarSearchsViewSet(ReadOnlyModelViewSet):
    """
    可替代型号搜索结果
    """
    queryset = Electron.objects.all()
    serializer_class = ElectronsSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        model_name = request.query_params['model_name']
        queryset3 = Electron.objects.filter(model_name=model_name)
        serializer3 = ElectronsSerializer(queryset3, many=True)
        try:
            instance = Electron.objects.get(model_name=model_name)
            query_set = instance.pin_electron.order_by('create_at')
            count1 = query_set.count()
            if not len(query_set) < 4:
                query_set = query_set[:4]
                serializer = PinToPinsElectronSerializer(query_set, many=True)
                electron_data = {
                    "model_name": serializer3.data,
                    "count": count1,
                    "electron": serializer.data[:4]
                }
                for electron_similar in serializer.data:
                    supplier = electron_similar["pin_to_pin"]["supplier"]
                    supplier_order = sorted(supplier, key=lambda x: x["create_at"], reverse=True)
                    data = supplier_order[:3]
                    electron_similar["pin_to_pin"]["supplier"] = data

                return Response(electron_data, status=status.HTTP_200_OK)
            if len(query_set) > 1:
                serializer1 = PinToPinsElectronSerializer(query_set, many=True)
                for electron_similar in serializer1.data:
                    supplier = electron_similar["pin_to_pin"]["supplier"]
                    supplier_order = sorted(supplier, key=lambda x: x["create_at"], reverse=True)
                    data1 = supplier_order[:3]
                    electron_similar["pin_to_pin"]["supplier"] = data1
                query_set2 = instance.similar_electron.order_by('create_at')
                count2 = query_set2.count()
                count3 = count1+count2
                serializer2 = SimiliarElectronSerializer(query_set2, many=True)
                data = (serializer1.data+serializer2.data)[:4]
                electron_data = {
                    "model_name": serializer3.data,
                    "count": count3,
                    "data": data[:4],

                }
                for electron_similar in serializer2.data:
                    supplier = electron_similar["similar"]["supplier"]
                    supplier_order = sorted(supplier, key=lambda x: x["create_at"], reverse=True)
                    data2 = supplier_order[:3]
                    electron_similar["similar"]["supplier"] = data2
                return Response(electron_data, status=status.HTTP_200_OK)
            query_set2 = instance.similar_electron.order_by('create_at')
            serializer2 = SimiliarElectronSerializer(query_set2, many=True)
            count2 = query_set2.count()
            electron_data = {
                "model_name": serializer3.data,
                "count": count2,
                "similiar": serializer2.data[:4]
            }
            for electron_similar in serializer2.data:
                supplier = electron_similar["similar"]["supplier"]
                supplier_order = sorted(supplier, key=lambda x: x["create_at"], reverse=True)
                data = supplier_order[:3]
                electron_similar["similar"]["supplier"] = data
            return Response(electron_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"status":301},status=status.HTTP_200_OK)


class ElectronListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    可替代元器件查询
    """
    pagination_class = Pagination
    queryset = Electron.objects.all()

    def list(self, request, *args, **kwargs):
        model_name = request.query_params['model_name']
        pin_to_pin = request.query_params.get('pin_to_pin', None)
        origin = request.query_params.get('origin', None)
        platform_price_min = request.query_params.get('platform_price_min', None)
        platform_price_max = request.query_params.get('platform_price_max', None)
        market_date_at = request.query_params.get('market_date_at', None)
        queryset = Electron.objects.get(model_name=model_name)

        if pin_to_pin:
            queryset = queryset.pin_electron
            if origin:
                queryset = queryset.filter(pin_to_pin__origin=origin)
            if platform_price_min:
                queryset = queryset.filter(pin_to_pin__platform_price__gte=platform_price_min)
            if platform_price_max:
                queryset = queryset.filter(pin_to_pin__platform_price__lte=platform_price_max)
            if market_date_at:
                queryset = queryset.filter(pin_to_pin__market_date_at__year=market_date_at)
            serializer = PinToPinsElectronSerializer(queryset, many=True)
            for electron_similar in serializer.data:
                supplier = electron_similar["pin_to_pin"]["supplier"]
                supplier_order = sorted(supplier, key=lambda x: x["create_at"], reverse=True)
                data = supplier_order[:3]
                electron_similar["pin_to_pin"]["supplier"] = data

            page = self.paginate_queryset(serializer.data)
            if page is not None:
                return self.get_paginated_response(page)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            querysets = queryset.pin_electron.all()
            if origin:
                querysets = querysets.filter(pin_to_pin__origin=origin)
            if platform_price_min:
                querysets = querysets.filter(pin_to_pin__platform_price__gte=platform_price_min)
            if platform_price_max:
                querysets = querysets.filter(pin_to_pin__platform_price__lte=platform_price_max)
            if market_date_at:
                querysets = querysets.filter(pin_to_pin__market_date_at__year=market_date_at)
            queryset = queryset.similar_electron.all()
            if origin:
                queryset = queryset.filter(similar__origin=origin)
            if platform_price_min:
                queryset = queryset.filter(similar__platform_price__gte=platform_price_min)
            if platform_price_max:
                queryset = queryset.filter(similar__platform_price__lte=platform_price_max)
            if market_date_at:
                queryset = queryset.filter(similar__market_date_at__year=market_date_at)
            serializer1 = PinToPinsElectronSerializer(querysets, many=True)
            for electron_similar in serializer1.data:
                supplier = electron_similar["pin_to_pin"]["supplier"]
                supplier_order = sorted(supplier, key=lambda x: x["create_at"], reverse=True)
                data = supplier_order[:3]
                electron_similar["pin_to_pin"]["supplier"] = data
            serializer = SimiliarElectronSerializer(queryset, many=True)
            for electron_similar in serializer.data:
                supplier = electron_similar["similar"]["supplier"]
                supplier_order = sorted(supplier, key=lambda x: x["create_at"], reverse=True)
                data = supplier_order[:3]
                electron_similar["similar"]["supplier"] = data

            page = self.paginate_queryset((serializer.data + serializer1.data))
            if page is not None:
                return self.get_paginated_response(page)
            return Response((serializer.data+serializer1.data), status=status.HTTP_200_OK)


class SchemeQueryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """匹配方案搜索结果"""
    queryset = Scheme.objects.all()
    serializer_class = SearchSchemeSerializer
    pagination_class = Pagination

    def list(self, request, *args, **kwargs):
        model_name = self.request.query_params["model_name"]
        is_reference = self.request.query_params.get("is_reference", '')
        category = self.request.query_params.get("category", '')

        queryset = Scheme.objects.filter(electrons__model_name__model_name=model_name)
        if is_reference != '':
            if int(is_reference) == 1:
                queryset = queryset.filter(is_reference=1)
            else:
                queryset = queryset.filter(is_reference=0)

        if category != '':
            queryset = queryset.filter(category_id=int(category))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductsQueryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    成品查询
    """

    pagination_class = Pagination
    queryset = Product.objects.all()
    serializer_class = ProductSerializers

    def list(self, request, *args, **kwargs):
        model_name = request.query_params['model_name']
        origin = request.query_params.get('origin', None)
        category = request.query_params.get('category_id', None)
        market_date_at = request.query_params.get('market_date_at', None)
        queryset = Product.objects.filter(electrons__model_name__model_name=model_name)
        if origin:
            queryset = queryset.filter(origin=origin)
        if category:
            queryset = queryset.filter(category=category)
        if market_date_at:
            queryset = queryset.filter(market_date_at__year=market_date_at)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ElectronContrastViewSet(ListModelMixin, viewsets.GenericViewSet):
    """
    产品对比
    """
    queryset = Electron.objects.all()
    serializer_class = ElectronContrastSerializer

    def list(self, request, *args, **kwargs):
        try:
            electrons = request.query_params['electron_id']

            electron_id = json.loads(electrons)
            queryset = []
            for single_electron in electron_id:
                electron = Electron.objects.get(id=single_electron)
                electron_dict = {
                    'id': electron.id,
                    'model_name': electron.model_name,
                    'images': electron.images,
                    'platform_price': electron.platform_price,
                    'market_date_at': electron.market_date_at,
                    'factory': electron.factory
                }
                kwargs = ElectronKwargsValueFront.objects.filter(electron_id=single_electron, kwargs__is_substitute=True)
                serializer1 = ElectronsKwargsSerializer(kwargs, many=True)

                electron_dict['parameter'] = serializer1.data
                queryset.append(electron_dict)
            return Response(queryset, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)


class SchemeCategoryViewSet(ReadOnlyModelViewSet):
    """
    方案类型
    """
    queryset = SchemeCategory.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            category = SchemeCategory.objects.all()
            serializer = SchemeCategorySerializer(category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SchemeCategory.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)


class ProductCategoryViewSet(ReadOnlyModelViewSet):
    """
    成品分类
    """
    queryset = ProductCategory.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            category = ProductCategory.objects.all()
            serializer = SchemeCategorySerializer(category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProductCategory.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)