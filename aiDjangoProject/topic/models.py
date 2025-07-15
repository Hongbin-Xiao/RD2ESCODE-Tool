from django.db import models

from user.models import SysUser

"""话题表：记录用户创建的所有对话话题"""
class Topic(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name='标题')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    # 关键：添加用户外键
    user = models.ForeignKey(SysUser, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        db_table = 'topic'
        verbose_name = '话题'
        verbose_name_plural = '话题'
    def __str__(self):
        return self.title