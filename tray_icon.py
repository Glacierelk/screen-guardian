import pystray
from PIL import Image, ImageDraw
import threading
import time
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
                "暂停监控" if self.screen_guardian.monitoring_active else "恢复监控",
                self.toggle_monitoring_with_password
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "退出",
                self.quit_application_with_password
            )
        )
    
    def show_settings(self, icon=None, item=None):
        """显示设置界面"""
        self.screen_guardian.show_settings()
    
    def show_status(self, icon=None, item=None):
        """显示状态信息"""
        status = self.screen_guardian.get_status_info()
        # 这里可以实现一个简单的状态显示窗口
        print(f"当前状态: {status}")
    
    def toggle_monitoring_with_password(self, icon=None, item=None):
        """切换监控状态（需要密码验证）"""
        def verify_and_toggle():
            try:
                # 显示密码验证对话框
                if show_password_dialog(
                    self.screen_guardian.config_manager,
                    "密码验证",
                    "暂停/恢复监控需要管理员权限，请输入密码："
                ):
                    self.screen_guardian.toggle_monitoring()
                    # 更新菜单文本
                    self.update_menu()
            except Exception as e:
                print(f"密码验证失败: {e}")
        
        # 在单独线程中执行，避免阻塞托盘图标
        threading.Thread(target=verify_and_toggle, daemon=True).start()
    
    def quit_application_with_password(self, icon=None, item=None):
        """退出应用程序（需要密码验证）"""
        def verify_and_quit():
            try:
                # 显示密码验证对话框
                if show_password_dialog(
                    self.screen_guardian.config_manager,
                    "密码验证",
                    "退出程序需要管理员权限，请输入密码："
                ):
                    self.screen_guardian.quit_application()
                    self.stop()
            except Exception as e:
                print(f"密码验证失败: {e}")
        
        # 在单独线程中执行，避免阻塞托盘图标
        threading.Thread(target=verify_and_quit, daemon=True).start()
    
    def update_menu(self):
        """更新菜单"""
        if self.icon:
            self.icon.menu = self.create_menu()
    
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
