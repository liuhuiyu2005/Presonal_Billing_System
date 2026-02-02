import os
import PyInstaller.__main__
import shutil

def build_desktop_executable():
    # 清理之前的构建文件
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('PersonalBillingDesktop.spec'):
        os.remove('PersonalBillingDesktop.spec')
    
    # PyInstaller配置 - 桌面应用
    PyInstaller.__main__.run([
        'desktop_app.py',
        '--name=PersonalBillingDesktop',
        '--onefile',
        '--windowed',  # 无控制台窗口
        '--icon=NONE',  # 可以添加图标文件路径
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--clean',
        '--noconfirm'
    ])
    
    print("桌面应用打包完成！可执行文件位于 dist/PersonalBillingDesktop.exe")
    print("双击即可运行，无需浏览器！")

if __name__ == '__main__':
    build_desktop_executable()