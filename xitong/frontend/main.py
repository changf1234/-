import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QMessageBox, QInputDialog, QHBoxLayout, QDialogButtonBox, QDialog, QLabel, QLineEdit, QListWidgetItem, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QLocale
import requests

class ProductSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择商品")
        self.resize(500, 400)
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["商品名", "条形码", "价格"])
        layout.addWidget(self.table)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("添加")
        btns.button(QDialogButtonBox.Cancel).setText("取消")
        layout.addWidget(btns)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        self.selected_row = None
        self.table.cellDoubleClicked.connect(self.accept)
        self.table.cellClicked.connect(self.on_row_selected)

    def on_row_selected(self, row, col):
        self.selected_row = row

    def set_products(self, products):
        self.table.setRowCount(len(products))
        for i, p in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(p['name']))
            self.table.setItem(i, 1, QTableWidgetItem(str(p['barcode'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(p['price'])))
        self.selected_row = None

    def get_selected_product(self, products):
        row = self.selected_row if self.selected_row is not None else self.table.currentRow()
        if row >= 0 and row < len(products):
            return products[row]
        return None

class StoreApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智慧便利店无人收银系统")
        QLocale.setDefault(QLocale(QLocale.Chinese, QLocale.China))
        self.layout = QVBoxLayout()
        self.list_layout = QHBoxLayout()
        self.product_list = QListWidget()
        self.list_layout.addWidget(self.product_list)
        self.delete_btn = QPushButton("删除选中商品")
        self.delete_btn.clicked.connect(self.delete_selected_item)
        self.list_layout.addWidget(self.delete_btn)
        self.layout.addLayout(self.list_layout)
        self.scan_btn = QPushButton("扫码添加商品")
        self.scan_btn.clicked.connect(self.scan_product)
        self.layout.addWidget(self.scan_btn)
        self.checkout_btn = QPushButton("结算")
        self.checkout_btn.clicked.connect(self.checkout)
        self.layout.addWidget(self.checkout_btn)
        # 新增：余额显示和充值按钮
        self.balance_label = QLabel("余额：￥0.00")
        self.layout.addWidget(self.balance_label)
        self.recharge_btn = QPushButton("充值")
        self.recharge_btn.clicked.connect(self.show_recharge_dialog)
        self.layout.addWidget(self.recharge_btn)
        self.select_btn = QPushButton("选择商品")
        self.select_btn.clicked.connect(self.select_product_dialog)
        self.layout.addWidget(self.select_btn)
        self.setLayout(self.layout)
        self.cart = []
        self.setup_cart_actions()
        self.balance = 0.0

    def delete_selected_item(self):
        idx = self.product_list.currentRow()
        if idx >= 0:
            self.cart.pop(idx)
            self.refresh_cart()

    def scan_product(self):
        barcode, ok = self.input_dialog_cn("扫码", "请输入商品条码：")
        if ok and barcode:
            resp = requests.get(f"http://127.0.0.1:8000/api/products/?barcode={barcode}")
            if resp.status_code == 200 and resp.json().get('products'):
                product = resp.json()['products'][0]
                # 检查购物车中是否已存在该商品
                for item in self.cart:
                    if item['id'] == product['id']:
                        item['quantity'] = item.get('quantity', 1) + 1
                        self.refresh_cart()
                        return
                product['quantity'] = 1
                self.cart.append(product)
                self.refresh_cart()
            else:
                QMessageBox.warning(self, "提示", "未找到该商品")

    def input_dialog_cn(self, title, label):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)
        label_widget = QLabel(label)
        layout.addWidget(label_widget)
        line_edit = QLineEdit()
        layout.addWidget(line_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog.setLayout(layout)
        result = dialog.exec_()
        return line_edit.text(), result == QDialog.Accepted

    def refresh_cart(self):
        self.product_list.clear()
        for idx, p in enumerate(self.cart):
            item_text = f"{p['name']} x{p['quantity']} - ￥{float(p['price'])*p['quantity']}"
            item = QListWidgetItem(item_text)
            self.product_list.addItem(item)
            # 添加加减按钮
            add_btn = QPushButton("+")
            sub_btn = QPushButton("-")
            add_btn.setFixedWidth(30)
            sub_btn.setFixedWidth(30)
            def make_add(idx=idx):
                return lambda: self.change_quantity(idx, 1)
            def make_sub(idx=idx):
                return lambda: self.change_quantity(idx, -1)
            add_btn.clicked.connect(make_add(idx))
            sub_btn.clicked.connect(make_sub(idx))
            self.product_list.setItemWidget(item, self._cart_item_widget(item_text, add_btn, sub_btn))

    def _cart_item_widget(self, text, add_btn, sub_btn):
        w = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        label = QLabel(text)
        layout.addWidget(label)
        layout.addWidget(sub_btn)
        layout.addWidget(add_btn)
        w.setLayout(layout)
        return w

    def change_quantity(self, index, delta):
        if 0 <= index < len(self.cart):
            self.cart[index]['quantity'] += delta
            if self.cart[index]['quantity'] <= 0:
                self.cart.pop(index)
            self.refresh_cart()

    def setup_cart_actions(self):
        self.product_list.itemDoubleClicked.connect(self.modify_quantity_dialog)

    def modify_quantity_dialog(self, item):
        idx = self.product_list.currentRow()
        if idx < 0:
            return
        p = self.cart[idx]
        num, ok = QInputDialog.getInt(self, "修改数量", f"请输入[{p['name']}]的新数量：", value=p['quantity'], min=0)
        if ok:
            if num <= 0:
                self.cart.pop(idx)
            else:
                self.cart[idx]['quantity'] = num
            self.refresh_cart()

    def update_balance(self):
        # 登录后或充值后刷新余额
        try:
            resp = requests.get(f"http://127.0.0.1:8000/api/balance/?username={self.username}")
            if resp.status_code == 200:
                self.balance = float(resp.json().get('balance', 0))
                self.balance_label.setText(f"余额：￥{self.balance:.2f}")
            else:
                self.balance_label.setText("余额：获取失败")
        except Exception:
            self.balance_label.setText("余额：获取失败")

    def show_recharge_dialog(self):
        amount, ok = QInputDialog.getDouble(self, "充值", "请输入充值金额：", min=0.01, decimals=2)
        if ok and amount > 0:
            print(f"充值用户名: {self.username}, 金额: {amount}")  # 调试输出
            try:
                resp = requests.post("http://127.0.0.1:8000/api/recharge/", json={"username": self.username, "amount": amount})
                print(f"充值返回: {resp.status_code}, {resp.text}")  # 调试输出
                if resp.status_code == 200:
                    new_balance = resp.json().get('balance', 0)
                    QMessageBox.information(self, "充值成功", f"充值成功，当前余额：￥{new_balance:.2f}")
                    self.update_balance()
                else:
                    QMessageBox.warning(self, "充值失败", f"充值失败：{resp.text}")
            except Exception as e:
                QMessageBox.warning(self, "充值异常", f"请求异常：{e}")

    def submit_order(self):
        if not self.cart:
            QMessageBox.warning(self, "提示", "购物车为空！")
            return
        items = [
            {
                'product_id': int(p['id']),
                'quantity': p.get('quantity', 1)
            } for p in self.cart
        ]
        # 提交订单时带上用户名
        data = {'items': items, 'username': self.username}
        resp = requests.post("http://127.0.0.1:8000/api/orders/create/", json=data)
        print('订单API返回：', resp.status_code, resp.text)
        if resp.status_code == 200:
            order = resp.json()
            QMessageBox.information(self, "下单成功", f"订单已提交，总价：￥{order['total']:.2f}")
            self.cart.clear()
            self.product_list.clear()
            self.update_balance()
        elif resp.status_code == 402:
            msg = resp.json().get('error', '余额不足')
            balance = resp.json().get('balance', 0)
            ret = QMessageBox.question(self, "余额不足", f"{msg}\n当前余额：￥{balance:.2f}\n是否立即充值？", QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.Yes:
                self.show_recharge_dialog()
        else:
            QMessageBox.warning(self, "下单失败", f"订单提交失败，请重试！\n{resp.text}")

    def checkout(self):
        total = sum(float(p['price']) * p.get('quantity', 1) for p in self.cart)
        QMessageBox.information(self, "结算", f"总价：￥{total:.2f}")
        # 新增：结算后自动提交订单
        self.submit_order()

    def show_order_detail(self, order_id):
        resp = requests.get(f"http://127.0.0.1:8000/api/orders/{order_id}/")
        if resp.status_code == 200:
            data = resp.json()
            order = data.get('order') or data  # 兼容直接返回 order 或直接返回订单对象
            if not order:
                QMessageBox.warning(self, "订单详情", "订单数据异常")
                return
            detail = f"订单号: {order.get('id', '')}\n时间: {order.get('created_at', '')}\n总价: ￥{order.get('total_price', 0)}\n"
            for item in order.get('items', []):
                pname = item.get('product', '')
                qty = item.get('quantity', 1)
                price = item.get('price', 0)
                detail += f"{pname} x{qty} - ￥{price}\n"
            QMessageBox.information(self, "订单详情", detail)
        else:
            QMessageBox.warning(self, "订单详情", "未找到该订单")

    def show_login_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("用户登录")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("用户名："))
        username_edit = QLineEdit()
        layout.addWidget(username_edit)
        layout.addWidget(QLabel("密码："))
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("登录")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog.setLayout(layout)
        if dialog.exec_() == QDialog.Accepted:
            username = username_edit.text()
            password = password_edit.text()
            if not username or not password:
                QMessageBox.warning(self, "提示", "请输入用户名和密码！")
                return self.show_login_dialog()
            # 登录请求
            resp = requests.post("http://127.0.0.1:8000/api/login/", json={"username": username, "password": password})
            if resp.status_code == 200 and resp.json().get('success'):
                self.username = username
                self.userinfo = resp.json().get('user', {})
                QMessageBox.information(self, "登录成功", f"欢迎，{username}！")
                self.update_balance()
                return True
            else:
                QMessageBox.warning(self, "登录失败", "用户名或密码错误！")
                return self.show_login_dialog()
        else:
            sys.exit(0)

    def showEvent(self, event):
        if not hasattr(self, 'username'):
            self.show_login_dialog()
        super().showEvent(event)

    def select_product_dialog(self):
        try:
            resp = requests.get("http://127.0.0.1:8000/api/products/")
            if resp.status_code == 200 and resp.json().get('products'):
                products = resp.json()['products']
                dlg = ProductSelectDialog(self)
                dlg.set_products(products)
                if dlg.exec_() == QDialog.Accepted:
                    product = dlg.get_selected_product(products)
                    if product:
                        # 检查购物车中是否已存在该商品
                        for item in self.cart:
                            if item['id'] == product['id']:
                                item['quantity'] = item.get('quantity', 1) + 1
                                self.refresh_cart()
                                return
                        product['quantity'] = 1
                        self.cart.append(product)
                        self.refresh_cart()
            else:
                QMessageBox.warning(self, "提示", "获取商品列表失败")
        except Exception as e:
            QMessageBox.warning(self, "异常", f"请求异常：{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StoreApp()
    win.show()
    sys.exit(app.exec_())
