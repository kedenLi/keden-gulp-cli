@echo off
echo 正在安装Python WebSocket客户端...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python版本:
python --version

echo.
echo 正在升级pip...
python -m pip install --upgrade pip

echo.
echo 正在安装websockets依赖...
python -m pip install websockets>=11.0.3

if %errorlevel% neq 0 (
    echo 错误: websockets安装失败
    pause
    exit /b 1
)

echo.
echo 正在安装其他依赖...
if exist requirements.txt (
    python -m pip install -r requirements.txt
) else (
    echo 未找到requirements.txt，跳过额外依赖安装
)

echo.
echo ✅ 安装完成！
echo.
echo 可用的命令:
echo   python test_websocket.py    - 运行简单测试
echo   python example.py           - 运行完整示例
echo   python setup.py             - 运行安装检查
echo.
echo 查看使用文档: README.md
echo.
pause
