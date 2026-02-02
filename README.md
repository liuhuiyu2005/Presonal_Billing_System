# 个人记账系统

一个基于Python Flask的个人记账系统，支持收入支出记录、数据统计和可视化。

## 功能特点

- 📊 收入支出记录管理
- 📈 实时数据统计和图表展示
- 💾 SQLite数据库存储
- 🖥️ 现代化Web界面
- 📦 可打包为独立可执行文件

## 安装和运行

### 开发环境运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
python main.py
```

3. 打开浏览器访问：http://127.0.0.1:5000

### 打包为可执行文件

1. 安装PyInstaller：
```bash
pip install pyinstaller
```

2. 运行打包脚本：
```bash
python build.py
```

3. 生成的可执行文件位于 `dist/PersonalBillingSystem.exe`

## 项目结构

```
Personal_Binlling_System/
├── app.py              # Flask应用主文件
├── main.py             # 应用启动文件
├── build.py            # 打包脚本
├── setup.py            # 安装配置
├── requirements.txt    # 依赖列表
├── templates/          # HTML模板
│   └── index.html
├── static/             # 静态文件
│   ├── styles.css
│   └── app.js
└── README.md
```

## 使用说明

1. **添加交易**：填写交易类型（收入/支出）、金额、类别、描述和日期
2. **查看统计**：顶部显示总收入、总支出和余额
3. **管理记录**：可以查看和删除所有交易记录
4. **数据持久化**：所有数据存储在SQLite数据库中

## 技术栈

- 后端：Python Flask
- 前端：HTML5 + CSS3 + JavaScript
- 数据库：SQLite3
- 打包工具：PyInstaller
- Web服务器：Waitress

## 许可证

MIT License