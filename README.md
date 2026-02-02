# 个人记账系统 - 桌面版

一个基于PyQt5的个人记账桌面应用程序，支持收入支出记录、数据统计和管理。

## 功能特点

- 📊 收入支出记录管理
- 💳 账户管理（支持多个账户，每个账户有独立余额）
- 🔄 可点击的账户卡片（悬停显示边框提示）
- 💾 SQLite数据库存储
- 🖥️ 原生Windows桌面界面
- 📦 单文件可执行程序
- 🎨 统一的图片图标风格

## 使用方法

### 直接运行（推荐）

1. 双击 `dist/PersonalBillingDesktop.exe`
2. 应用程序会自动启动Windows窗口界面
3. 开始使用记账功能

### 开发环境运行

1. 安装依赖：
```bash
pip install PyQt5==5.15.10
```

2. 运行应用：
```bash
python desktop_app.py
```

### 重新打包

如果需要修改代码后重新打包：
```bash
python build_desktop.py
```

## 项目结构

```
Personal_Binlling_System/
├── desktop_app.py          # 桌面应用主文件
├── build_desktop.py        # 打包脚本
├── requirements.txt        # 依赖列表
├── .gitignore             # Git忽略文件
├── README.md              # 说明文档
└── icons/                 # 图标文件目录
    ├── add.png            # 记账按钮图标
    ├── alipay.png         # 支付宝账户图标
    ├── default.png        # 默认账户图标
    ├── details.png        # 详情按钮图标
    ├── home.png           # 首页按钮图标
    └── wechat.png         # 微信账户图标
```

## 核心功能

1. **财务概览**：实时显示总收入、总支出和余额
2. **账户管理**：支持添加多个账户，每个账户有独立余额和图标
3. **添加交易**：支持收入/支出记录，包含金额、类别、描述、日期
4. **交易管理**：查看所有记录，支持删除操作
5. **数据持久化**：使用SQLite数据库存储

## 技术栈

- 界面框架：PyQt5
- 数据库：SQLite3
- 打包工具：PyInstaller
- 兼容性：Windows 7/10/11

## 许可证

MIT License