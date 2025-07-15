from django.contrib.auth.models import AbstractUser
from django.db import models


class SysUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    avatar = models.CharField(max_length=255,
                              null=True,
                              verbose_name="用户头像")
    email = models.CharField(max_length=100,
                             null=True,
                             verbose_name="用户邮箱")
    phone = models.CharField(max_length=11,
                             null=True,
                             verbose_name="手机号码")
    login_date = models.DateField(null=True,
                                  verbose_name="最后登录时间")
    status = models.IntegerField(null=True,
                                 verbose_name="帐号状态（0正常1停用）")
    create_time = models.DateField(null=True,
                                   verbose_name="创建时间", )
    update_time = models.DateField(null=True,
                                   verbose_name="更新时间")
    remark = models.CharField(max_length=500,
                              null=True,
                              verbose_name="备注")
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'

    class Meta:
        db_table = "sys_user"
