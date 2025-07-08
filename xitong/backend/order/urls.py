from django.urls import path
from . import views

urlpatterns = [
    path('api/orders/', views.order_list),
    path('api/orders/create/', views.create_order),
    path('api/orders/<int:order_id>/', views.order_detail),
    path('api/balance/', views.balance_view),
    path('api/recharge/', views.recharge_view),
]
