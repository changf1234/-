from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .models import Order, OrderItem, UserProfile
from product.models import Product
from django.contrib.auth.models import User
import traceback
from decimal import Decimal, InvalidOperation

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            username = data.get('username')
            user = None
            if username:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = None
            total = Decimal('0.00')
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 1)
                try:
                    product = Product.objects.get(id=product_id)
                    price = Decimal(str(product.price)) * Decimal(str(quantity))
                    total += price
                except (Product.DoesNotExist, TypeError, ValueError):
                    continue
            # 新增：校验余额
            if user:
                profile, _ = UserProfile.objects.get_or_create(user=user)
                if profile.balance < total:
                    return JsonResponse({'error': '余额不足，请充值！', 'balance': float(profile.balance)}, status=402)
                profile.balance -= total
                profile.save()
            order = Order.objects.create(created_at=timezone.now(), total_price=total, user=user)
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 1)
                try:
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
                except Product.DoesNotExist:
                    continue
            order.save()
            return JsonResponse({'order_id': order.id, 'total': float(total)})
        except Exception as e:
            return JsonResponse({'error': f'服务器异常: {str(e)}', 'trace': traceback.format_exc()}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    data = []
    for order in orders:
        items = [
            {
                'product': item.product.name,
                'quantity': item.quantity,
                'price': float(item.price)
            } for item in order.items.all()
        ]
        data.append({
            'id': order.id,
            'created_at': order.created_at,
            'total_price': float(order.total_price),
            'items': items
        })
    return JsonResponse({'orders': data})

def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        items = [
            {
                'product': item.product.name,
                'quantity': item.quantity,
                'price': float(item.price)
            } for item in order.items.all()
        ]
        data = {
            'id': order.id,
            'created_at': order.created_at,
            'total_price': float(order.total_price),
            'items': items
        }
        return JsonResponse({'order': data})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

@csrf_exempt
def balance_view(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({'error': '缺少用户名'}, status=400)
    try:
        user = User.objects.get(username=username)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return JsonResponse({'balance': float(profile.balance)})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)

@csrf_exempt
def recharge_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            amount = data.get('amount')
            try:
                amount = Decimal(str(amount))
            except (TypeError, ValueError, InvalidOperation):
                return JsonResponse({'error': '充值金额无效'}, status=400)
            if not username or amount <= 0:
                return JsonResponse({'error': '参数错误'}, status=400)
            try:
                user = User.objects.get(username=username)
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.balance += amount
                profile.save()
                return JsonResponse({'balance': float(profile.balance)})
            except User.DoesNotExist:
                return JsonResponse({'error': '用户不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'服务器异常: {str(e)}', 'trace': traceback.format_exc()}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
