"""clmwm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include(('apps.user.urls', 'apps.user'), namespace='user')),  # 用户模块
    path('cart/', include(('apps.cart.urls', 'apps.cart'), namespace='cart')),  # 购物车模块
    path('order/', include(('apps.order.urls', 'apps.order'), namespace='order')),  # 订单模块
    path('ordermanage/', include(('apps.ordermanage.urls', 'apps.ordermanage'), namespace='ordermanage')),  # 订单管理模块
    path('goodsmanage/', include(('apps.goodsmanage.urls', 'apps.goodsmanage'), namespace='goodsmanage')),  # 商品管理模块
    path('commentmanage/', include(('apps.commentmanage.urls', 'apps.commentmanage'), namespace='commentmanage')),  # 评论管理模块
    path('comment/', include(('apps.comment.urls', 'apps.comment'), namespace='comment')),  # 评论模块
    path('', include(('apps.goods.urls', 'apps.goods'), namespace='goods')),  # 商品模块,首页
]

# 仅在DEBUG模式下加载模块
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

