import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QDateEdit, QHeaderView, QTabWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon

class BillingDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('billing_desktop.db')
        self.init_db()
    
    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      amount REAL NOT NULL,
                      category TEXT NOT NULL,
                      description TEXT,
                      date TEXT NOT NULL,
                      type TEXT NOT NULL)''')
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
    
    def get_summary(self):
        c = self.conn.cursor()
        
        c.execute('SELECT SUM(amount) FROM transactions WHERE type = "收入"')
        total_income = c.fetchone()[0] or 0
        
        c.execute('SELECT SUM(amount) FROM transactions WHERE type = "支出"')
        total_expense = c.fetchone()[0] or 0
        
        return total_income, total_expense, total_income - total_expense

class AddTransactionWidget(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("添加交易")
        title.setFont(QFont("微软雅黑", 14, QFont.Bold))
        layout.addWidget(title)
        
        # 交易类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["收入", "支出"])
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # 金额
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("金额:"))
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("请输入金额")
        amount_layout.addWidget(self.amount_edit)
        layout.addLayout(amount_layout)
        
        # 类别
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("类别:"))
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("如：工资、餐饮、交通等")
        category_layout.addWidget(self.category_edit)
        layout.addLayout(category_layout)
        
        # 描述
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("描述:"))
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("可选描述信息")
        desc_layout.addWidget(self.desc_edit)
        layout.addLayout(desc_layout)
        
        # 日期
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("日期:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)
        
        # 添加按钮
        self.add_btn = QPushButton("添加交易")
        self.add_btn.clicked.connect(self.add_transaction)
        self.add_btn.setStyleSheet("QPushButton { background-color: #007AFF; color: white; padding: 8px; border-radius: 4px; }")
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

class TransactionListWidget(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("交易记录")
        title.setFont(QFont("微软雅黑", 14, QFont.Bold))
        layout.addWidget(title)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
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
            delete_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; padding: 4px; border-radius: 3px; }")
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

class SummaryWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("财务概览")
        title.setFont(QFont("微软雅黑", 14, QFont.Bold))
        layout.addWidget(title)
        
        # 统计信息
        self.income_label = QLabel("总收入: ¥0.00")
        self.expense_label = QLabel("总支出: ¥0.00")
        self.balance_label = QLabel("余额: ¥0.00")
        
        for label in [self.income_label, self.expense_label, self.balance_label]:
            label.setFont(QFont("微软雅黑", 12))
            layout.addWidget(label)
        
        self.refresh_summary()
        self.setLayout(layout)
    
    def refresh_summary(self):
        income, expense, balance = self.db.get_summary()
        
        self.income_label.setText(f"总收入: ¥{income:.2f}")
        self.expense_label.setText(f"总支出: ¥{expense:.2f}")
        self.balance_label.setText(f"余额: ¥{balance:.2f}")
        
        # 设置颜色
        self.income_label.setStyleSheet("color: darkgreen;")
        self.expense_label.setStyleSheet("color: darkred;")
        if balance >= 0:
            self.balance_label.setStyleSheet("color: darkgreen; font-weight: bold;")
        else:
            self.balance_label.setStyleSheet("color: darkred; font-weight: bold;")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = BillingDatabase()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("个人记账系统")
        self.setGeometry(100, 100, 900, 600)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # 创建标签页
        self.tabs = QTabWidget()
        
        # 概览标签页
        self.summary_widget = SummaryWidget(self.db)
        self.tabs.addTab(self.summary_widget, "概览")
        
        # 添加交易标签页
        self.add_widget = AddTransactionWidget(self.db, self.refresh_all)
        self.tabs.addTab(self.add_widget, "添加交易")
        
        # 交易记录标签页
        self.list_widget = TransactionListWidget(self.db, self.refresh_all)
        self.tabs.addTab(self.list_widget, "交易记录")
        
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
        
        # 刷新所有数据
        self.refresh_all()
    
    def refresh_all(self):
        self.summary_widget.refresh_summary()
        self.list_widget.refresh_table()

def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()