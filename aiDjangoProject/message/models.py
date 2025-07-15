from django.db import models
from django.conf import settings
from topic.models import Topic


class Message(models.Model):
    ROLE_CHOICES = (
        ('user', '用户'),
        ('assistant', 'AI助手'),
        ('system', '系统提示'),
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField(blank=True, null=True)
    file1 = models.FileField(upload_to='uploads/messages/', blank=True, null=True, verbose_name='文件1')
    file2 = models.FileField(upload_to='uploads/messages/', blank=True, null=True, verbose_name='文件2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        db_table = 'message'
        verbose_name = '消息表'

    def __str__(self):
        file_count = sum([1 for f in [self.file1, self.file2] if f])
        file_info = f" ({file_count}个文件)" if file_count > 0 else ""
        return f'{self.role}: {self.content[:30] or "📎 文件"}{file_info}'

    @property
    def files(self):
        """返回所有非空文件的列表"""
        return [f for f in [self.file1, self.file2] if f]

    @property
    def has_files(self):
        """检查是否有文件"""
        return bool(self.file1 or self.file2)
