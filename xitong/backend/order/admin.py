from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price')
    search_fields = ('user__username',)
    list_filter = ('created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')




# 设置站点标题和头部
admin.site.site_header = '智慧便利店无人收银系统后台管理'
admin.site.site_title = '智慧便利店无人收银系统后台管理'
admin.site.index_title = '站点管理'


