from django.urls import path, re_path

from apps.ordermanage import views

urlpatterns = [
    re_path(r'^sj_order/(?P<page>\d+)/$', views.SjOrderView.as_view(), name='sj_order'),  # 商家订单管理
    path('receive/<order_status>/<order_id>', views.OrderReceive.as_view(), name='receive'),  # 商家接受或改变订单
    path('refuse/<order_id>', views.OrderRefuse.as_view(), name='refuse'),  # 商家拒绝订单
    path('status/', views.status, name='status'),  # 改变店铺状态
]
