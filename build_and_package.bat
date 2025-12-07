@echo off
chcp 65001 >nul
echo 正在构建和打包记忆卡牌游戏...
echo ================================

echo 正在安装依赖...
python install_dependencies.py
if %errorlevel% neq 0 (
    echo 错误：依赖安装失败！
    pause
    exit /b 1
)

echo 正在构建可执行文件...
python package_app.py
if %errorlevel% neq 0 (
    echo 错误：打包失败！
    pause
    exit /b 1
)

echo ================================
echo 构建和打包完成！
echo 可执行文件位于 distribution 文件夹中
echo ================================

echo 打开输出目录...
start "" "%~dp0distribution"

pause