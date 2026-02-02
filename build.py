import os
import PyInstaller.__main__
import shutil

def build_executable():
    # 清理之前的构建文件
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('PersonalBillingSystem.spec'):
        os.remove('PersonalBillingSystem.spec')
    
    # PyInstaller配置
    PyInstaller.__main__.run([
        'main.py',
        '--name=PersonalBillingSystem',
        '--onefile',
        '--windowed',
        '--add-data=templates;templates',
        '--add-data=static;static',
        '--hidden-import=waitress',
        '--hidden-import=flask',
        '--clean',
        '--noconfirm'
    ])
    
    print("构建完成！可执行文件位于 dist/PersonalBillingSystem.exe")

if __name__ == '__main__':
    build_executable()