from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import APIException, _get_error_details
from rest_framework import status

from django.utils.translation import ugettext_lazy as _


class ValidationError(APIException):
    """
    重写异常类
    """
    status_code = status.status = status.HTTP_200_OK
    default_detail = _('Invalid input.')
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        self.detail = _get_error_details(detail, code)


def validate_file_extension(value):
    """
    自定义校验文件上传的格式
    """
    if value.content_type != 'application/pdf':
        raise ValidationError({"status": 400, "message": '只能上传PDF文件'})

#
# def validate_image_extension(value):
#     import os
#
#     ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
#     valid_extensions = ['.jpg', '.png', '.jpeg', '.gif', 'bmp']
#     if not ext in valid_extensions:
#         print(111111111111111)
#         raise ValidationError({"status": 400, "message": '只能上传图片'})