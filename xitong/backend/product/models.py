from django.db import models
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='商品名称')
    barcode = models.CharField(max_length=50, unique=True, verbose_name='条码')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'

    def __str__(self):
        return self.name
