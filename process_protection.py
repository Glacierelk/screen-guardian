# -*- coding: utf-8 -*-
"""
进程保护模块
提供更强的进程保护功能，防止程序被恶意终止
"""

import os
import sys
import time
import threading
import subprocess
import psutil
from datetime import datetime

class ProcessProtection:
    def __init__(self, screen_guardian):
        self.screen_guardian = screen_guardian
        self.protection_active = True
        self.monitor_thread = None
        self.restart_attempts = 0
        self.max_restart_attempts = 3
        
    def start_protection(self):
        """启动进程保护"""
        try:
            # 设置进程优先级为高
            self._set_high_priority()
            
            # 启动监控线程
            self.monitor_thread = threading.Thread(target=self._protection_monitor, daemon=True)
            self.monitor_thread.start()
            
            # 创建守护进程（仅在非调试模式下）
            if not self._is_debug_mode():
                self._create_watchdog()
            
            print("进程保护已启动")
            
        except Exception as e:
            print(f"启动进程保护失败: {e}")
    
    def _set_high_priority(self):
        """设置进程为高优先级"""
        try:
            current_process = psutil.Process()
            if sys.platform == "win32":
                # Windows: 设置为高优先级
                current_process.nice(psutil.HIGH_PRIORITY_CLASS)
            else:
                # Unix系统: 设置为较高优先级
                current_process.nice(-10)
        except Exception as e:
            print(f"设置进程优先级失败: {e}")
    
    def _is_debug_mode(self):
        """检查是否在调试模式下运行"""
        return (
            hasattr(sys, 'gettrace') and sys.gettrace() is not None or
            'pydevd' in sys.modules or
            'pdb' in sys.modules or
            os.path.basename(sys.argv[0]).endswith('.py')
        )
    
    def _create_watchdog(self):
        """创建守护进程"""
        try:
            # 创建简单的守护脚本
            watchdog_script = f'''
import time
import psutil
import subprocess
import sys

target_pid = {os.getpid()}
target_exe = r"{sys.executable}"
target_script = r"{os.path.abspath(sys.argv[0])}"

while True:
    try:
        if not psutil.pid_exists(target_pid):
            print(f"检测到主进程 {{target_pid}} 已终止，尝试重启...")
            subprocess.Popen([target_exe, target_script], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
            break
        time.sleep(5)
    except Exception as e:
        print(f"守护进程监控异常: {{e}}")
        time.sleep(10)
'''
            
            # 保存守护脚本
            watchdog_file = "screen_guardian_watchdog.py"
            with open(watchdog_file, 'w', encoding='utf-8') as f:
                f.write(watchdog_script)
            
            # 启动守护进程
            if sys.platform == "win32":
                subprocess.Popen([sys.executable, watchdog_file], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen([sys.executable, watchdog_file], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
        except Exception as e:
            print(f"创建守护进程失败: {e}")
    
    def _protection_monitor(self):
        """进程保护监控"""
        current_pid = os.getpid()
        
        while self.protection_active:
            try:
                # 检查进程状态
                current_process = psutil.Process(current_pid)
                
                # 检查内存使用率，防止内存泄漏
                memory_percent = current_process.memory_percent()
                if memory_percent > 50:  # 如果内存使用超过50%，记录警告
                    print(f"警告：内存使用率较高 {memory_percent:.1f}%")
                
                # 检查CPU使用率
                cpu_percent = current_process.cpu_percent()
                if cpu_percent > 80:  # 如果CPU使用超过80%，记录警告
                    print(f"警告：CPU使用率较高 {cpu_percent:.1f}%")
                
                # 监控关键系统文件
                self._monitor_system_files()
                
                time.sleep(10)  # 每10秒检查一次
                
            except psutil.NoSuchProcess:
                print("主进程已终止")
                break
            except Exception as e:
                print(f"进程监控异常: {e}")
                time.sleep(30)
    
    def _monitor_system_files(self):
        """监控关键系统文件"""
        try:
            # 检查锁文件是否被删除
            if hasattr(self.screen_guardian, 'lock_file'):
                lock_file = self.screen_guardian.lock_file
                if not os.path.exists(lock_file):
                    print("检测到锁文件被删除，重新创建...")
                    try:
                        with open(lock_file, 'w') as f:
                            f.write(str(os.getpid()))
                    except Exception as e:
                        print(f"重新创建锁文件失败: {e}")
            
            # 检查配置文件
            config_file = self.screen_guardian.config_manager.config_file
            if not os.path.exists(config_file):
                print("检测到配置文件被删除，尝试恢复...")
                self.screen_guardian.config_manager.save_config()
                
        except Exception as e:
            print(f"系统文件监控异常: {e}")
    
    def handle_termination_request(self):
        """处理终止请求"""
        # 如果在休息状态，拒绝终止
        if (hasattr(self.screen_guardian, 'current_state') and 
            self.screen_guardian.current_state == 'resting'):
            print("休息时间中，拒绝终止请求")
            return False
        
        # 要求密码验证
        try:
            from password_dialog import show_password_dialog
            
            result = show_password_dialog(
                self.screen_guardian.config_manager,
                "进程保护",
                "检测到程序终止请求，请输入管理员密码确认："
            )
            
            if result:
                print("密码验证成功，允许终止")
                self.protection_active = False
                return True
            else:
                print("密码验证失败，拒绝终止")
                return False
                
        except Exception as e:
            print(f"密码验证过程出错: {e}")
            return False
    
    def stop_protection(self):
        """停止进程保护"""
        self.protection_active = False
        print("进程保护已停止")
    
    def log_protection_event(self, event_type, details=""):
        """记录保护事件"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {event_type}: {details}\n"
            
            # 写入日志文件
            with open("screen_guardian_protection.log", "a", encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"记录保护事件失败: {e}")
