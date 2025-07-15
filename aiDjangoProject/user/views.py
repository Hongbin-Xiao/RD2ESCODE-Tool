from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from utils import test1_code_ge
from utils.response import api_success, api_error
from .serializers import UserRegisterSerializer, UserSerializer
from openai import OpenAI
from django.conf import settings
from pathlib import Path


class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            return api_success(data=serializer.data)
        return api_error()


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        # utils_dir = Path(settings.BASE_DIR) / 'utils'
        # write_path = os.path.join(settings.BASE_DIR, 'utils', 'C52_codes')
        # a1 = test1_code_ge.test1_with_compile_feedback(max_retry=1,parent_path=utils_dir)  #########初始生成
        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return api_success(data={
                'refreshToken': str(refresh),
                'accessToken': str(refresh.access_token),
                'userInfo': UserSerializer(user).data
            })
        return api_error(code=401, message='用户名或密码错误')
