import os
import sys
import webbrowser
import threading
import time
from app import app, init_db
from waitress import serve

def open_browser():
    time.sleep(2)  # 等待服务器启动
    webbrowser.open('http://127.0.0.1:5000')

def main():
    # 初始化数据库
    init_db()
    
    # 在打包模式下使用waitress服务器
    if getattr(sys, 'frozen', False):
        print("个人记账系统启动中...")
        print("服务器运行在: http://127.0.0.1:5000")
        print("正在打开浏览器...")
        
        # 在新线程中打开浏览器
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 使用waitress生产服务器
        serve(app, host='127.0.0.1', port=5000)
    else:
        # 开发模式
        app.run(debug=True, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()