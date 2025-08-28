@echo off
echo 正在安装Node.js WebSocket客户端依赖...
echo.

REM 检查是否安装了Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Node.js，请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js版本:
node --version

echo.
echo 正在安装依赖包...
npm install

if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ✅ 安装完成！
echo.
echo 可用的命令:
echo   npm start     - 运行完整示例
echo   npm test      - 运行简单测试
echo   node test-websocket.js - 直接运行测试
echo.
pause
