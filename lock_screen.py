import tkinter as tk
from tkinter import ttk
import random
import time
import threading
from password_dialog import show_password_dialog

class LockScreen:
    def __init__(self, break_duration_seconds, config_manager, on_break_end=None, on_early_exit=None):
        self.break_duration = break_duration_seconds
        self.remaining_time = break_duration_seconds
        self.config_manager = config_manager
        self.on_break_end = on_break_end
        self.on_early_exit = on_early_exit  # 提前退出回调
        self.is_locked = True
        self.root = None
        self.password_dialog_open = False
        
    def create_window(self):
        """创建锁屏窗口"""
        # 创建全屏窗口
        self.root = tk.Tk()
        self.root.title("ScreenGuardian - 休息时间")
        # 使用半透明的灰色背景，模拟磨玻璃效果
        self.root.configure(bg='#808080')
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置窗口大小和位置
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # 设置全屏和置顶属性
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.85)  # 设置透明度，创造磨玻璃效果
        
        # 禁用窗口装饰
        self.root.overrideredirect(True)
        
        # 设置窗口状态
        self.root.state('normal')
        self.root.lift()
        self.root.focus_force()
        
        # 禁用关闭和快捷键
        self.root.protocol("WM_DELETE_WINDOW", self.do_nothing)
        self.root.bind('<Alt-F4>', self.do_nothing)
        self.root.bind('<Control-Alt-Delete>', self.do_nothing)
        self.root.bind('<Control-c>', self.do_nothing)
        self.root.bind('<Control-v>', self.do_nothing)
        
        # 特殊处理ESC键 - 弹出密码验证
        self.root.bind('<Escape>', self.handle_escape_key)
        
        # 捕获其他所有键盘输入
        self.root.bind('<Key>', self.handle_other_keys)
        
        return self.root
        
    def do_nothing(self, event=None):
        """阻止窗口关闭"""
        return "break"
    
    def handle_escape_key(self, event=None):
        """处理ESC键 - 显示密码验证"""
        if self.password_dialog_open:
            return "break"
        
        self.password_dialog_open = True
        
        def verify_password():
            try:
                # 创建密码验证对话框
                result = show_password_dialog(
                    self.config_manager,
                    "提前结束休息",
                    "输入管理员密码以提前结束休息："
                )
                
                if result:
                    print("密码验证成功，提前结束休息")
                    # 调用提前退出回调
                    if self.on_early_exit:
                        self.on_early_exit()
                    # 解锁屏幕
                    self.unlock_screen()
                else:
                    print("密码验证失败或取消")
                    
            except Exception as e:
                print(f"密码验证过程出错: {e}")
            finally:
                self.password_dialog_open = False
        
        # 在单独线程中处理密码验证，避免阻塞UI
        threading.Thread(target=verify_password, daemon=True).start()
        return "break"
    
    def handle_other_keys(self, event=None):
        """处理其他键盘输入 - 阻止所有操作"""
        return "break"
    
    def setup_ui(self):
        """设置界面 - 磨玻璃效果"""
        # 主容器 - 半透明灰色背景
        main_frame = tk.Frame(self.root, bg='#555555')
        main_frame.pack(expand=True, fill='both')
        
        # 创建一个内层容器，模拟磨玻璃效果
        glass_frame = tk.Frame(main_frame, bg='#888888', relief='ridge', bd=3)
        glass_frame.place(relx=0.5, rely=0.5, anchor='center', 
                         relwidth=0.75, relheight=0.8)
        
        # 添加内边框效果
        inner_frame = tk.Frame(glass_frame, bg='#999999', relief='sunken', bd=2)
        inner_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            inner_frame, 
            text="🛡️ ScreenGuardian", 
            font=('Microsoft YaHei', 26, 'bold'),
            fg='#ffffff', 
            bg='#999999'
        )
        title_label.pack(pady=(30, 20))
        
        # 休息提示
        rest_label = tk.Label(
            inner_frame,
            text="🌟 休息时间到了！让眼睛放松一下吧 🌟",
            font=('Microsoft YaHei', 18),
            fg='#ffe082',
            bg='#999999'
        )
        rest_label.pack(pady=15)
        
        # 倒计时显示
        self.time_label = tk.Label(
            inner_frame,
            text="",
            font=('Microsoft YaHei', 40, 'bold'),
            fg='#ffffff',
            bg='#999999'
        )
        self.time_label.pack(pady=25)
        
        # 健康建议
        self.advice_label = tk.Label(
            inner_frame,
            text="",
            font=('Microsoft YaHei', 15),
            fg='#e8f5e8',
            bg='#999999',
            wraplength=500,
            justify='center'
        )
        self.advice_label.pack(pady=15)
        
        # 眼保健操提示容器
        exercise_container = tk.Frame(inner_frame, bg='#aaaaaa', relief='groove', bd=2)
        exercise_container.pack(pady=20, padx=40, fill='x')
        
        tk.Label(
            exercise_container,
            text="👁️ 简单的眼部放松动作 👁️",
            font=('Microsoft YaHei', 16, 'bold'),
            fg='#ffc107',
            bg='#aaaaaa'
        ).pack(pady=10)
        
        exercises = [
            "1. 闭眼深呼吸 10 秒",
            "2. 眼球左右转动 5 次", 
            "3. 远眺窗外远处物体",
            "4. 轻轻按摩眼部周围",
            "5. 眨眼 20 次"
        ]
        
        for exercise in exercises:
            tk.Label(
                exercise_container,
                text=exercise,
                font=('Microsoft YaHei', 13),
                fg='#f5f5f5',
                bg='#aaaaaa'
            ).pack(pady=2)
        
        # 底部提示
        bottom_label = tk.Label(
            inner_frame,
            text="⏰ 休息结束后将自动解锁，请耐心等待",
            font=('Microsoft YaHei', 12),
            fg='#d0d0d0',
            bg='#999999'
        )
        bottom_label.pack(side='bottom', pady=15)
    
    def update_timer(self):
        """更新倒计时"""
        if self.remaining_time > 0:
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            time_text = f"{minutes:02d}:{seconds:02d}"
            self.time_label.config(text=f"剩余时间: {time_text}")
            
            # 更新健康建议
            self.update_advice()
            
            self.remaining_time -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.unlock_screen()
    
    def update_advice(self):
        """更新健康建议"""
        advices = [
            "💧 记得喝点水，保持身体水分充足",
            "🧘 深呼吸几次，让身心得到放松",
            "🚶 起身走动一下，活动活动筋骨",
            "🌿 看看绿色植物或远处的风景",
            "💪 做几个简单的颈部和肩部运动",
            "😊 保持微笑，放松面部肌肉",
            "🎵 听听轻松的音乐，放松心情"
        ]
        
        # 每15秒更换一次建议
        if self.remaining_time % 15 == 0:
            advice = random.choice(advices)
            self.advice_label.config(text=advice)
    
    def show(self):
        """显示锁屏"""
        try:
            # 创建窗口
            self.create_window()
            
            # 设置界面
            self.setup_ui()
            
            # 启动定时器
            self.update_timer()
            
            # 确保窗口获得焦点
            self.root.after(100, self._ensure_focus)
            
            # 运行主循环
            self.root.mainloop()
            
        except Exception as e:
            print(f"锁屏显示失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _ensure_focus(self):
        """确保窗口获得焦点"""
        try:
            self.root.lift()
            self.root.focus_force()
            self.root.attributes('-topmost', True)
            # 每秒重新确保置顶
            if self.is_locked:
                self.root.after(1000, self._ensure_focus)
        except:
            pass
    
    def unlock_screen(self):
        """解锁屏幕"""
        print("解锁屏幕")
        self.is_locked = False
        
        if self.on_break_end:
            self.on_break_end()
            
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
