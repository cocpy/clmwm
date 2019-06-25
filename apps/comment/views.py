from collections import Iterable

from django.shortcuts import render, reverse, redirect
from django.db.models import Sum, Count, Avg

from apps.order.models import OrderInfo, CommentImage

from utils.fdfs.storage import FastDFSStorage
# Create your views here.


def new(request):
    """支付成功后，评价功能"""

    # 接收数据
    file = request.FILES.getlist('file')
    flavor = request.POST.get('flavor')
    package = request.POST.get('package')
    comment = request.POST.get('detail_comment')
    order_id = request.POST.get('order_id')

    # 校验数据
    if not order_id:
        return redirect(reverse('order:success', kwargs={'order_id': order_id}), {'errmsg': '无效的订单id'})

    if flavor and not int(flavor) in range(1, 6):
        return redirect(reverse('order:success', {'order_id': order_id}))

    if package and not int(package) in range(1, 6):
        return redirect(reverse('order:success', {'order_id': order_id}))

    try:
        order_info = OrderInfo.objects.get(order_id=order_id, user=request.user)
    except OrderInfo.DoesNotExist:
        return redirect(reverse('order:success', kwargs={'order_id': order_id}), {'errmsg': '订单不存在'})

    if order_info.order_status == 7:
        return redirect(reverse('order:success', kwargs={'order_id': order_id}), {'errmsg': '订单已评论'})

    # 业务处理
    order_info.comment = comment
    order_info.score = int(flavor) + int(package)
    order_info.order_status = 7
    order_info.save()

    # 重新计算店铺评分
    avg = OrderInfo.objects.filter(shop=order_info.shop).aggregate(Avg('score'))
    order_info.shop.shop_score = avg['score__avg']
    order_info.shop.save()

    # FDFS上传文件
    if isinstance(file, Iterable):
        for item in file:
            res = FastDFSStorage().save(item.name, item)
            CommentImage.objects.create(order=order_info, image=res)

    response = redirect(reverse('goods:index'))
    return response
