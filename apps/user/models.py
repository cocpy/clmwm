from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel
# Create your models here.


class User(AbstractUser, BaseModel):
    """用户模型类"""

    sex = models.CharField(max_length=2, verbose_name='性别')
    phone = models.CharField(max_length=20, verbose_name='手机号码')
    image = models.ImageField(upload_to='user', verbose_name='用户头像')
    real_name = models.CharField(max_length=20, verbose_name='真实姓名')

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.real_name


class Address(BaseModel):
    """地址模型类"""

    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='所属账户')
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')
    phone = models.CharField(max_length=20, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    lng = models.DecimalField(max_digits=10, decimal_places=6, verbose_name='经度')
    lat = models.DecimalField(max_digits=10, decimal_places=6, verbose_name='纬度')

    class Meta:
        db_table = 'df_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.addr


class Shop(BaseModel):
    """商家店铺模型类"""

    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='所属账户')
    shop_name = models.CharField(max_length=20, verbose_name='店铺名称')
    shop_addr = models.CharField(max_length=256, verbose_name='店铺地址')
    shop_type = models.CharField(max_length=256, verbose_name='店铺类型')
    type_detail = models.CharField(max_length=256, verbose_name='类型信息')
    shop_score = models.DecimalField(default=0, max_digits=10, decimal_places=1, verbose_name='店铺评分')
    shop_price = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='起送价格')
    shop_sale = models.IntegerField(default=0, verbose_name='店铺销量')
    shop_image = models.ImageField(upload_to='shop', verbose_name='店铺图片')
    receive_start = models.TimeField(verbose_name='接单时间开始')
    receive_end = models.TimeField(verbose_name='接单时间结束')
    business_do = models.BooleanField(default=True, verbose_name='是否营业')
    high_opinion = models.CharField(max_length=20, verbose_name='好评度')

    def __str__(self):
        return self.shop_name

    class Meta:
        db_table = 'df_shop'
        verbose_name = '店铺'
        verbose_name_plural = verbose_name


class UserImage(BaseModel):
    """用户图片模型类"""

    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='所属账户')
    image = models.ImageField(upload_to='user', verbose_name='图片路径')

    class Meta:
        db_table = 'df_user_image'
        verbose_name = '用户图片'
        verbose_name_plural = verbose_name


class ShopImage(BaseModel):
    """店铺图片模型类"""

    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, verbose_name='店铺')
    image = models.ImageField(upload_to='shop', verbose_name='图片路径')

    class Meta:
        db_table = 'df_shop_image'
        verbose_name = '店铺图片'
        verbose_name_plural = verbose_name


class ShopTypeDetail(BaseModel):
    """店铺类型详细信息"""

    type_code = models.CharField(max_length=256, verbose_name='类型编码')
    type_name = models.CharField(max_length=256, verbose_name='类型名称')

    class Meta:
        db_table = 'df_shop_type'
        verbose_name = '店铺类型'
        verbose_name_plural = verbose_name

