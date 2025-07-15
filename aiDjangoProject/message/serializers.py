# topic/serializers.py
from rest_framework import serializers
from .models import  Message

from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()
    file_count = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ['id', 'topic', 'role', 'content', 'file1', 'file2', 'files', 'file_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'files', 'file_count']

    def get_files(self, obj):
        """返回所有文件的信息"""
        files = []
        if obj.file1:
            files.append({
                'field': 'file1',
                'name': obj.file1.name.split('/')[-1],  # 获取文件名
                'url': obj.file1.url,
                'size': obj.file1.size
            })
        if obj.file2:
            files.append({
                'field': 'file2',
                'name': obj.file2.name.split('/')[-1],
                'url': obj.file2.url,
                'size': obj.file2.size
            })
        return files

    def get_file_count(self, obj):
        """返回文件数量"""
        return sum([1 for f in [obj.file1, obj.file2] if f])

