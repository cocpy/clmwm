from django.shortcuts import render
from django.views.generic import View

from apps.user.models import Shop
from utils.common import shop_is_new, get_comment_confusion, good_rate


class MessView(View):
    """商家留言管理模块"""

    def get(self, request, a_page, b_page, c_page):
        """商家留言页面展示"""

        try:
            shop = Shop.objects.get(user_id=request.user.id)
        except Shop.DoesNotExist:
            return render(request, 'login.html', {'errmsg': '用户登录信息已失效，请重新登录！'})

        # 获取该店铺的好评
        order_info_a = get_comment_confusion(6, 11, shop, a_page)
        # 获取该店铺的中评
        order_info_b = get_comment_confusion(3, 6, shop, b_page)
        # 或取该店铺的差评
        order_info_c = get_comment_confusion(0, 3, shop, c_page)

        # 计算好评率
        rate = good_rate(shop)

        # 判断是否为新店
        shop_is_new(shop)

        context = {'shop': shop, 'rate': rate,
                   'order_info_a': order_info_a,
                   'order_info_b': order_info_b,
                   'order_info_c': order_info_c}

        return render(request, 'sj_mess.html', context)
