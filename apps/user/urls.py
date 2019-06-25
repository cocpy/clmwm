from django.urls import path, re_path
from . import views
from apps.user.views import RegisterView, LoginView, LogoutView, ShopRegisterView, UserActivate

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # 用户注册
    path('sj_register/', ShopRegisterView.as_view(), name='sj_register'),  # 店铺注册
    path('login/', LoginView.as_view(), name='login'),  # 用户登录
    path('logout/', LogoutView.as_view(), name='logout'),  # 用户登出
    re_path(r'^activate/(?P<token>.*)$', UserActivate.as_view(), name='activate'),  # 用户激活
    re_path(r'^type_detail$', views.find_type, name='type_detail'),  # 详细类型
]
