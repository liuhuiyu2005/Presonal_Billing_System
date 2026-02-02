import sys
import sqlite3
from datetime import datetime
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QDateEdit, QHeaderView, 
                             QFrame, QStackedWidget, QGridLayout, QScrollArea, QAbstractScrollArea)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QScrollArea

class BillingDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('billing_desktop.db')
        self.init_db()
    
    def init_db(self):
        c = self.conn.cursor()
        
        # 创建账户表
        c.execute('''CREATE TABLE IF NOT EXISTS accounts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      initial_balance REAL DEFAULT 0,
                      current_balance REAL DEFAULT 0,
                      icon TEXT DEFAULT '💳')''')
        
        # 创建交易表（添加账户关联）
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      amount REAL NOT NULL,
                      category TEXT NOT NULL,
                      description TEXT,
                      date TEXT NOT NULL,
                      type TEXT NOT NULL,
                      account_id INTEGER,
                      FOREIGN KEY (account_id) REFERENCES accounts (id))''')
        self.conn.commit()
    
    def add_transaction(self, amount, category, description, date, trans_type):
        c = self.conn.cursor()
        c.execute('INSERT INTO transactions (amount, category, description, date, type) VALUES (?, ?, ?, ?, ?)',
                  (amount, category, description, date, trans_type))
        self.conn.commit()
    
    def get_transactions(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM transactions ORDER BY date DESC')
        return c.fetchall()
    
    def delete_transaction(self, transaction_id):
        c = self.conn.cursor()
        c.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        self.conn.commit()
    
    # 账户管理方法
    def add_account(self, name, initial_balance):
        c = self.conn.cursor()
        
        # 根据账户名称自动设置图标
        icon = '💳'  # 默认图标
        if '支付宝' in name or 'alipay' in name.lower():
            icon = '📱'  # 支付宝图标
        elif '微信' in name or 'wechat' in name.lower() or '微信' in name:
            icon = '💬'  # 微信图标
        elif '现金' in name or 'cash' in name.lower():
            icon = '💵'  # 现金图标
        elif '银行卡' in name or 'card' in name.lower() or '银行' in name:
            icon = '💳'  # 银行卡图标
        
        c.execute('INSERT INTO accounts (name, initial_balance, current_balance, icon) VALUES (?, ?, ?, ?)',
                  (name, initial_balance, initial_balance, icon))
        self.conn.commit()
        return c.lastrowid
    
    def get_accounts(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM accounts ORDER BY id')
        return c.fetchall()
    
    def get_total_balance(self):
        c = self.conn.cursor()
        c.execute('SELECT SUM(current_balance) FROM accounts')
        return c.fetchone()[0] or 0
    
    def get_summary(self):
        c = self.conn.cursor()
        
        c.execute('SELECT SUM(amount) FROM transactions WHERE type = "收入"')
        total_income = c.fetchone()[0] or 0
        
        c.execute('SELECT SUM(amount) FROM transactions WHERE type = "支出"')
        total_expense = c.fetchone()[0] or 0
        
        total_balance = self.get_total_balance()
        
        return total_income, total_expense, total_balance
    
    def delete_account(self, account_id):
        # 删除账户
        with self.conn:
            c = self.conn.cursor()
            c.execute('DELETE FROM accounts WHERE id = ?', (account_id,))

class AddAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加账户")
        self.setModal(True)
        self.setFixedSize(300, 180)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 账户名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("账户名称:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("如：支付宝、微信钱包、现金等")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 初始余额
        balance_layout = QHBoxLayout()
        balance_layout.addWidget(QLabel("初始余额:"))
        self.balance_edit = QLineEdit()
        self.balance_edit.setPlaceholderText("请输入初始余额")
        self.balance_edit.setText("0.00")
        balance_layout.addWidget(self.balance_edit)
        layout.addLayout(balance_layout)
        
        # 确定按钮
        self.confirm_btn = QPushButton("确定")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                padding: 8px;
                border-radius: 15px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
            QPushButton:pressed {
                background-color: #004499;
            }
        """)
        self.confirm_btn.clicked.connect(self.confirm)
        layout.addWidget(self.confirm_btn)
        
        self.setLayout(layout)
    
    def confirm(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入账户名称")
            return
        
        try:
            balance = float(self.balance_edit.text())
        except ValueError:
            balance = 0.0
        
        self.accept()
    
    def get_account_data(self):
        name = self.name_edit.text().strip()
        try:
            balance = float(self.balance_edit.text())
        except ValueError:
            balance = 0.0
        return name, balance

class NavigationIcon(QWidget):
    clicked = pyqtSignal()
    
    def __init__(self, icon_name, label_text, is_active=False):
        super().__init__()
        self.icon_name = icon_name
        self.label_text = label_text
        self.is_active = is_active
        self.init_ui()
        
    def init_ui(self):
        import os
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(5)
        
        # 图标
        self.icon_label = QLabel()
        
        # 获取图标路径
        icon_path = os.path.join(os.path.dirname(__file__), "icons", f"{self.icon_name}.png")
        
        if os.path.exists(icon_path):
            from PyQt5.QtGui import QPixmap
            pixmap = QPixmap(icon_path)
            # 调整图片大小
            pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        else:
            # 如果图片不存在，使用默认文本
            self.icon_label.setText("🏠")
            self.icon_label.setFont(QFont("微软雅黑", 20))
        
        self.icon_label.setAlignment(Qt.AlignCenter)
        
        # 文字
        self.text_label = QLabel(self.label_text)
        self.text_label.setFont(QFont("微软雅黑", 10))
        self.text_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        
        self.setLayout(layout)
        self.setFixedHeight(80)
        self.update_style()
        
    def update_style(self):
        if self.is_active:
            self.setStyleSheet("""
                QWidget {
                    background-color: #007AFF;
                    border-radius: 10px;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    color: #666;
                }
                QWidget:hover {
                    background-color: #f0f0f0;
                    border-radius: 10px;
                }
            """)
    
    def set_active(self, active):
        self.is_active = active
        self.update_style()
    
    def mousePressEvent(self, event):
        self.clicked.emit()

class HomePage(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback
        self.init_ui()
    
    def init_ui(self):
        # 主垂直布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 总余额区域
        balance_layout = QVBoxLayout()
        balance_layout.setSpacing(5)
        
        # 总余额标题
        balance_title = QLabel("总余额")
        balance_title.setFont(QFont("微软雅黑", 16))
        balance_title.setAlignment(Qt.AlignCenter)
        balance_layout.addWidget(balance_title)
        
        # 总余额数字
        self.balance_label = QLabel("¥0.00")
        self.balance_label.setFont(QFont("微软雅黑", 36, QFont.Bold))
        self.balance_label.setAlignment(Qt.AlignCenter)
        self.balance_label.setStyleSheet("color: #7B68EE;")  # 紫色
        balance_layout.addWidget(self.balance_label)
        
        main_layout.addLayout(balance_layout)
        
        # 账户网格区域
        self.accounts_container = QWidget()
        self.accounts_layout = QGridLayout()
        self.accounts_layout.setSpacing(15)
        self.accounts_layout.setAlignment(Qt.AlignTop)
        
        self.accounts_container.setLayout(self.accounts_layout)
        main_layout.addWidget(self.accounts_container)
        
        # 添加账户按钮
        self.add_account_btn = QPushButton("添加账户")
        self.add_account_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                padding: 15px;
                border-radius: 10px;
                font-size: 14px;
                border: 2px dashed #ccc;
            }
            QPushButton:hover {
                border-color: #007AFF;
                color: #007AFF;
            }
        """)
        self.add_account_btn.clicked.connect(self.add_account)
        main_layout.addWidget(self.add_account_btn)
        
        self.setLayout(main_layout)
        self.refresh_data()
    
    def add_account(self):
        dialog = AddAccountDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, balance = dialog.get_account_data()
            if name:
                self.db.add_account(name, balance)
                QMessageBox.information(self, "成功", f"账户 {name} 添加成功！")
                self.refresh_data()
                self.refresh_callback()
            else:
                QMessageBox.warning(self, "警告", "请输入账户名称")
    
    def delete_account(self, account_id):
        # 显示确认对话框
        reply = QMessageBox.question(self, "确认删除", "确定要删除这个账户吗？", 
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 从数据库中删除账户
            self.db.delete_account(account_id)
            # 刷新数据
            self.refresh_data()
            self.refresh_callback()
    
    def on_account_clicked(self, account):
        # 账户点击事件 - 显示空弹窗
        QMessageBox.information(self, "账户详情", "")
    
    def get_icon_path(self, account_name):
        # 根据账户名称返回对应的图标路径
        icon_dir = os.path.join(os.path.dirname(__file__), "icons")
        
        if "微信" in account_name:
            return os.path.join(icon_dir, "wechat.png")
        elif "支付宝" in account_name:
            return os.path.join(icon_dir, "alipay.png")
        elif "现金" in account_name:
            return os.path.join(icon_dir, "cash.png")
        elif "银行卡" in account_name or "建行" in account_name:
            return os.path.join(icon_dir, "bank.png")
        else:
            return os.path.join(icon_dir, "default.png")
    
    def refresh_accounts(self):
        # 清空现有账户显示
        for i in reversed(range(self.accounts_layout.count())):
            widget = self.accounts_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 获取账户列表
        accounts = self.db.get_accounts()
        
        if accounts:
            # 显示账户网格
            row = 0
            col = 0
            
            for account in accounts:
                account_widget = self.create_account_widget(account)
                self.accounts_layout.addWidget(account_widget, row, col)
                
                # 每行两个账户
                col += 1
                if col >= 2:
                    col = 0
                    row += 1
    
    def create_account_widget(self, account):
        # 创建可点击的账户卡片
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                padding: 15px;
                border: 1px solid transparent;
                border-radius: 8px;
            }
            QWidget:hover {
                border-color: #007AFF;
            }
            QWidget QLabel {
                border: none;
            }
        """)
        
        # 添加点击事件
        widget.mousePressEvent = lambda event: self.on_account_clicked(account)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)  # 减小间距，让账户名字和余额更靠近
        layout.setAlignment(Qt.AlignTop)
        
        # 顶部：图标（居中）
        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignCenter)
        
        # 根据账户名称设置正确的图标
        account_name = account[1]
        icon_text = "💰"  # 默认图标
        
        if "微信" in account_name:
            icon_text = "💬"  # 微信图标
        elif "支付宝" in account_name:
            icon_text = "📱"  # 支付宝图标
        elif "现金" in account_name:
            icon_text = "💵"  # 现金图标
        elif "银行卡" in account_name or "建行" in account_name:
            icon_text = "💳"  # 银行卡图标
        
        # 图标 - 使用图片形式
        icon_path = self.get_icon_path(account_name)
        icon_label = QLabel()
        
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            # 调整图片大小
            pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            # 如果图片不存在，使用默认图标
            icon_label.setText("💰")
            icon_label.setFont(QFont("微软雅黑", 28))
        
        icon_layout.addWidget(icon_label)
        layout.addLayout(icon_layout)
        
        # 账户名称 - 居中
        name_label = QLabel(account[1])  # name字段
        name_label.setFont(QFont("微软雅黑", 12))
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # 余额 - 居中
        balance_label = QLabel(f"¥{account[3]:.2f}")  # current_balance字段
        balance_label.setFont(QFont("微软雅黑", 16, QFont.Bold))
        balance_label.setAlignment(Qt.AlignCenter)
        
        # 设置余额颜色
        if account[3] >= 0:
            balance_label.setStyleSheet("color: #1890ff;")  # 蓝色
        else:
            balance_label.setStyleSheet("color: #52c41a;")  # 绿色
        
        layout.addWidget(balance_label)
        
        widget.setLayout(layout)
        return widget
    
    def create_stat_card(self, icon, title, value):
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 图标
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("微软雅黑", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        
        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("微软雅黑", 12))
        title_label.setAlignment(Qt.AlignCenter)
        
        # 数值
        value_label = QLabel(value)
        value_label.setFont(QFont("微软雅黑", 16, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card
    
    def refresh_data(self):
        income, expense, balance = self.db.get_summary()
        
        # 更新总余额显示
        self.balance_label.setText(f"¥{balance:.2f}")
        
        # 刷新账户列表
        self.refresh_accounts()

class DetailsPage(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("交易详情")
        title.setFont(QFont("微软雅黑", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "类型", "金额", "类别", "描述", "日期", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.refresh_table()
        self.setLayout(layout)
    
    def refresh_table(self):
        transactions = self.db.get_transactions()
        self.table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            self.table.setItem(row, 0, QTableWidgetItem(str(trans[0])))
            self.table.setItem(row, 1, QTableWidgetItem(trans[5]))
            self.table.setItem(row, 2, QTableWidgetItem(f"¥{trans[1]:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(trans[2]))
            self.table.setItem(row, 4, QTableWidgetItem(trans[3] or ""))
            self.table.setItem(row, 5, QTableWidgetItem(trans[4]))
            
            # 删除按钮
            delete_btn = QPushButton("删除")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 4px;
                    border-radius: 8px;
                    border: none;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            delete_btn.clicked.connect(lambda checked, tid=trans[0]: self.delete_transaction(tid))
            self.table.setCellWidget(row, 6, delete_btn)
            
            # 设置颜色
            if trans[5] == "收入":
                self.table.item(row, 2).setForeground(Qt.darkGreen)
            else:
                self.table.item(row, 2).setForeground(Qt.darkRed)
    
    def delete_transaction(self, transaction_id):
        reply = QMessageBox.question(self, "确认删除", "确定要删除这条交易记录吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_transaction(transaction_id)
            self.refresh_table()
            self.refresh_callback()

class AddTransactionPage(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("添加交易")
        title.setFont(QFont("微软雅黑", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 表单
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        
        # 交易类型
        form_layout.addWidget(QLabel("类型:"), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["收入", "支出"])
        form_layout.addWidget(self.type_combo, 0, 1)
        
        # 金额
        form_layout.addWidget(QLabel("金额:"), 1, 0)
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("请输入金额")
        form_layout.addWidget(self.amount_edit, 1, 1)
        
        # 类别
        form_layout.addWidget(QLabel("类别:"), 2, 0)
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("如：工资、餐饮、交通等")
        form_layout.addWidget(self.category_edit, 2, 1)
        
        # 描述
        form_layout.addWidget(QLabel("描述:"), 3, 0)
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("可选描述信息")
        form_layout.addWidget(self.desc_edit, 3, 1)
        
        # 日期
        form_layout.addWidget(QLabel("日期:"), 4, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addWidget(self.date_edit, 4, 1)
        
        layout.addLayout(form_layout)
        
        # 添加按钮
        self.add_btn = QPushButton("添加交易")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                padding: 10px;
                border-radius: 15px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
            QPushButton:pressed {
                background-color: #004499;
            }
        """)
        self.add_btn.clicked.connect(self.add_transaction)
        layout.addWidget(self.add_btn)
        
        self.setLayout(layout)
    
    def add_transaction(self):
        try:
            amount = float(self.amount_edit.text())
            category = self.category_edit.text().strip()
            description = self.desc_edit.text().strip()
            date = self.date_edit.date().toString("yyyy-MM-dd")
            trans_type = self.type_combo.currentText()
            
            if not category:
                QMessageBox.warning(self, "警告", "请输入类别")
                return
            
            self.db.add_transaction(amount, category, description, date, trans_type)
            
            # 清空输入框
            self.amount_edit.clear()
            self.category_edit.clear()
            self.desc_edit.clear()
            
            QMessageBox.information(self, "成功", "交易添加成功！")
            self.refresh_callback()
            
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的金额")

class NavigationBar(QWidget):
    page_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_index = 0
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(0)
        
        # 创建三个导航图标
        self.home_icon = NavigationIcon("home", "首页", True)
        self.details_icon = NavigationIcon("details", "详情")
        self.add_icon = NavigationIcon("add", "记账")
        
        # 连接点击信号
        self.home_icon.clicked.connect(lambda: self.set_active_page(0))
        self.details_icon.clicked.connect(lambda: self.set_active_page(1))
        self.add_icon.clicked.connect(lambda: self.set_active_page(2))
        
        layout.addWidget(self.home_icon)
        layout.addWidget(self.details_icon)
        layout.addWidget(self.add_icon)
        
        self.setLayout(layout)
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #ddd;
            }
        """)
    
    def set_active_page(self, index):
        self.current_index = index
        
        # 更新图标状态
        self.home_icon.set_active(index == 0)
        self.details_icon.set_active(index == 1)
        self.add_icon.set_active(index == 2)
        
        # 发射页面切换信号
        self.page_changed.emit(index)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = BillingDatabase()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("个人记账系统")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 页面堆栈
        self.stacked_widget = QStackedWidget()
        
        # 创建三个页面
        self.home_page = HomePage(self.db, self.refresh_all)
        self.details_page = DetailsPage(self.db, self.refresh_all)
        self.add_page = AddTransactionPage(self.db, self.refresh_all)
        
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.details_page)
        self.stacked_widget.addWidget(self.add_page)
        
        # 导航栏
        self.nav_bar = NavigationBar()
        self.nav_bar.page_changed.connect(self.stacked_widget.setCurrentIndex)
        
        main_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(self.nav_bar)
        
        central_widget.setLayout(main_layout)
    
    def refresh_all(self):
        self.home_page.refresh_data()
        self.details_page.refresh_table()

def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()