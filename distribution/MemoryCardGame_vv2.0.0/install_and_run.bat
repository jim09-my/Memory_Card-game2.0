@echo off
chcp 65001 >nul
TITLE 记忆卡牌游戏安装程序

echo ========================================
echo    记忆卡牌游戏 v2.0.0 安装程序
echo ========================================

echo 正在检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Python环境！
    echo 请先安装Python 3.7或更高版本。
    pause
    exit /b 1
)

echo 正在安装游戏依赖...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告：依赖安装可能有问题，但将继续尝试运行游戏...
)

echo 正在启动游戏...
echo ========================================
echo 游戏即将开始，请稍候...
echo ========================================

python main.py

echo 游戏已退出。
pause