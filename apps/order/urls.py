from django.urls import path

from apps.order.views import OrderGenerateView, OrderPayView, CheckPayView, OrderBuySuccessView, QueryOrderView, GoCommentView

urlpatterns = [
    path('generate/', OrderGenerateView.as_view(), name='generate'),
    path('pay/', OrderPayView.as_view(), name='pay'),
    path('check/', CheckPayView.as_view(), name='check'),
    path('success/<order_id>', OrderBuySuccessView.as_view(), name='success'),
    path('go_comment/<order_id>', GoCommentView.as_view(), name='go_comment'),
    path('query/<page>/', QueryOrderView.as_view(), name='query')
]
