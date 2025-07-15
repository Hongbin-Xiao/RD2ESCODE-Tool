from rest_framework.response import Response


def api_response(data=None, code=200, message='请求成功'):
    """
    构建统一响应结构
    """
    return Response({
        'code': code,
        'message': message,
        'data': data if data is not None else {}
    })


def api_error(message='fail', code=400, data=None):
    return api_response(code=code, message=message, data=data or {})


def api_success(message='success', code=200, data=None):
    return api_response(code=code, message=message, data=data or {})
