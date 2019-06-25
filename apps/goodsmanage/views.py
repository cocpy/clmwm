from django.shortcuts import render, redirect, reverse
from django.views.generic import View

from apps.goods.models import GoodsType, GoodsSKU, Goods, GoodsImage
from apps.user.models import Shop
from utils.common import goods_item, page_item, shop_is_new

from utils.fdfs.storage import FastDFSStorage


class SjcpglView(View):
    """商家菜品管理"""

    def get(self, request, page):

        # 获取店铺信息
        try:
            df_shop = Shop.objects.get(user_id=request.user.id)
        except Shop.DoesNotExist:
            return render(request, 'login.html', {'errmsg': '用户登录信息已失效，请重新登录！'})

        # 获取店铺下的所有商品
        goods_sku_info = GoodsSKU.objects.filter(goods__shop_id=df_shop.id).order_by('-update_time')

        # 为商品添加图片
        goods_item(goods_sku_info)

        # 对数据进行分页
        context = page_item(goods_sku_info, page, 3)

        shop_is_new(df_shop)

        context['shop'] = df_shop

        return render(request, 'sj_cpgl.html', context)

    def post(self, request, page):
        """处理商品上架"""

        # 接收数据
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        pack = request.POST.get('pack')
        typ = request.POST.get('type')
        img = request.FILES.get('file')

        # 校验基本数据
        if not all([img, name, price, stock, pack, typ]):
            # 数据不完整
            return render(request, 'sj_cpgl.html', {'errmsg': '缺少相关数据'})

        # FDFS上传图片
        rec = FastDFSStorage().save(img.name, img)

        # 业务表添加数据

        try:
            df_shop = Shop.objects.get(user_id=request.user.id)
        except Shop.DoesNotExist:
            return render(request, 'login.html', {'errmsg': '用户登录信息已失效，请重新登录！'})

        df_goods = Goods(name=name, shop_id=df_shop.id)
        df_goods.save()

        # 确定是否为新增类型
        try:
            df_goods_type = GoodsType.objects.get(name=typ, shop_id=df_shop.id)
        except GoodsType.DoesNotExist:
            df_goods_type = GoodsType(name=typ, shop_id=df_shop.id)
            df_goods_type.save()

        df_goods_sku = GoodsSKU(goods=df_goods, type=df_goods_type, name=name, price=price,
                                unite='per', stock=stock, pack=pack)
        df_goods_sku.save()

        df_goods_image = GoodsImage(image=rec, sku_id=df_goods_sku.id)
        df_goods_image.save()

        return redirect(reverse('goodsmanage:sj_cpgl', kwargs={'page': 1}))
        # return render(request, 'sj_cpgl.html')


class SjcpglUpdateView(View):
    """商品修改"""

    def get(self, request, goods_id):
        """展示页面"""

        try:
            goods_sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goodsmanage:sj_cpgl'))

        # 获得商品图片
        goods_item(goods_sku)

        try:
            df_shop = Shop.objects.get(user_id=request.user.id)
        except Shop.DoesNotExist:
            return render(request, 'login.html', {'errmsg': '用户登录信息已失效，请重新登录！'})

        # 判断是否为新店
        shop_is_new(df_shop)

        return render(request, 'sj_cpgl_update.html', {'sku': goods_sku, 'shop': df_shop})

    def post(self, request, goods_id):
        """提交商品修改"""

        # 接收数据
        sku_id = goods_id
        file = request.POST.get('file')
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        pack = request.POST.get('pack')
        typ = request.POST.get('type')

        # 校验基本数据
        if not all([name, price, stock, pack, typ]):
            # 数据不完整
            return render(request, 'sj_cpgl.html', {'errmsg': '缺少相关数据'})

        try:
            df_shop = Shop.objects.get(user_id=request.user.id)
        except Shop.DoesNotExist:
            return render(request, 'login.html', {'errmsg': '用户登录信息已失效，请重新登录！'})

        # 若修改的是商品类型，需查看该类型是否已存在
        try:
            df_goods_type = GoodsType.objects.get(name=typ, shop_id=df_shop.id)
        except GoodsType.DoesNotExist:
            df_goods_type = GoodsType(name=typ, shop_id=df_shop.id)
            df_goods_type.save()

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return render(request, 'login.html', {'errmsg': '数据错误，请重新登录！'})

        # 暂未校验sku_id与该用户是否存在所属关系

        sku.name = name
        sku.price = price
        sku.stock = stock
        sku.pack = pack
        sku.type = df_goods_type
        sku.save()

        # 是否对商品图片进行了修改
        if file:
            good_image= GoodsImage.objects.get(sku_id=sku.id)
            # FDFS上传图片
            rec = FastDFSStorage().save(file.name, file)
            good_image.image = rec
            good_image.save()


        # return render(request, 'sj_cpgl.html', {'success': '菜品修改成功！'})
        return redirect(reverse('goodsmanage:sj_cpgl', kwargs={'page': 1}))

    def update_del(self, sku_id):
        """处理商品删除"""

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return render(self.request, 'login.html', {'errmsg': '数据错误，请重新登录！'})
        type = sku.type
        sku.delete()

        # 该商家该类型下最后一件商品删除时，该类型也应删除
        goods_type = GoodsSKU.objects.filter(type=type).count()
        if goods_type == 0:
            type.delete()

        return redirect(reverse('goodsmanage:sj_cpgl', kwargs={'page': 1}))
