from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied
from utils.response import api_response


def custom_exception_handler(exc, context):
    # 先调用 DRF 默认的处理器
    response = drf_exception_handler(exc, context)

    if response is not None:
        # DRF 已处理的异常，包装成统一格式
        message = response.data.get('detail') or '出错了'
        return api_response(code=response.status_code, message=message, data={})
    else:
        # 非 DRF 异常，返回通用错误
        return api_response(code=500, message='服务器内部错误', data={})
