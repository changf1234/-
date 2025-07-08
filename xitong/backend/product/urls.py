from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 首页
    path('api/products/', views.product_list),
    path('api/login/', views.login_api),  # 登录API
]
