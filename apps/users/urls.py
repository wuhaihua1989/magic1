from django.conf.urls import (include, url)
from apps.users.views import *
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token
from . import views
from magic.settings import PREFIX, PREFIX_BACK
from apps.users.views import *


router = routers.DefaultRouter()
router.register(PREFIX_BACK + 'groups', GroupViewSet)
router.register(PREFIX_BACK + 'permissions', PermissionViewSet)
router.register(PREFIX_BACK + 'menus', MenuViewSet)
index = IndexViewSet.as_view({'get': 'list'})
user_back_login = UserViewSet.as_view()
urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^ic/usernames/(?P<username>\w{5,20})/count/$', views.UserNameCountView.as_view()),
    url(r'^ic/mobiles/(?P<mobile>1[345789]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^ic/users/$', views.UserView.as_view()),
    url(r'^ic/authorizations/$', views.UserAuthorizeView.as_view(), name='authorizations'),  # 登陆视图
    url(r"^ic/accounts/(?P<account>\w{5,20})/sms/token/$", views.SMSCodeTokenView.as_view()),
    url(r"^ic/accounts/(?P<account>\w{5,20})/password/token/$", views.PasswordTokenView.as_view()),
    url(r"^ic/users/(?P<pk>\d+)/password/$", views.PasswordView.as_view()),
    url(r"^ic/user/detail$", views.UserDetailView.as_view()),
    url(r'^' + PREFIX_BACK + 'backenduser/login/', user_back_login , name='后台用户登陆'),
    url(r'^' + PREFIX_BACK + 'index/', index, name='后台用户首页'),

]