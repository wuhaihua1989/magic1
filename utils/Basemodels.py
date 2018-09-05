from django.db import models


class BaseModel(models.Model):
    create_at = models.DateField(auto_now_add=True,verbose_name="创建时间")
    update_at= models.DateField(auto_now=True,verbose_name="更新时间")

    class Meta:
        abstract = True