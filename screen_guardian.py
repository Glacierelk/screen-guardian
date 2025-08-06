# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import threading
import time
import sys
import os
import signal
import atexit

from config_manager import ConfigManager
from parent_control import ParentControlPanel
from lock_screen import LockScreen
from tray_icon import TrayIcon
from process_protection import ProcessProtection

class ScreenGuardian:
    def __init__(self):
        # 首先检查多实例运行（必须在最开头）
        self.check_single_instance()
        
        # 设置进程保护
        self._setup_process_protection()
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 状态变量
        self.monitoring_active = True
        self.current_state = 'working'  # working, resting
        self.work_start_time = time.time()
        self.remaining_work_time = self.config_manager.get_work_duration()
        self.remaining_break_time = 0
        
        # 界面组件
        self.parent_control = ParentControlPanel(self.config_manager)
        self.tray_icon = None
        self.lock_screen = None
        
        # 进程保护
        self.process_protection = ProcessProtection(self)
        
        # 主循环控制
        self.running = True
        self.timer_thread = None
    
    def _setup_process_protection(self):
        """设置进程保护"""
        try:
            # 注册退出处理函数
            atexit.register(self._cleanup_on_exit)
            
            # 捕获终止信号
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
            
            # 在Windows上尝试捕获更多信号
            if sys.platform == "win32":
                try:
                    signal.signal(signal.SIGBREAK, self._signal_handler)
                except AttributeError:
                    pass  # SIGBREAK在某些Windows版本中可能不可用
            
            # 启动进程监控线程
            self._start_process_monitor()
            
        except Exception as e:
            print(f"设置进程保护失败: {e}")
    
    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        print(f"收到信号 {signum}，尝试保护进程...")
        
        # 使用进程保护模块处理终止请求
        if self.process_protection.handle_termination_request():
            self.quit_application()
        else:
            print("终止请求被拒绝")
    
    def _start_process_monitor(self):
        """启动进程监控"""
        def monitor():
            import psutil
            current_pid = os.getpid()
            
            while self.running:
                try:
                    # 检查进程是否还存在
                    if not psutil.pid_exists(current_pid):
                        break
                    
                    # 检查父进程状态
                    current_proc = psutil.Process(current_pid)
                    if not current_proc.is_running():
                        break
                    
                    time.sleep(5)  # 每5秒检查一次
                    
                except Exception as e:
                    print(f"进程监控异常: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def _cleanup_on_exit(self):
        """退出时的清理函数"""
        try:
            # 清理锁文件
            if hasattr(self, 'lock_file') and os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except:
            pass
        
    def check_single_instance(self):
        """检查是否已有实例在运行"""
        import psutil
        
        # 首先检查锁文件
        self.lock_file = 'screen_guardian.lock'
        
        # 检查锁文件是否存在
        if os.path.exists(self.lock_file):
            try:
                with open(self.lock_file, 'r') as f:
                    old_pid = int(f.read().strip())
                
                # 检查该PID的进程是否还在运行
                try:
                    old_proc = psutil.Process(old_pid)
                    if old_proc.is_running():
                        messagebox.showerror("错误", f"ScreenGuardian 已经在运行中！\nPID: {old_pid}\n请检查任务管理器或系统托盘。")
                        sys.exit(1)
                except psutil.NoSuchProcess:
                    # 进程不存在，删除过期的锁文件
                    os.remove(self.lock_file)
            except (ValueError, FileNotFoundError):
                # 锁文件格式错误或无法读取，删除它
                try:
                    os.remove(self.lock_file)
                except:
                    pass
        
        # 检查是否有其他ScreenGuardian进程在运行
        current_pid = os.getpid()
        current_name = os.path.basename(sys.argv[0])
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # 检查进程名
                proc_name = proc.info['name']
                
                if proc_name.lower() in ['screenguardian.exe', 'screen_guardian.exe']:
                    # 获取该进程的最终父进程PID
                    other_root_pid = self._get_root_process_pid(proc.info['pid'])
                    # 获取当前进程的最终父进程PID
                    current_root_pid = self._get_root_process_pid(current_pid)
                    
                    # 如果两个进程的根进程不同，说明是不同的ScreenGuardian实例
                    if other_root_pid != current_root_pid:
                        messagebox.showerror("错误", f"ScreenGuardian 已经在运行中！\n进程名: {proc_name}\nPID: {proc.info['pid']}\n请检查任务管理器或系统托盘。")
                        sys.exit(1)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # 创建锁文件
        try:
            with open(self.lock_file, 'w') as f:
                f.write(str(current_pid))
        except Exception as e:
            print(f"创建锁文件失败: {e}")
    
    def _get_root_process_pid(self, pid):
        """获取进程的最终父进程PID"""
        import psutil
        
        try:
            current_proc = psutil.Process(pid)
            root_pid = pid
            
            # 沿着父进程链向上查找，直到找到最终的父进程
            while True:
                try:
                    parent = current_proc.parent()
                    if parent is None:
                        break
                    
                    # 继续向上查找父进程
                    root_pid = parent.pid
                    current_proc = parent
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break
            
            return root_pid
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return pid
    
    def start(self):
        """启动应用程序"""
        print("ScreenGuardian 启动中...")
        
        # 启动进程保护
        self.process_protection.start_protection()
        
        # 如果是首次运行，显示设置界面
        if self.config_manager.is_first_run():
            print("首次运行，显示设置界面...")
            self.show_settings()
        
        # 启动托盘图标
        self.tray_icon = TrayIcon(self)
        self.tray_icon.start()
        
        # 启动监控定时器
        self.start_monitoring()
        
        # 保持主线程运行
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("检测到键盘中断...")
            if self.process_protection.handle_termination_request():
                self.quit_application()
        except Exception as e:
            print(f"主循环异常: {e}")
            self.quit_application()
        # 移除finally块，避免无条件退出
    
    def start_monitoring(self):
        """启动监控"""
        if self.timer_thread and self.timer_thread.is_alive():
            return
        
        try:
            self.timer_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.timer_thread.start()
            print("监控已启动")
        except Exception as e:
            print(f"启动监控失败: {e}")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.running:
            try:
                if not self.monitoring_active:
                    time.sleep(1)
                    continue
                    
                if self.current_state == 'working':
                    self._handle_working_state()
                elif self.current_state == 'resting':
                    self._handle_resting_state()
                    
                time.sleep(1)
            except Exception as e:
                print(f"监控循环异常: {e}")
                time.sleep(5)  # 异常后等待5秒再继续
    
    def _handle_working_state(self):
        """处理工作状态"""
        self.remaining_work_time -= 1
        
        # 更新托盘图标状态
        if self.remaining_work_time <= 300:  # 剩余5分钟时警告
            if self.tray_icon:
                self.tray_icon.update_icon('warning')
        
        # 工作时间结束，进入休息状态
        if self.remaining_work_time <= 0:
            self._start_break()
    
    def _handle_resting_state(self):
        """处理休息状态"""
        self.remaining_break_time -= 1
        
        # 休息时间结束
        if self.remaining_break_time <= 0:
            self._end_break()
    
    def _start_break(self):
        """开始休息"""
        print("开始休息时间")
        self.current_state = 'resting'
        self.remaining_break_time = self.config_manager.get_break_duration()
        
        # 更新托盘图标
        if self.tray_icon:
            self.tray_icon.update_icon('resting')
        
        # 在单独线程中显示锁屏，避免阻塞主监控循环
        try:
            lock_thread = threading.Thread(target=self._show_lock_screen, daemon=True)
            lock_thread.start()
        except Exception as e:
            print(f"启动锁屏线程失败: {e}")
            self._fallback_break_timer()
    
    def _show_lock_screen(self):
        """显示锁屏"""
        try:
            print(f"准备显示锁屏，剩余休息时间: {self.remaining_break_time}秒")
            
            # 创建锁屏实例
            self.lock_screen = LockScreen(
                self.remaining_break_time,
                self.config_manager,
                on_break_end=self._on_break_end_callback,
                on_early_exit=self._on_early_exit_callback
            )
            
            # 显示锁屏（会阻塞直到休息结束）
            self.lock_screen.show()
            
        except Exception as e:
            print(f"显示锁屏失败: {e}")
            import traceback
            traceback.print_exc()
            # 如果锁屏失败，启动备用计时器
            self._fallback_break_timer()
        finally:
            # 确保锁屏对象被清理
            self.lock_screen = None
    
    def _fallback_break_timer(self):
        """备用休息计时器"""
        print("使用备用计时器等待休息结束...")
        start_time = time.time()
        while time.time() - start_time < self.remaining_break_time and self.current_state == 'resting':
            time.sleep(1)
        if self.current_state == 'resting':
            self._on_break_end_callback()
    
    def _on_break_end_callback(self):
        """休息结束回调"""
        print("休息时间结束")
        self._end_break()
    
    def _on_early_exit_callback(self):
        """提前退出休息回调"""
        print("用户提前结束休息")
        self._end_break()
    
    def _end_break(self):
        """结束休息"""
        self.current_state = 'working'
        self.remaining_work_time = self.config_manager.get_work_duration()
        self.work_start_time = time.time()
        
        # 更新托盘图标
        if self.tray_icon:
            self.tray_icon.update_icon('working')
        
        print("重新开始工作计时")
    
    def show_settings(self):
        """显示设置界面"""
        def show_in_thread():
            try:
                self.parent_control.show_settings()
                if self.parent_control.root:
                    self.parent_control.root.mainloop()
            except Exception as e:
                print(f"显示设置界面失败: {e}")
        
        # 在单独线程中显示设置界面
        try:
            settings_thread = threading.Thread(target=show_in_thread, daemon=True)
            settings_thread.start()
        except Exception as e:
            print(f"启动设置界面线程失败: {e}")
    
    def get_status_info(self):
        """获取状态信息"""
        if self.current_state == 'working':
            minutes = self.remaining_work_time // 60
            seconds = self.remaining_work_time % 60
            return f"工作中 - 剩余时间: {minutes:02d}:{seconds:02d}"
        elif self.current_state == 'resting':
            minutes = self.remaining_break_time // 60
            seconds = self.remaining_break_time % 60
            return f"休息中 - 剩余时间: {minutes:02d}:{seconds:02d}"
        else:
            return "监控已暂停"
    
    def toggle_monitoring(self):
        """切换监控状态"""
        old_state = self.monitoring_active
        self.monitoring_active = not self.monitoring_active
        status = "恢复" if self.monitoring_active else "暂停"
        print(f"监控已{status}")
        
        # 如果从暂停恢复到监控状态，重置时间
        if not old_state and self.monitoring_active:
            if self.current_state == 'working':
                self.remaining_work_time = self.config_manager.get_work_duration()
                self.work_start_time = time.time()
            elif self.current_state == 'resting':
                # 如果在休息状态恢复监控，强制结束休息
                self._end_break()
        
        # 更新托盘图标
        if self.tray_icon:
            try:
                if self.monitoring_active:
                    self.tray_icon.update_icon('working' if self.current_state == 'working' else 'resting')
                else:
                    self.tray_icon.update_icon('orange')
                    
                # 延迟更新菜单以避免线程冲突
                def delayed_menu_update():
                    time.sleep(0.1)
                    self.tray_icon.update_menu()
                
                threading.Thread(target=delayed_menu_update, daemon=True).start()
                
            except Exception as e:
                print(f"更新托盘图标失败: {e}")
            # 更新菜单文本
            self.tray_icon.update_menu()
    
    def quit_application(self):
        """退出应用程序"""
        print("正在退出 ScreenGuardian...")
        self.running = False
        
        # 停止进程保护
        if hasattr(self, 'process_protection'):
            self.process_protection.stop_protection()
        
        # 停止托盘图标
        if self.tray_icon:
            self.tray_icon.stop()
        
        # 关闭设置界面
        if self.parent_control and hasattr(self.parent_control, 'root') and self.parent_control.root:
            try:
                self.parent_control.root.quit()
                self.parent_control.root.destroy()
            except:
                pass
        
        # 关闭锁屏
        if self.lock_screen and hasattr(self.lock_screen, 'root'):
            try:
                self.lock_screen.unlock_screen()
            except:
                pass
        
        # 清理锁文件
        try:
            if hasattr(self, 'lock_file') and os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except:
            pass
        
        # 强制退出所有线程
        print("程序已退出")
        os._exit(0)  # 强制退出，确保所有线程都被终止

def main():
    """主函数"""
    try:
        app = ScreenGuardian()
        app.start()
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()
