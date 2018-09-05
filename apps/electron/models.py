from django.db import models
from apps.users.models import User
from utils.Basemodels import BaseModel


# Create your models here.
# 元器件类型
class ElectronCategory(models.Model):
    """元器件类型"""
    name = models.CharField(max_length=188, verbose_name='类型', unique=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.CharField(max_length=512,verbose_name='类型图片', null=True, blank=True)

    class Meta:
        db_table = 'm_electron_category'
        verbose_name = u"电子元器件类型"
        verbose_name_plural = u'电子元器件类型'

    def __str__(self):
        return self.name





# 元器件系统图
class ElectronCircuitDiagram(BaseModel):
    """电路图"""
    name = models.CharField(max_length=188, verbose_name='电路图名称')    
    diagram = models.TextField(verbose_name='图片地址', null=True, blank=True)
    electron = models.ForeignKey("electron.Electron", on_delete=models.CASCADE, verbose_name='电子元器件')


    class Meta:
        db_table = 'm_circuit_diagram'
        verbose_name = u"电路图"
        verbose_name_plural = u'电路图'


# 元器件参数
class ElectronKwargs(models.Model):
    """参数"""
    electron = models.ForeignKey(ElectronCategory, on_delete=models.CASCADE, verbose_name='类型')
    cname = models.CharField(max_length=188, unique=True, verbose_name='名称')  # 电流
    ename = models.CharField(max_length=188, verbose_name='英文名')
    is_contrast = models.BooleanField(default=False, verbose_name='是否是比较参数')
    is_substitute = models.BooleanField(default=False, verbose_name='是否是对比参数')

    class Meta:
        db_table = 'm_electron_kwargs'
        verbose_name = u"元器件参数"
        verbose_name_plural = u'元器件参数'


# 元器件参数值（后期参数检索可能会用到的字段）
class ElectronKwargsValue(models.Model):
    kwargs = models.ForeignKey(ElectronKwargs, on_delete=models.CASCADE, verbose_name='参数', help_text='参数')
    value = models.CharField(max_length=166, help_text='参数值', verbose_name='参数值')

    class Meta:
        db_table = 'm_electron_kwargs_value'
        verbose_name = u'元器件参数值'
        verbose_name_plural = u'元器件参数值'


# 元器件
class Electron(BaseModel):
    """电子元器件"""
    origin_choices = ((u'1', u'国内'), (u'0', u'国外'))

    name = models.CharField(max_length=188, verbose_name="名称")
    model_name = models.CharField(max_length=188, verbose_name='型号', unique=True)
    views = models.IntegerField(verbose_name="浏览量", null=True, blank=True)
    images = models.TextField(verbose_name='图片地址', null=True, blank=True)
    is_supply = models.BooleanField(default=False, verbose_name='平台有无货')
    is_hot = models.BooleanField(default=False, verbose_name='是否热销')
    factory = models.CharField(max_length=366, verbose_name='产商', null=True, blank=True)
    category = models.ForeignKey(ElectronCategory, related_name="electrons",
                                 on_delete=models.CASCADE, verbose_name='类型')

    source_web = models.CharField(max_length=366, verbose_name='来源站点')  # 如果是用户创建的话，站点是用户名

    price = max_money = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='平台价格')
    specifc = models.CharField(max_length=388, verbose_name="特性", null=True, blank=True)
    # 对应元器件参数表 存储ID
    "电压，电容，电阻"
    kwargs = models.CharField(max_length=188, verbose_name="参数编号(','分隔)", null=True, blank=True)
    # 对应元器件的参数值，和元器件表中的参数值无关
    "1.5，3.0V，4.5V (存储数据的值，参数值模型表无关)"
    kwargs_values = models.CharField(max_length=388, verbose_name="参数值(','分隔)", null=True, blank=True)


    desc_specific = models.TextField(verbose_name='描述', null=True, blank=True)  # html 编辑器
    data_sheet_name = models.CharField(max_length=188, verbose_name='数据表名称', null=True, blank=True)
    data_sheet = models.CharField(max_length=388, verbose_name='数据表', null=True, blank=True)  # pdf 数据表

    origin = models.CharField(max_length=266, choices=origin_choices, verbose_name='产地', null=True, blank=True)
    market_date_at = models.DateTimeField(verbose_name='上市时间', null=True)  # 站点爬取
    supplier = models.ManyToManyField("Supplier", through="electron.ElectronSupplier", verbose_name='供应商')  # 自定义第三张表


    # 应用支持 apply_support = ""
    factory_link = models.CharField(max_length=266, verbose_name='原厂链接', null=True, blank=True)
    linkman = models.CharField(max_length=166, verbose_name='联系人', null=True, blank=True)
    phone = models.CharField(max_length=166, verbose_name='联系电话', null=True, blank=True)

    # pintopin 通过查询PinToPin 表匹配
    # unit = models.FloatField()
    # factory = models.ManyToManyField(Factory)
    # brand = models.ManyToManyField(Brand)

    class Meta:
        db_table = 'm_electron'
        verbose_name = u"电子元器件"
        verbose_name_plural = u'电子元器件'

    def __str__(self):
        return self.model_name


# PinToPin元器件(完全可替换)
class PinToPin(BaseModel):
    """相同元器件型号 （关系联结）pin to pin"""

    pin_to_pin = models.ForeignKey(Electron, related_name='pin_to_pin_electron', on_delete=models.CASCADE, verbose_name='PintoPin元器件')


    class Meta:
        db_table = 'm_pintopin'
        verbose_name = u"PinToPin"
        verbose_name_plural = u'PinToPin'
        unique_together = ('electron', 'pin_to_pin')


# 可替换元器件（部分相似）
class SimilarElectron(BaseModel):
    """相同元器件型号 （关系联结）pin to pin"""

    similar = models.ForeignKey(Electron, related_name='similar_electrons', on_delete=models.CASCADE, verbose_name='可替换元器件')


    class Meta:
        db_table = 'm_electron_similar'
        verbose_name = u'可替换元器件'
        verbose_name_plural = u'可替换元器件'
        unique_together = ('electron', 'similar')





# 元器件供应商
class ElectronSupplier(BaseModel):
    """供应商器件"""
    electron = models.ForeignKey('Electron', on_delete=models.CASCADE, verbose_name='电子元器件')
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, verbose_name="供应商")
    inventory = models.IntegerField(verbose_name="存量", null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    batch_no = models.CharField(max_length=188, verbose_name='批号')  # 最终生产时间


    class Meta:
        db_table = 'm_electron_supplier'
        verbose_name = u"供应商元器件"
        verbose_name_plural = u'供应商元器件'

    def __str__(self):
        return self.electron.name + '-' + self.supplier.name

    # 供应商
class Supplier(models.Model):
    """供应商"""
    name = models.CharField(max_length=188, verbose_name='名称')
    phone_number = models.CharField(max_length=166, verbose_name='联系方式', null=True, blank=True)
    address = models.CharField(max_length=366, verbose_name='地址', null=True, blank=True)

    class Meta:
        db_table = 'm_supplier'
        verbose_name = u"供应商"
        verbose_name_plural = u'供应商'

    def __str__(self):
        return self.name

# 元器件视频
class ElectronVideo(BaseModel):
    """元器件视频"""
    electron = models.ForeignKey(Electron, on_delete=models.CASCADE, verbose_name='元器件')
    url = models.TextField(verbose_name='视频地址', null=True, blank=True)
    title = models.CharField(max_length=188, verbose_name='标题')
    ispay = models.BooleanField(default=False, verbose_name='是否支付')
    ishare = models.BooleanField(default=False, verbose_name="是否分享")
    is_primary = models.BooleanField(default=False, verbose_name='是否是主视频')  # 主视频能大于15秒，否则设置失败


    class Meta:
        db_table = 'm_electron_video'
        verbose_name = u'元器件视频'
        verbose_name_plural = u'元器件视频'

    def __str__(self):
        return self.title


# 元器件消费者
class ElectronConsumer(models.Model):
    """消费者对于的元器件操作权限"""
    electron = models.ForeignKey(Electron, on_delete=models.CASCADE, verbose_name='电子元器件')
    consumer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='消费者')
    ispay = models.BooleanField(default=False, verbose_name='是否支付')
    ishare = models.BooleanField(default=False, verbose_name="是否分享")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'm_electron_consumer'
        verbose_name = u'已支付元器件'
        verbose_name_plural = u'已支付元器件'


# 评论类
class UniversalComment(models.Model):
    """通用评论存储表"""
    universal_choices = (('1', '元器件'), ('2', '应用方案'), ('3', '成品'))
    type = models.CharField(max_length=10, choices=universal_choices, verbose_name='评论类型')
    universal_id = models.IntegerField(verbose_name='编号(元器件,方案,成品)')
    consumer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论人')
    content = models.TextField(verbose_name='评论内容')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'm_electron_comment'
        verbose_name = u"评论"
        verbose_name_plural = u'评论'


