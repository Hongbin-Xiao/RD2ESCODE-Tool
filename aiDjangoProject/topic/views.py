# views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from utils.response import api_success, api_error
from .models import Topic
from .serializers import TopicSerializer
from utils import step


class TopicListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        topics = Topic.objects.filter(user=request.user).order_by('-created_at')
        serializer = TopicSerializer(topics, many=True)
        return api_success(data=serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id  # 绑定当前登录用户（SysUser）
        serializer = TopicSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return api_success(data=serializer.data)
        return api_error(code=400, message='参数错误')
