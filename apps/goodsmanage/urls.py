from django.conf.urls import re_path

from apps.goodsmanage.views import SjcpglView, SjcpglUpdateView

urlpatterns = [
    re_path(r'^sj_cpgl/(?P<page>\d+)/$', SjcpglView.as_view(), name='sj_cpgl'),  # 商品管理
    re_path(r'^sj_cpgl_update/(?P<goods_id>(\d+))/$', SjcpglUpdateView.as_view(), name='sj_cpgl_update'),  # 商品修改
    re_path(r'^update_del/(?P<sku_id>(\d+))/$', SjcpglUpdateView.update_del, name='update_del'),  # 商品删除
]
