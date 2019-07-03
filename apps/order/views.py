import os
import datetime

from django.shortcuts import render, redirect, HttpResponse, reverse
from django.views.generic import View
from django.db import transaction
from django.conf import settings
from django.http import JsonResponse

from apps.user.models import Shop, User
from apps.goods.models import GoodsSKU, Goods
from apps.order.models import OrderInfo, OrderGoods, OrderTrack
from utils.common import calculate_distance_duration, page_item

# from alipay.aop.api.AlipayClientConfig import AlipayClientConfig  # 客户端配置类
# from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient  # 默认客户端类
# from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel  # 网站支付数据模型类
# from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest  # 网站支付请求类

from alipay import AliPay

# Create your views here.


class OrderGenerateView(View):
    """处理订单生成"""

    def get(self, request):
        pass

    @transaction.atomic
    def post(self, request):

        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return render(request, 'login.html', {'errmsg': '用户登录信息已失效，请重新登录！'})

        # 接收数据
        sku_str = request.POST.get('sku_ids')[1:]
        addr = request.POST.get('address')
        remarks = request.POST.get('remarks')
        invoice_head = request.POST.get('invoice_head')
        taxpayer_number = request.POST.get('taxpayer_number')

        try:
            sku_ids = sku_str[4:sku_str.find('cm2=') - 1].split('%2C')
            sku_counts = sku_str[sku_str.find('cm2=') + 4:].split('%2C')
            sku_info = GoodsSKU.objects.filter(id__in=sku_ids)
            for index, sku in enumerate(sku_info):
                goods = Goods.objects.get(id=sku.goods_id)
                shop = Shop.objects.get(id=goods.shop_id)
        except Exception:
            return redirect(reverse('goods:wm_index'), {'errmsg': '数据错误'})

        # 校验基本数据
        if not all([sku_str, shop, addr, sku_ids, sku_counts, sku_info]):
            # 数据不完整
            return render(request, 'sj_cpgl.html', {'errmsg': '缺少相关数据'})

        # 订单id: 20200802181630+用户id
        order_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(request.user.id)

        total_price, total_count, range_flag = 0, 0, 0

        # 设置事务保存点
        save_id = transaction.savepoint()
        try:

            # 重新计算运费
            distance = calculate_distance_duration(shop, user, address_id=addr)

            # 订单表添加数据
            order = OrderInfo.objects.create(order_id=order_id, user_id=request.user.id, addr_id=addr, shop=shop,
                                             remarks=remarks, invoice_head=invoice_head, total_price=0, total_count=0,
                                             taxpayer_number=taxpayer_number, transit_price=distance.send_price,
                                             transit_time=distance.duration)
            # 订单轨迹表添加一条数据
            order_track = OrderTrack.objects.create(order=order, status=1)

            # 乐观锁尝试3次
            for i in range(3):

                if range_flag:
                    break

                # 生成订单明细
                for index, item in enumerate(sku_info):

                    # 判断商品库存
                    if int(item.stock) < int(sku_counts[index]):
                        return HttpResponse('商品库存不足')

                    # 插入数据
                    order_goods = OrderGoods.objects.create(order=order, sku=item, price=item.price,
                                                            count=sku_counts[index])
                    # 更新库存，返回受影响的行数
                    stock = item.stock - int(sku_counts[index])
                    res = GoodsSKU.objects.filter(id=item.id, stock=item.stock).update(
                        stock=stock, sales=item.sales+int(sku_counts[index]))

                    if res == 0:
                        if i == 2:
                            # 尝试的第3次
                            transaction.savepoint_rollback(save_id)
                            return HttpResponse('下单失败')
                        continue

                    # 累加计算订单商品的总数量和总价格
                    total_price += (item.price + int(item.pack)) * int(sku_counts[index])
                    total_count += int(sku_counts[index])

                    a = len(sku_info)
                    if index == len(sku_info)-1:
                        range_flag = 1

            # 更新订单信息表中的商品的总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()

        except Exception as e:
            transaction.savepoint_rollback(save_id)
            # return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        # 提交事务
        transaction.savepoint_commit(save_id)

        total_all = int(order.transit_price) + total_price

        return render(request, 'wm_pay.html', {'order': order, 'shop': shop, 'total_all': total_all})


class OrderPayView(View):
    """订单支付"""

    def ali_native(self, request):
        """
        调用阿里原生接口，需要C++环境支持，
        pip install alipay-sdk-python
        使用时，需取消上方第四部分注释，安装对应版本的编译环境
        订单支付
        """

        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})

        # 校验店铺是否营业
        if not order.shop.business_do:
            return JsonResponse({'res': 4, 'errmsg': '店铺已休息'})

        # 业务处理:调用支付宝的支付接口
        alipay_client_config = AlipayClientConfig()  # 创建配置对象
        alipay_client_config.server_url = settings.ALIPAY_URL  # 网关
        alipay_client_config.app_id = settings.ALIPAY_APPID  # APPID
        alipay_client_config.app_private_key = settings.APP_PRIVATE_KEY  # 应用私钥

        client = DefaultAlipayClient(alipay_client_config=alipay_client_config)  # 使用配置创建客户端

        model = AlipayTradePagePayModel()  # 创建网站支付模型
        model.out_trade_no = order_id  # 商户订单号码
        model.total_amount = int(order.total_price+order.transit_price)  # 支付总额
        model.subject = '吃了么外卖%s' % order_id  # 订单标题
        model.body = '吃了么外卖订单'  # 订单描述
        model.product_code = 'FAST_INSTANT_TRADE_PAY'  # 与支付宝签约的产品码名称，目前只支持这一种。
        model.timeout_express = '15m'  # 订单过期关闭时长（分钟）
        pay_request = AlipayTradePagePayRequest(biz_model=model)  # 通过模型创建请求对象
        # pay_request.notify_url = settings.ALIPAY_NOTIFY_URL  # 设置回调通知地址
        pay_request.return_url = None
        pay_request.notify_url = None

        response = client.page_execute(pay_request, http_method='GET')  # 获取支付链接

        return JsonResponse({'res': 3, 'pay_url': response})

    def post(self, request):
        """
        调用封装好的接口，
        pip install python-alipay-sdk
        订单支付
        """

        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})

        # 校验店铺是否营业
        if not order.shop.business_do:
            return JsonResponse({'res': 4, 'errmsg': '店铺已休息'})

        # 业务处理:使用python sdk调用支付宝的支付接口
        # 初始化
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem'),
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem'), # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )

        # 调用支付接口
        # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        # total_pay = order.total_price+order.transit_price  # Decimal
        total_amount = int(order.total_price + order.transit_price)
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单id
            total_amount=str(total_amount),  # 支付总金额
            subject='吃了么外卖%s' % order_id,
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )

        # 返回应答
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'res': 3, 'pay_url': pay_url})


# ajax post /order/check/ data:订单id(order_id)
class CheckPayView(View):
    """查看订单支付的结果"""

    def post(self, request):
        """查询支付结果"""

        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})

        # 初始化
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )

        # 调用支付宝的交易查询接口
        while True:

            # 网络不好会导致接口调用失败
            response = alipay.api_alipay_trade_query(order_id)

            code = response.get('code')
            if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':

                # 支付成功,获取支付宝交易号
                trade_no = response.get('trade_no')

                # 更新订单状态
                order.trade_no = trade_no
                order.order_status = 2  # 待评价
                order.save()

                # 订单轨迹表生成新数据
                order_track = OrderTrack.objects.create(order=order, status=2)

                # 返回结果
                # return redirect(reverse('order:success', kwargs={'order_id': order_id}))
                return JsonResponse({'res': 3, 'message': '支付成功'})
            elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
                # 等待买家付款
                # 业务处理失败，可能一会就会成功
                import time
                time.sleep(5)
                continue
            else:
                # 支付出错
                return JsonResponse({'res': 4, 'errmsg': '支付失败'})


class OrderBuySuccessView(View):
    """支付成功，跳转详情页面"""

    def get(self, request, order_id, is_comment=False):

        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        try:
            order_info = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})

        order_goods = OrderGoods.objects.filter(order=order_info)
        pay_price = int(order_info.total_price) + int(order_info.transit_price)
        order_track = OrderTrack.objects.filter(order=order_info, status__gt=1)
        # 预计送达时间
        arrive_time = order_info.create_time + datetime.timedelta(minutes=order_info.transit_time)

        context = {'order': order_info, 'order_goods': order_goods, 'pay_price': pay_price, 'order_track': order_track, 'arrive_time': arrive_time}

        # 控制页面跳转
        if is_comment:
            return context
        else:
            return render(request, 'wm_ordertrack.html', context)


class QueryOrderView(View):
    """查询订单"""

    def get(self, request, page):
        """查询订单"""

        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
        # 进行中的订单
        order_going = OrderInfo.objects.filter(user=user, order_status__gte=2, order_status__lte=6)
        # 进行中的订单商品明细
        order_going_goods = OrderGoods.objects.filter(order__in=order_going)
        # 已完成的订单
        order_finish = OrderInfo.objects.filter(user=user, order_status__gte=7)
        # 已完成的订单商品明细
        order_finish_goods = OrderGoods.objects.filter(order__in=order_finish)
        # 分页处理
        order_going = page_item(order_going, page, 10)
        order_finish = page_item(order_finish, page, 10)
        order_going.update({'order_going_goods': order_going_goods})
        order_finish.update({'order_finish_goods': order_finish_goods})
        return render(self.request, 'wm_query_order.html', {'order_going': order_going, 'order_finish': order_finish})


class GoCommentView(View):

    def get(self, request, order_id):
        """跳转到评论页面"""

        context = OrderBuySuccessView.get(self, request, order_id, is_comment=True)
        return render(request, 'wm_buysuccess.html', context)
