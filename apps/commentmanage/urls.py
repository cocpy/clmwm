from django.urls import re_path

from apps.commentmanage.views import MessView

urlpatterns = [
    re_path(r'^mess/(?P<a_page>\d+)/(?P<b_page>\d+)/(?P<c_page>\d+)/$', MessView.as_view(), name='mess'),  # 商家留言管理
]
