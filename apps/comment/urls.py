from django.urls import path

from apps.comment import views

urlpatterns = [
    path('order/', views.new, name='order'),  # 订单评论模块
]
