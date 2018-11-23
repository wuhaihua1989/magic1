from rest_framework import serializers
from django_redis import get_redis_connection
from redis import RedisError
from apps.users.models import User
import logging
import re
from magic.settings import REGEX_MOBILE
logger = logging.getLogger('magic')


class CheckAccessTokenForSMSSerializer(serializers.Serializer):

    access_token = serializers.CharField(label='发送短信的临时票据access_token', required=True, allow_null=False)

    def validate(self,attrs):
        # 获取发送短信的凭证 access_token，并校验
        access_token = attrs["access_token"]
        print(access_token)

        # 从user.User模型中调用验证access_token的方法
        mobile = User.check_sms_code_token(access_token)
        if not mobile:
            raise serializers.ValidationError("无效或错误的access_token")

        # 判断60s内是否发送过短信
        redis_conn = get_redis_connection("verify_codes")
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            raise serializers.ValidationError('请求次数过于频繁')

        self.mobile = mobile

        return attrs



class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, required=True, label="手机号码")

    def validate_mobile(self, mobile):
        """
        验证手机号码
        :param data:
        :return:
        """

        # 手机是否注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("手机号码已经存在")

        # 验证手机号码是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码非法")

        return mobile