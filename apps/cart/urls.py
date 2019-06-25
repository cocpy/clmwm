from django.urls import path

from apps.cart import views

urlpatterns = [
    path('wm_start', views.WmStartView.as_view(), name='wm_start'),
    path('address/', views.save_address, name='address')
]
