import pystray
from PIL import Image, ImageDraw
import threading
import time
import tkinter as tk
from tkinter import messagebox
from password_dialog import show_password_dialog

class TrayIcon:
    def __init__(self, screen_guardian):
        self.screen_guardian = screen_guardian
        self.icon = None
        self.running = False
        
    def create_icon_image(self, color='green'):
        """创建托盘图标"""
        # 创建一个简单的圆形图标
        image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # 根据状态选择颜色
        colors = {
            'green': '#27ae60',    # 正常工作
            'red': '#e74c3c',      # 休息中
            'orange': '#f39c12'    # 警告
        }
        
        fill_color = colors.get(color, '#27ae60')
        
        # 绘制圆形
        draw.ellipse([8, 8, 56, 56], fill=fill_color)
        
        # 绘制盾牌形状
        draw.polygon([
            (32, 16), (24, 20), (16, 28), (16, 36),
            (24, 48), (32, 52), (40, 48), (48, 36),
            (48, 28), (40, 20)
        ], fill='white')
        
        # 绘制字母 "S"
        try:
            draw.text((28, 26), "S", fill=fill_color, anchor="mm")
        except TypeError:
            # 兼容旧版本PIL
            draw.text((25, 22), "S", fill=fill_color)
        
        return image
    
    def update_icon(self, status='working'):
        """更新图标状态"""
        if not self.icon:
            return
            
        color_map = {
            'working': 'green',
            'resting': 'red',
            'warning': 'orange'
        }
        
        color = color_map.get(status, 'green')
        new_image = self.create_icon_image(color)
        self.icon.icon = new_image
    
    def create_menu(self):
        """创建右键菜单"""
        try:
            monitoring_text = "暂停监控" if self.screen_guardian.monitoring_active else "恢复监控"
            
            return pystray.Menu(
                pystray.MenuItem(
                    "设置",
                    self.show_settings,
                    default=True
                ),
                pystray.MenuItem(
                    "状态信息",
                    self.show_status
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    monitoring_text,
                    self.toggle_monitoring_with_password
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    "退出",
                    self.quit_application_with_password
                )
            )
        except Exception as e:
            print(f"创建菜单失败: {e}")
            # 返回一个基本菜单
            return pystray.Menu(
                pystray.MenuItem("退出", self.quit_application_with_password)
            )
    
    def show_settings(self, icon=None, item=None):
        """显示设置界面"""
        self.screen_guardian.show_settings()
    
    def show_status(self, icon=None, item=None):
        """显示状态信息"""
        def display_status():
            try:
                # 添加延迟确保托盘菜单完全关闭
                time.sleep(0.1)
                
                # 获取状态信息
                status = self.screen_guardian.get_status_info()
                monitoring_status = "启用" if self.screen_guardian.monitoring_active else "暂停"
                current_state = "工作中" if self.screen_guardian.current_state == 'working' else "休息中"
                
                # 获取配置信息
                config = self.screen_guardian.config_manager
                work_duration = config.get_work_duration()
                break_duration = config.get_break_duration()
                
                # 格式化工作和休息时长
                work_minutes = work_duration // 60
                break_minutes = break_duration // 60
                
                # 使用简单的消息框显示状态信息
                status_message = f"""ScreenGuardian 状态信息

监控状态: {monitoring_status}
当前状态: {current_state}
详细信息: {status}
工作时长: {work_minutes} 分钟
休息时长: {break_minutes} 分钟

提示: 右键托盘图标可以访问更多功能"""
                
                messagebox.showinfo("ScreenGuardian 状态信息", status_message)
                
            except Exception as e:
                print(f"显示状态信息失败: {e}")
                # 如果获取状态失败，使用简单的消息框
                try:
                    status = self.screen_guardian.get_status_info()
                    monitoring_status = "启用" if self.screen_guardian.monitoring_active else "暂停"
                    messagebox.showinfo("状态信息", 
                                      f"监控状态: {monitoring_status}\n当前状态: {status}")
                except:
                    messagebox.showinfo("状态信息", "无法获取状态信息")
        
        # 在单独线程中显示状态窗口
        threading.Thread(target=display_status, daemon=True).start()
    
    def toggle_monitoring_with_password(self, icon=None, item=None):
        """切换监控状态（需要密码验证）"""
        def verify_and_toggle():
            try:
                # 添加延迟确保托盘菜单完全关闭
                time.sleep(0.1)
                
                # 显示密码验证对话框
                if show_password_dialog(
                    self.screen_guardian.config_manager,
                    "密码验证",
                    "暂停/恢复监控需要管理员权限："
                ):
                    # 切换监控状态
                    self.screen_guardian.toggle_monitoring()
                    
                    # 延迟更新菜单，避免线程冲突
                    def delayed_update():
                        time.sleep(0.2)
                        self.update_menu()
                    
                    threading.Thread(target=delayed_update, daemon=True).start()
                    
            except Exception as e:
                print(f"密码验证失败: {e}")
        
        # 在单独线程中执行，避免阻塞托盘图标
        threading.Thread(target=verify_and_toggle, daemon=True).start()
    
    def quit_application_with_password(self, icon=None, item=None):
        """退出应用程序（需要密码验证）"""
        def verify_and_quit():
            try:
                # 添加延迟确保托盘菜单完全关闭
                time.sleep(0.1)
                
                # 显示密码验证对话框
                if show_password_dialog(
                    self.screen_guardian.config_manager,
                    "密码验证",
                    "退出程序需要管理员权限，请输入密码："
                ):
                    # 延迟执行退出，确保对话框完全关闭
                    def delayed_quit():
                        time.sleep(0.2)
                        self.screen_guardian.quit_application()
                        self.stop()
                    
                    threading.Thread(target=delayed_quit, daemon=True).start()
                    
            except Exception as e:
                print(f"密码验证失败: {e}")
        
        # 在单独线程中执行，避免阻塞托盘图标
        threading.Thread(target=verify_and_quit, daemon=True).start()
    
    def update_menu(self):
        """更新菜单"""
        try:
            if self.icon and self.running:
                new_menu = self.create_menu()
                self.icon.menu = new_menu
        except Exception as e:
            print(f"更新菜单失败: {e}")
    
    def toggle_monitoring(self, icon=None, item=None):
        """切换监控状态（保留原方法，用于内部调用）"""
        self.screen_guardian.toggle_monitoring()
    
    def quit_application(self, icon=None, item=None):
        """退出应用程序（保留原方法，用于内部调用）"""
        self.screen_guardian.quit_application()
        self.stop()
    
    def start(self):
        """启动托盘图标"""
        if self.running:
            return
            
        self.running = True
        
        # 创建图标
        image = self.create_icon_image()
        menu = self.create_menu()
        
        self.icon = pystray.Icon(
            "ScreenGuardian",
            image,
            "ScreenGuardian - 电脑使用时间管理",
            menu
        )
        
        # 在单独线程中运行托盘图标
        self.tray_thread = threading.Thread(target=self._run_tray, daemon=True)
        self.tray_thread.start()
    
    def _run_tray(self):
        """运行托盘图标"""
        try:
            self.icon.run()
        except Exception as e:
            print(f"托盘图标运行失败: {e}")
    
    def stop(self):
        """停止托盘图标"""
        self.running = False
        if self.icon:
            self.icon.stop()
