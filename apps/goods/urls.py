from django.urls import path, re_path

from apps.goods import views

urlpatterns = [
    path('sj_index/', views.sj_index, name='sj_index'),  # 商家首页
    path('find', views.MySearchView(), name='haystack'),  # 全站检索
    re_path(r'^wm_index/(?P<code>[0-4])/(?P<page>\d+)/$', views.WmIndexView.as_view(), name='wm_index'),  # 店铺列表
    re_path(r'^goods/(?P<goods_id>\d+)/(?P<a_page>\d+)/(?P<b_page>\d+)/(?P<c_page>\d+)$',
        views.ShopDetailView.as_view(), name='shop_detail'),  # 店铺详情页
    path('', views.index, name='index')  # 买家首页
]
