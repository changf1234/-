from django.db import models
from product.models import Product
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='账户余额')

    class Meta:
        verbose_name = '用户余额'
        verbose_name_plural = '用户余额'

    def __str__(self):
        return f"{self.user.username} 余额: ￥{self.balance}"

class Order(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='下单用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='订单总价')

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'

    def __str__(self):
        return f'订单 {self.id}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='订单')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')

    class Meta:
        verbose_name = '订单商品'
        verbose_name_plural = '订单商品'

    def __str__(self):
        return f'{self.product} x {self.quantity}'
