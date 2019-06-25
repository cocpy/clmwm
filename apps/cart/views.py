from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.http import JsonResponse

from apps.goods.models import GoodsSKU, Goods
from apps.user.models import Shop, User, Address
from utils.common import calculate_distance_duration, get_lng_lat

# Create your views here.


def save_address(request):
    """处理新增地址"""

    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return render(request, 'login.html', {'errmsg': '用户登录信息已失效，请重新登录！'})

    receiver = request.POST.get('receiver')
    addr_region = request.POST.get('region')
    addr_factor = request.POST.get('addr')
    phone = request.POST.get('phone')
    default = request.POST.get('default')

    # 校验数据
    if not all([addr_region, default, receiver, phone, addr_factor]):
        # 缺少相关数据
        return JsonResponse({'res': 1, 'errmsg': '缺少相关数据'})

    # 整合地址数据
    addr = addr_region + addr_factor

    if int(default) > 0:
        default = True
        # 查询出默认地址，设为非默认状态
        address_user = Address.objects.get(is_default=True, user=user)
        address_user.is_default = False
        address_user.save()
    else:
        default = False

    # 调用方法，获取经纬度
    lat_lng = get_lng_lat(addr)
    lat = lat_lng['lat']
    lng = lat_lng['lng']

    # 地址表新增数据
    address = Address(user=user, receiver=receiver, addr=addr, phone=phone, is_default=default, lat=lat, lng=lng)
    address.save()

    return JsonResponse({'res': 2, 'errmsg': '保存成功'})


class WmStartView(View):
    """订单确认"""

    def get(self, request):

        # 接收数据
        array_id = request.GET.get('cm1').split(',')
        array_count = request.GET.get('cm2').split(',')

        if len(array_id) != len(array_count):
            return redirect(reverse('goods:wm_index'), {'errmsg': '数据错误'})

        sku_info = GoodsSKU.objects.filter(id__in=array_id)

        # 遍历出所有商品信息
        flag, total, total_goods = 0, 0, 0
        for sku in sku_info:
            sku.unite = array_count[flag]
            total_goods = total_goods + (sku.price + int(sku.pack)) * int(sku.unite)
            goods = Goods.objects.get(id=sku.goods_id)
            shop = Shop.objects.get(id=goods.shop_id)
            flag += 1

        # 判断店铺状态
        if not shop.business_do:
            return redirect(reverse('goods:index'))

        if request.user.id:
            print('该用户的id为：%s ' % request.user.id)
        else:
            return redirect(reverse('user:login'))

        user = User.objects.get(id=request.user.id)

        # 计算运费
        distance = calculate_distance_duration(shop, user)

        # 一共支付
        total = total_goods + int(distance.send_price)

        # 设置顺序
        address_info = Address.objects.order_by('-is_default').filter(user_id=request.user.id)

        # 整合数据
        context = {'sku_info': sku_info, 'total_goods': total_goods, 'total': total, 'shop': shop, 'user': user,
                   'address_info': address_info}

        return render(request, 'wm_plaorder.html', context)

    def post(self, request):
        pass
