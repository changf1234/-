# Generated by Django 5.2.3 on 2025-06-22 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': '商品', 'verbose_name_plural': '商品'},
        ),
        migrations.AlterField(
            model_name='product',
            name='barcode',
            field=models.CharField(max_length=50, unique=True, verbose_name='条码'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=100, verbose_name='商品名称'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='价格'),
        ),
    ]
