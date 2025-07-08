# 智慧便利店无人收银系统

## 项目简介
本项目为纯软件版智慧便利店无人收银系统，包含 PyQt 前端和 Django 后端，支持商品扫码、购物车、结算、订单管理等功能。

## 技术栈
- Python 3
- Django（后端 REST API，订单、商品、用户余额管理）
- PyQt5（前端桌面应用，购物车、结算、商品选择、余额管理等）
- SQLite（默认数据库）
- requests（前端与后端通信）

## 主要功能
- 商品管理：支持后台批量导入商品，商品包含名称、条形码、价格
- 购物车：前端可添加、删除、修改商品数量
- 商品选择：前端支持弹窗选择商品，无需扫码
- 结算下单：自动校验余额，余额不足时提示充值
- 用户余额管理：余额显示、充值、下单自动扣款，后台可管理用户余额
- 订单管理：支持订单明细、订单商品明细查看
- 用户登录：支持简单用户名密码登录

## 运行方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化数据库并导入商品数据
```bash
cd backend
python manage.py migrate
python manage.py loaddata product/fixtures/products.json
```

### 3. 启动后端 Django 服务
```bash
python manage.py runserver
```

### 4. 启动前端 PyQt 客户端
```bash
cd ../frontend
python main.py
```

### 5. 管理后台（可选）
浏览器访问 http://127.0.0.1:8000/admin/

## 说明
- 本系统为无人收银模拟，无需扫码枪，用户可直接通过“选择商品”弹窗添加商品。
- 支持余额充值、余额不足提示、订单自动扣款。
- 所有商品、订单、用户余额均可在 Django 后台管理。
