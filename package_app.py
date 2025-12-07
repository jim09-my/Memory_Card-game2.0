import os
import sys
import subprocess
import shutil
from datetime import datetime

def create_distribution():
    """Create a distribution package for the Memory Card Game"""
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create distribution directory
    dist_name = f"MemoryCardGame_v{get_version()}"
    dist_dir = os.path.join(project_dir, "distribution", dist_name)
    os.makedirs(dist_dir, exist_ok=True)
    
    print(f"Creating distribution package: {dist_name}")
    
    # Build the executable
    build_executable()
    
    # Copy the executable to distribution folder
    exe_source = os.path.join(project_dir, "MemoryCardGame.exe")
    exe_dest = os.path.join(dist_dir, "MemoryCardGame.exe")
    
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, exe_dest)
        print(f"Copied executable to: {exe_dest}")
    else:
        print("ERROR: Executable not found!")
        return False
    
    # Copy documentation
    docs_to_copy = ["README.md", "游戏说明书.md", "LICENSE"]
    for doc in docs_to_copy:
        doc_source = os.path.join(project_dir, doc)
        doc_dest = os.path.join(dist_dir, doc)
        if os.path.exists(doc_source):
            shutil.copy2(doc_source, doc_dest)
            print(f"Copied documentation: {doc}")
    
    # Create a run.bat file for easy execution
    run_bat_content = """@echo off
cd /d "%~dp0"
MemoryCardGame.exe
pause
"""
    run_bat_path = os.path.join(dist_dir, "run.bat")
    with open(run_bat_path, 'w', encoding='utf-8') as f:
        f.write(run_bat_content)
    print(f"Created run.bat: {run_bat_path}")
    
    # Create a readme.txt for the distribution
    readme_content = f"""Memory Card Game v{get_version()}
========================

这是一个基于Python和Tkinter开发的记忆翻牌游戏。

运行方法：
1. 双击 run.bat 文件运行游戏
   或
2. 直接双击 MemoryCardGame.exe 文件运行游戏

系统要求：
- Windows 7 或更高版本
- 无需安装额外组件

游戏特性：
- 经典记忆翻牌游戏玩法
- 多种难度级别
- 计时挑战模式
- 成就系统
- 积分奖励机制
- 用户账户管理
- 商城系统
- 管理员功能

管理员登录：
- 在登录界面点击游戏Logo 5次进入管理员模式
- 或使用管理员账户登录（用户名：admin，密码：123456）

打包时间： {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    readme_path = os.path.join(dist_dir, "readme.txt")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"Created readme.txt: {readme_path}")
    
    print(f"\nDistribution package created successfully!")
    print(f"Location: {dist_dir}")
    return True

def get_version():
    """Get version from VERSION file"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(project_dir, "VERSION")
    
    if os.path.exists(version_file):
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return "1.0.0"

def build_executable():
    """Build the executable using PyInstaller"""
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # PyInstaller command with improved options
    cmd = [
        'pyinstaller',
        '--onefile',  # Single executable file
        '--windowed',  # No console window
        '--name', 'MemoryCardGame',  # Executable name
        '--icon', 'NONE',  # No icon for now
        '--add-data', 'assets;assets',  # Include assets folder
        '--add-data', 'data;data',  # Include data folder
        '--hidden-import', 'PIL._tkinter_finder',
        '--clean',  # Clean PyInstaller cache
        'main.py'
    ]
    
    print("Building executable...")
    print("Command:", ' '.join(cmd))
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Build successful!")
        
    except subprocess.CalledProcessError as e:
        print("Build failed!")
        print("Error:", e)
        print("Stdout:", e.stdout)
        print("Stderr:", e.stderr)
        raise
    except Exception as e:
        print("An error occurred:", e)
        raise

if __name__ == '__main__':
    try:
        create_distribution()
        print("\nPackage creation completed successfully!")
    except Exception as e:
        print(f"\nPackage creation failed: {e}")
        sys.exit(1)