from django.db import models
from django.conf import settings
from .constants import *
from django.contrib.auth.models import (Permission, Group, AbstractUser, ContentType)
from utils.Basemodels import BaseModel
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSerializer
from itsdangerous import BadData
# Create your models here.


class User(AbstractUser):
    """
     用户模型类
     """
    gender_choices = ((u'1', u'男'), (u'0', u'女'))
    mobile = models.CharField(max_length=11, verbose_name="手机号码")
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,on_delete=models.SET_NULL, verbose_name='默认地址')
    icon = models.TextField(verbose_name='头像', null=True, blank=True)
    rel_name = models.CharField(max_length=188, verbose_name='真实姓名', help_text='真实姓名', null=True, blank=True)

    qq = models.CharField(max_length=20, verbose_name='QQ号码', help_text='QQ号码', null=True, blank=True)
    is_member = models.BooleanField(default=True, verbose_name='会员', help_text='会员')

    gender = models.CharField(max_length=2, choices=gender_choices, verbose_name='性别', help_text='性别', null=True,
                              blank=True)

    profession = models.ForeignKey('Professions', on_delete=models.CASCADE, verbose_name='职业',related_name='pro_p', help_text='职业', null=True,blank=True)
    name = models.CharField(max_length=88)
    industry = models.ForeignKey('Industry', on_delete=models.CASCADE, verbose_name='行业',related_name='ins_i', help_text='行业', null=True, blank=True)
    # 企业还是个人用户，预留辨别字段
    company_name = models.CharField(max_length=188, verbose_name='公司名称', help_text='公司名称', null=True, blank=True)
    company_tel_number = models.CharField(max_length=188, verbose_name='电话号码', help_text='电话号码', null=True, blank=True)
    company_fax_number = models.CharField(max_length=188, verbose_name='传真', help_text='传真', null=True, blank=True)
    company_tax_number = models.CharField(max_length=188, verbose_name='纳税识别号', help_text='纳税识别号', null=True,blank=True)

    company_address = models.CharField(max_length=188, verbose_name='公司地址', help_text='地址', null=True, blank=True)

    class Meta:
        db_table = "m_users"
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name


    def generate_sms_code_token(self):
        """生成发送短信的临时票据[access_token]"""
        # TJWSerializer(秘钥,token有效期[秒])
        serializer = TJWSerializer(settings.SECRET_KEY, SMS_CODE_TOKEN_EXPIRES)
        # serializer.dumps(数据), 返回bytes类型
        token = serializer.dumps({'mobile': self.mobile})
        # 把bytes转成字符串
        token = token.decode()
        return token

    @staticmethod
    def check_sms_code_token(access_token):
        """检验发送短信的临时票据[access_token]"""
        serializer = TJWSerializer(settings.SECRET_KEY, SMS_CODE_TOKEN_EXPIRES)
        data = serializer.loads(access_token)
        return data['mobile']

    def generate_password_token(self):
        """生成重置密码的临时票据[access_token]"""
        # TJWSerializer(秘钥,token有效期[秒])
        serializer = TJWSerializer(settings.SECRET_KEY, SMS_CODE_TOKEN_EXPIRES)
        # serializer.dumps(数据), 返回bytes类型
        token = serializer.dumps({'user': self.id})
        # 把bytes转成字符串
        token = token.decode()
        return token




# 职业
class Professions(BaseModel):
    """职业"""
    name = models.CharField(max_length=88)
    # parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='pro', null=True, blank=True,verbose_name='职业类')


    class Meta:
        db_table = 'm_profession'
        verbose_name = u"职业"
        verbose_name_plural = u'职业'


class Industry(BaseModel):
    """"""
    name = models.CharField(max_length=88)
    # parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='ins', null=True, blank=True,verbose_name='行业类')

    class Meta:
        db_table = 'm_Industry'
        verbose_name = u"行业"
        verbose_name_plural = u'行业'


# 收货地址
class Address(BaseModel):
    """收货地址 """
    consumer = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='关联消费者')
    province = models.ForeignKey('Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')

    city = models.ForeignKey('Area'
                             , on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('Area', on_delete=models.PROTECT, related_name='district_addresses',verbose_name='区')

    address = models.CharField(max_length=188, verbose_name='详细地址')
    signer_name = models.CharField(max_length=188, verbose_name='签收人')
    signer_mobile = models.CharField(max_length=11, verbose_name='签收人号码')
    is_default = models.BooleanField(default=False, verbose_name='是否是默认地址')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'm_sign_address'
        verbose_name = u'收货地址'
        verbose_name_plural = u'收货地址'


class Area(models.Model):
    """
    行政区划
    """
    name = models.CharField(max_length=20, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,verbose_name='上级行政区划')


    class Meta:
        db_table = 'm_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name


# 自定义权限类
class CustomPermission(models.Model):
    """自定义权限类"""

    class Meta:
        db_table = 'm_custom_permission'
        verbose_name = u'自定义权限'
        verbose_name_plural = u'自定义权限'
        # 命名为cms设计稿里面对应 '菜单权限' 的地方, 例如用户管理
        permissions = (
            ("custom_permission_electronmanage", u"产品管理"),
            ("custom_permission_electrolist", u"产品列表"),
            ("custom_permission_schememanage", u"方案管理"),
            ("custom_permission_schemelist", u"方案列表"),
            ("custom_permission_product", u"成品管理"),
            ("custom_permission_productlist", u"成品列表"),
            ("custom_permission_productcustom", u"成品制作"),
            ("custom_permission_usermanage", u"用户管理"),
            ("custom_permission_userlist", u"用户列表"),
            ("custom_permission_ordermanage", u"订单管理"),
            ("custom_permission_config", u"平台配置"),
            ("custom_permission_electrontype", u"器件分类"),
            ("custom_permission_schemetype", u"方案分类"),
            ("custom_permission_producttype", u"成品分类"),
            ("custom_permission_contenttype", u"内容管理"),
            ("custom_permission_freighconfig", u"运费配置"),
            ("custom_permission_website", u"网页信息"),
        )


class Menu(models.Model):
    """菜单类"""
    parent = models.ForeignKey("self", on_delete=models.CASCADE, verbose_name='上级菜单', help_text='上级菜单', null=True,
                               blank=True, related_name='children')
    cname = models.CharField(max_length=366, verbose_name='菜单中文名称', help_text='菜单中文名称')
    ename = models.CharField(max_length=366, verbose_name='菜单英文名', help_text='菜单英文名')
    path = models.CharField(max_length=366, verbose_name='路由配置', help_text='路由配置')
    permissions = models.ManyToManyField(Permission, verbose_name='权限', help_text='权限')

    class Meta:
        db_table = 'm_menu'
        verbose_name = u'菜单'
        verbose_name_plural = u'菜单'

    def __str__(self):
        return self.cname


class RoleMenu(models.Model):
    """角色菜单管理"""
    role = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='角色')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name='菜单')

    class Meta:
        db_table = 'm_role_menu'
        verbose_name = u'角色菜单权限'
        verbose_name_plural = u'角色菜单权限'

    def __str__(self):
        return self.role.name