# -*- coding: utf-8 -*-
"""
批处理文件编码修复脚本
修复现有发布包中的批处理文件编码问题
"""

import os
from pathlib import Path

def fix_batch_files():
    """修复批处理文件的编码问题"""
    print("🔧 修复批处理文件编码问题...")
    
    release_dir = Path("ScreenGuardian_Release_Windows")
    
    if not release_dir.exists():
        print("❌ 发布目录不存在，请先运行打包脚本")
        return False
    
    # 安装向导脚本
    install_script = """@echo off
chcp 65001 >nul
title ScreenGuardian 安装向导
echo.
echo =========================================
echo        ScreenGuardian 安装向导
echo =========================================
echo.
echo 欢迎使用 ScreenGuardian 电脑时间管理软件！
echo.
echo 安装选项：
echo 1. 仅运行程序（推荐）
echo 2. 创建桌面快捷方式
echo 3. 设置开机自启动
echo 4. 完整安装（快捷方式+自启动）
echo 5. 退出
echo.
set /p choice=请选择安装选项 (1-5): 

if "%choice%"=="1" goto RUN_ONLY
if "%choice%"=="2" goto DESKTOP_SHORTCUT
if "%choice%"=="3" goto AUTO_START
if "%choice%"=="4" goto FULL_INSTALL
if "%choice%"=="5" goto EXIT
goto INVALID

:RUN_ONLY
echo.
echo 正在启动 ScreenGuardian...
start "" "%~dp0ScreenGuardian.exe"
goto END

:DESKTOP_SHORTCUT
echo.
echo 正在创建桌面快捷方式...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\ScreenGuardian.lnk'); $Shortcut.TargetPath = '%~dp0ScreenGuardian.exe'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'ScreenGuardian 电脑时间管理'; $Shortcut.Save()"
echo 桌面快捷方式创建完成
start "" "%~dp0ScreenGuardian.exe"
goto END

:AUTO_START
echo.
echo 正在设置开机自启动...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\ScreenGuardian.lnk'); $Shortcut.TargetPath = '%~dp0ScreenGuardian.exe'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'ScreenGuardian 电脑时间管理'; $Shortcut.Save()"
echo 开机自启动设置完成
start "" "%~dp0ScreenGuardian.exe"
goto END

:FULL_INSTALL
echo.
echo 正在进行完整安装...
echo - 创建桌面快捷方式...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\ScreenGuardian.lnk'); $Shortcut.TargetPath = '%~dp0ScreenGuardian.exe'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'ScreenGuardian 电脑时间管理'; $Shortcut.Save()"
echo - 设置开机自启动...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\ScreenGuardian.lnk'); $Shortcut.TargetPath = '%~dp0ScreenGuardian.exe'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'ScreenGuardian 电脑时间管理'; $Shortcut.Save()"
echo 完整安装完成
start "" "%~dp0ScreenGuardian.exe"
goto END

:INVALID
echo 无效选择，请重新运行安装向导
goto END

:EXIT
echo 安装已取消
goto END

:END
echo.
echo 感谢使用 ScreenGuardian！
echo 如有问题请查看使用说明.txt
pause
"""

    # 管理员启动脚本
    admin_script = """@echo off
chcp 65001 >nul
title ScreenGuardian 启动器
echo.
echo =========================================
echo         ScreenGuardian 启动器
echo =========================================
echo.
echo 注意：此程序需要管理员权限才能正常工作
echo.

REM 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 管理员权限确认，启动程序...
    echo.
    start "" "%~dp0ScreenGuardian.exe"
    echo 程序已启动，请查看系统托盘
) else (
    echo 需要管理员权限，正在请求提升权限...
    echo.
    powershell -Command "Start-Process '%~dp0ScreenGuardian.exe' -Verb RunAs"
    echo 如果看到UAC提示，请点击"是"
)

echo.
echo 程序说明：
echo - 程序将在系统托盘中运行
echo - 右键托盘图标查看菜单
echo - 首次运行需要设置密码和时间
echo.
pause
"""

    # 快速测试脚本
    quick_test = """@echo off
chcp 65001 >nul
title ScreenGuardian 快速测试
echo.
echo =========================================
echo        ScreenGuardian 快速测试
echo =========================================
echo.
echo 此工具将启动 ScreenGuardian 进行快速功能测试
echo 建议首次使用时运行此测试
echo.
echo 测试内容：
echo - 程序启动测试
echo - 界面显示测试  
echo - 基本功能测试
echo.
set /p continue=继续测试吗？(Y/n): 

if /i "%continue%"=="n" goto END

echo.
echo 正在启动测试...
echo 1. 检查程序文件...
if not exist "ScreenGuardian.exe" (
    echo 找不到 ScreenGuardian.exe
    goto END
)
echo 程序文件正常

echo.
echo 2. 启动程序进行测试...
echo 注意：请设置较短的测试时间（如工作1分钟，休息30秒）
echo.
start "" "%~dp0ScreenGuardian.exe"

echo.
echo 3. 测试说明：
echo - 程序应该出现在系统托盘中
echo - 右键托盘图标测试菜单功能
echo - 设置短时间参数测试锁屏功能
echo - 新功能：休息时测试ESC键密码验证功能
echo - 新功能：测试暂停/恢复监控功能
echo - 新功能：尝试在任务管理器中结束进程（需要密码）
echo - 测试完成后可在托盘菜单中退出程序
echo.
echo 新功能测试要点：
echo 1. 休息锁屏时按ESC键，应该弹出密码输入框
echo 2. 托盘右键菜单的暂停/恢复功能应该正常工作
echo 3. 程序具有进程保护，强制结束需要密码验证
echo.
echo 测试启动完成
echo 请在系统托盘中查看程序图标

:END
pause
"""

    # 卸载工具脚本
    uninstall_script = """@echo off
chcp 65001 >nul
title ScreenGuardian 卸载工具
echo.
echo =========================================
echo        ScreenGuardian 卸载工具
echo =========================================
echo.
echo 警告：此操作将完全卸载 ScreenGuardian
echo 包括删除配置文件和快捷方式
echo.
set /p confirm=确认卸载吗？(y/N): 

if /i "%confirm%" neq "y" (
    echo 取消卸载
    goto END
)

echo.
echo 正在卸载 ScreenGuardian...

echo - 终止运行中的进程...
taskkill /F /IM ScreenGuardian.exe >nul 2>&1

echo - 删除桌面快捷方式...
if exist "%USERPROFILE%\\Desktop\\ScreenGuardian.lnk" del "%USERPROFILE%\\Desktop\\ScreenGuardian.lnk"

echo - 删除开机自启动...
if exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\ScreenGuardian.lnk" del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\ScreenGuardian.lnk"

echo - 清理临时文件...
if exist "screen_guardian.lock" del "screen_guardian.lock"

echo - 清理配置文件...
set /p keep_config=是否保留配置文件？(y/N): 
if /i "%keep_config%" neq "y" (
    if exist "screen_guardian_config.json" del "screen_guardian_config.json"
    echo   配置文件已删除
) else (
    echo   配置文件已保留
)

echo.
echo ✅ ScreenGuardian 卸载完成！
echo.
echo 感谢使用 ScreenGuardian
echo 如需重新安装，请运行安装向导.bat

:END
pause
"""

    # 保存修复后的文件
    files_to_fix = [
        ("安装向导.bat", install_script),
        ("以管理员身份运行.bat", admin_script),
        ("快速测试.bat", quick_test),
        ("卸载工具.bat", uninstall_script)
    ]
    
    for filename, content in files_to_fix:
        file_path = release_dir / filename
        try:
            # 使用GBK编码保存，这是Windows批处理文件的标准编码
            with open(file_path, 'w', encoding='gbk') as f:
                f.write(content)
            print(f"   ✅ 修复: {filename}")
        except Exception as e:
            print(f"   ❌ 修复失败: {filename} - {e}")
    
    print("✅ 批处理文件编码修复完成！")
    print("\n📋 修复的文件:")
    for filename, _ in files_to_fix:
        print(f"   - {filename}")
    
    print("\n💡 现在可以正常运行这些批处理文件，不会出现乱码。")
    return True

if __name__ == "__main__":
    fix_batch_files()
