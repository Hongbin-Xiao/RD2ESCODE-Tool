import json

from django.template.defaultfilters import title
from django.views import View
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from twisted.web.html import output

from .models import Message
from .serializers import MessageSerializer
from utils.response import api_success, api_error
from utils import step
from pathlib import Path
from django.http import HttpResponse, FileResponse
from django.conf import settings
from django.utils.encoding import escape_uri_path


class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = MessageSerializer

    def get(self, request, topic_id):
        messages = Message.objects.filter(topic_id=topic_id)
        serializer = MessageSerializer(messages, many=True)
        return api_success(data=serializer.data)

    def post(self, request, topic_id):
        data = request.data.copy()
        data['topic'] = topic_id
        data['role'] = 'user'
        file1 = data.get('file1')
        file2 = data.get('file2')
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            message = serializer.save()
            file1 = message.file1.name
            file2 = message.file2.name
            if file1 and file2:
                file1_path = Path(settings.MEDIA_ROOT) / file1
                file2_path = Path(settings.MEDIA_ROOT) / file2
                step.start_async(file1_path, file2_path, topic_id=topic_id)
            else:
                step.ask_async(topic_id, data['content'])
            return api_success(data=serializer.data)
        return api_error(code=400, message='提交失败', data=serializer.errors)


class MessageDownloadView(APIView):
    """单独的文件下载视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            file_name = request.GET.get('fileName')
            if not file_name:
                return api_success(message="缺少文件名参数", code=400)

            # 构建文件路径
            file_path = Path(settings.MEDIA_ROOT) / 'compile' / file_name
            print(f"请求文件: {file_name}")
            print(f"完整路径: {file_path}")
            print(f"路径存在: {file_path.exists()}")

            if not file_path.exists():
                return api_success(message="文件不存在", code=401)

            # 获取文件信息
            file_stat = file_path.stat()
            print(f"文件大小: {file_stat.st_size} bytes")
            print(f"文件修改时间: {file_stat.st_mtime}")

            # 检查文件是否为空
            if file_stat.st_size == 0:
                return api_error("文件为空", 400)

            # 尝试读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content_preview = f.read(200)  # 读取前200个字符
                    print(f"文件内容预览: {repr(content_preview)}")
            except UnicodeDecodeError:
                print("文件包含二进制内容，无法预览")

            # 创建响应
            with open(file_path, 'rb') as f:
                file_content = f.read()

            response = HttpResponse(
                file_content,
                content_type='text/plain; charset=utf-8' if file_name.endswith('.c') else 'application/octet-stream'
            )

            # 设置下载头
            encoded_filename = escape_uri_path(file_name)
            response[
                'Content-Disposition'] = f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
            response['Content-Length'] = len(file_content)

            return response

        except Exception as e:
            print(f"下载异常详情: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return api_error(f"下载失败: {str(e)}", 500)


class JsonFileView(APIView):
    def get(self, request):
        # “初始代码生成"
        result = []
        chat_history_data = []
        chat_history = Path(settings.MEDIA_ROOT) / 'history' / 'chat_history.json'
        with open(chat_history, 'r', encoding='utf-8') as f:
            data = json.load(f)
            chat_history_data = data[3:]
            data = data[:2]
            data.append({"role": "file", "content": "initial_output.c"})
            think1 = {"messages": [
                {**item, "content": item["content"][:12]+ "..."} if item["role"] == "user" else item
                for item in data
            ], "title": "Initial code generation"}
            result.append(think1)
        compile_history = Path(settings.MEDIA_ROOT) / 'history' / 'compile_history.json'
        with open(compile_history, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data = data[2:]
            for idx, val in enumerate(data):
                if (idx+1) % 2 == 0:
                    val['role'] = 'ai1'
                else:
                    val['role'] = 'ai2'
            think2 = {"messages": data, "title": "Compilation correction"}
            result.append(think2)
        chat_history_reference = Path(settings.MEDIA_ROOT) / 'history' / 'chat_history_reference.json'
        with open(chat_history_reference, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for val in data:
                if val['role'] == 'assistant':
                    val['role'] = 'file'
                    val['content'] = 'modular.c,procedural.c,structural.c'
                elif val['role'] == 'user':
                    val['content'] = val['content'][:12]+ "..."
            think3 = {"messages": data, "title": "Reference code generation"}
            result.append(think3)
        chat_history_reference1 = Path(settings.MEDIA_ROOT) / 'history' / 'chat_history_reference1.json'
        with open(chat_history_reference1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data = data[3:]
            for idx, val in enumerate(data):
                if (idx+1) % 2 == 0:
                    val['role'] = 'ai1'
                else:
                    val['role'] = 'ai2'
            think4 = {"messages": data, "title": "Compilation correction - structured"}
            result.append(think4)
        chat_history_reference2 = Path(settings.MEDIA_ROOT) / 'history' / 'chat_history_reference2.json'
        with open(chat_history_reference2, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data = data[3:]
            for idx, val in enumerate(data):
                if (idx+1) % 2 == 0:
                    val['role'] = 'ai1'
                else:
                    val['role'] = 'ai2'
            think5 = {"messages": data, "title": "Compilation correction - modularized"}
            result.append(think5)
        chat_history_reference3 = Path(settings.MEDIA_ROOT) / 'history' / 'chat_history_reference3.json'
        with open(chat_history_reference3, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data = data[3:]
            for idx, val in enumerate(data):
                if (idx+1) % 2 == 0:
                    val['role'] = 'ai3'
                else:
                    val['role'] = 'ai2'
            think6 = {"messages": data, "title": "Compilation correction - procedural"}
            result.append(think6)
        chat_history_fix = Path(settings.MEDIA_ROOT) / 'history' / 'chat_history_fix.json'
        with open(chat_history_fix, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for val in data:
                if val['role'] == 'user':
                    val['role'] = 'ai3'
                    val['content'] = 'modular.c,procedural.c,structural.c'
                elif val['role'] == 'assistant':
                    val['role'] = 'ai4'
            think7 = {"messages": data, "title": "Check and provide correction suggestions"}
            result.append(think7)
        compile1_history = Path(settings.MEDIA_ROOT) / 'history' / 'compile1_history.json'
        with open(compile1_history, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data = data[3:]
            for idx, val in enumerate(data):
                if (idx+1) % 2 == 0:
                    val['role'] = 'ai1'
                else:
                    val['role'] = 'ai2'
            for val in chat_history_data:
                if val['role'] == 'user':
                    val['role'] = 'ai4'
                    val['content'] = val['content'][:50] + "..."
                elif val['role'] == 'assistant':
                    val['role'] = 'ai1'
                    val['content'] = val['content'][:50] + "..."
            think8 = {"messages": chat_history_data + data, "title": "修正代码"}
            result.append(think8)
        return api_success(data=result)
