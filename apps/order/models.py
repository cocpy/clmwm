from django.db import models
from db.base_model import BaseModel
# Create your models here.


class OrderInfo(BaseModel):
    """订单模型类"""

    PAY_METHOD_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付')
    )

    ORDER_STATUS_CHOICES = (
        (1, '订单待支付'),
        (2, '订单已支付'),
        (3, '商家已接单'),
        (4, '骑手取货中'),
        (5, '订单配送中'),
        (6, '订单已送达'),
        (7, '订单已评价')
    )

    order_id = models.CharField(max_length=128, primary_key=True, verbose_name='订单id')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='用户')
    addr = models.ForeignKey('user.Address', on_delete=models.CASCADE, verbose_name='地址')
    shop = models.ForeignKey('user.Shop', on_delete=models.CASCADE, verbose_name='店铺')
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=3, verbose_name='支付方式')
    total_count = models.IntegerField(default=1, verbose_name='商品数量')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')
    transit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单运费')
    transit_time = models.IntegerField(default=30, verbose_name='配送时间')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单状态')
    trade_no = models.CharField(max_length=128, verbose_name='支付编号')
    comment = models.CharField(max_length=256, default='此用户未填写任何评价！', verbose_name='评论')
    invoice_head = models.CharField(max_length=256, verbose_name='发票抬头')
    taxpayer_number = models.CharField(max_length=22, verbose_name='纳税人识别号')
    remarks = models.CharField(max_length=256, verbose_name='订单备注')
    score = models.SmallIntegerField(default=10, verbose_name='订单综合评分')

    class Meta:
        db_table = 'df_order_info'
        verbose_name = '订单'
        verbose_name_plural = verbose_name


class OrderGoods(BaseModel):
    """订单商品模型类"""

    order = models.ForeignKey('OrderInfo', on_delete=models.CASCADE, verbose_name='订单')
    sku = models.ForeignKey('goods.GoodsSKU', on_delete=models.CASCADE, verbose_name='商品SKU')
    count = models.IntegerField(default=1, verbose_name='商品数目')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    comment = models.CharField(max_length=256, verbose_name='评论')

    class Meta:
        db_table = 'df_order_goods'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name


class OrderTrack(BaseModel):
    """订单轨迹表"""

    ORDER_STATUS_CHOICES = (
        (1, '订单待支付'),
        (2, '订单已支付'),
        (3, '商家已接单'),
        (4, '骑手取货中'),
        (5, '订单配送中'),
        (6, '订单已送达'),
        (7, '订单已评价')
    )

    order = models.ForeignKey('OrderInfo', on_delete=models.CASCADE, verbose_name='订单')
    status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单状态')

    class Meta:
        db_table = 'df_order_track'
        verbose_name = '订单轨迹'
        verbose_name_plural = verbose_name


class CommentImage(BaseModel):
    """订单评论图片模型类"""

    order = models.ForeignKey('OrderInfo', on_delete=models.CASCADE, verbose_name='订单')
    image = models.ImageField(upload_to='order_info', verbose_name='图片路径')

    class Meta:
        db_table = 'df_order_image'
        verbose_name = '订单评论图片'
        verbose_name_plural = verbose_name
