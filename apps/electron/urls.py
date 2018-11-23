from django.conf.urls import include, url
from apps.electron.views import views_front, views_back
from rest_framework import routers
from magic.settings import PREFIX_BACK

router = routers.DefaultRouter()
router.register(PREFIX_BACK + 'electrons/electron', views_back.ElectronViewSet)  # 后台元器件详情页面
router.register(PREFIX_BACK + 'electrons/categories', views_back.ElectronCategoryViewSet)  # 后台元器件分类
router.register(PREFIX_BACK + 'electrons/kwargs', views_back.ElectronKwargsViewSet)  # 后台元器件参数
router.register(PREFIX_BACK + 'electrons/suppliers', views_back.SupplierListViewSet)  # 供应商信息
router.register(PREFIX_BACK + 'electrons/circuit_diagrams', views_back.ElectronCircuitDiagramViewSet)  # 后台元器件电路图
router.register(PREFIX_BACK + 'electrons/detail', views_back.FrontElectronDetailViewSet)  # 后台元器件详情
router.register(PREFIX_BACK + 'electrons/datasheet', views_back.FileStorageViewSet)  # 后台上传数据表
router.register(PREFIX_BACK + 'electrons/video', views_back.ElectronVideoViewSet)  # 后台设置元器件视频
router.register(PREFIX_BACK + 'electrons/pelectron', views_back.PinToPinViewSet)  # 后台PinToPin元器件
router.register(PREFIX_BACK + 'electrons/selectron', views_back.SimilarElectronViewSet)  # 后台查询可替代产品

router.register(PREFIX_BACK + 'electrons/detail', views_front.ElectronDetailViewSet)  # 前台产品详情页面
router.register(PREFIX_BACK + 'electrons/suppliers', views_front.ElectronSuppliersViewSet)  # 前台产品详情页供应商信息
router.register(PREFIX_BACK+'electrons/searchs', views_front.ElectronsSearchsViewSet)  # 前台首页搜索功能
router.register(PREFIX_BACK+'electrons/Similar', views_front.SimilarSearchsViewSet)  # 前台搜索结果页面可替代型号
router.register(PREFIX_BACK+'electrons/filtrate', views_front.ElectronListViewSet)  # 前台搜索结果页面可替代型号查询
router.register(PREFIX_BACK+'electrons/electroncontrast', views_front.ElectronContrastViewSet)  # 前台搜索结果对比页面
router.register(PREFIX_BACK+'electrons/SchemeQuery', views_front.SchemeQueryViewSet)  # 前台搜索结果页面更多方案查询
router.register(PREFIX_BACK+'electrons/ProductsQuery', views_front.ProductsQueryViewSet)  # 前台搜索结果页面更多成品查询
router.register(PREFIX_BACK+'electrons/SchemeCategory', views_front.SchemeCategoryViewSet)  # 方案分类
router.register(PREFIX_BACK+'electrons/ProductCategory', views_front.ProductCategoryViewSet)  # 成品分类


urlpatterns = [
    url(r'^'+PREFIX_BACK+'hot', views_front.HotElectronViewSet.as_view({'get': 'list'})),  # 首页热搜产品
    url('', include(router.urls)),
]
