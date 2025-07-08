from django.http import JsonResponse, HttpResponse
from .models import Product
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model
import json

User = get_user_model()

def home(request):
    return HttpResponse('<h2>欢迎使用智慧便利店无人收银系统</h2><p>请通过前端扫码或访问 API。</p>')

def product_list(request):
    barcode = request.GET.get('barcode')
    if barcode:
        products = list(Product.objects.filter(barcode=barcode).values())
    else:
        products = list(Product.objects.values())
    return JsonResponse({'products': products})

# 用户登录API
@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except Exception:
            return JsonResponse({'success': False, 'msg': '参数错误'}, status=400)
        user = authenticate(username=username, password=password)
        if user is not None:
            return JsonResponse({'success': True, 'msg': '登录成功', 'user': {
                'id': user.id,
                'username': user.username,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }})
        else:
            return JsonResponse({'success': False, 'msg': '用户名或密码错误'}, status=401)
    return JsonResponse({'success': False, 'msg': '仅支持POST'}, status=405)
