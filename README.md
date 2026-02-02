# 个人记账系统 - 桌面版

一个基于PyQt5的个人记账桌面应用程序，支持收入支出记录、数据统计和管理。

## 功能特点

- 📊 收入支出记录管理
- 📈 实时数据统计和图表展示
- 💾 SQLite数据库存储
- 🖥️ 原生Windows桌面界面
- 📦 单文件可执行程序

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
└── README.md              # 说明文档
```

## 核心功能

1. **财务概览**：实时显示总收入、总支出和余额
2. **添加交易**：支持收入/支出记录，包含金额、类别、描述、日期
3. **交易管理**：查看所有记录，支持删除操作
4. **数据持久化**：使用SQLite数据库存储

## 技术栈

- 界面框架：PyQt5
- 数据库：SQLite3
- 打包工具：PyInstaller
- 兼容性：Windows 7/10/11

## 许可证

MIT License