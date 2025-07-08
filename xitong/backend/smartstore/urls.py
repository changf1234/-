from django.contrib import admin
from django.urls import path, include

urlpatterns = [
## grappelli 路由已移除
    path('admin/', admin.site.urls),
path('api/', include('product.urls')),
path('api/', include('order.urls')),
]
