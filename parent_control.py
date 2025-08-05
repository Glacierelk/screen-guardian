import tkinter as tk
from tkinter import ttk, messagebox
from config_manager import ConfigManager

class ParentControlPanel:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.root = None
        
    def show_settings(self):
        """显示设置界面"""
        if self.root:
            self.root.destroy()
            
        self.root = tk.Tk()
        self.root.title("ScreenGuardian - 家长控制面板")
        self.root.geometry("500x400")
        self.root.configure(bg='#ecf0f1')
        self.root.resizable(False, False)
        
        # 使窗口居中
        self.center_window()
        
        # 首次运行设置密码
        if self.config_manager.is_first_run():
            self.show_first_run_setup()
        else:
            self.show_password_prompt()
    
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
    
    def show_first_run_setup(self):
        """首次运行设置"""
        self.clear_window()
        
        # 标题
        title_label = tk.Label(
            self.root,
            text="🛡️ ScreenGuardian 初始设置",
            font=('Microsoft YaHei', 18, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title_label.pack(pady=30)
        
        # 说明
        info_label = tk.Label(
            self.root,
            text="欢迎使用 ScreenGuardian!\n请设置家长控制密码以保护设置不被修改",
            font=('Microsoft YaHei', 12),
            bg='#ecf0f1',
            fg='#34495e',
            justify='center'
        )
        info_label.pack(pady=20)
        
        # 密码输入框架
        password_frame = tk.Frame(self.root, bg='#ecf0f1')
        password_frame.pack(pady=20)
        
        tk.Label(
            password_frame,
            text="设置密码:",
            font=('Microsoft YaHei', 12),
            bg='#ecf0f1'
        ).grid(row=0, column=0, padx=10, pady=5, sticky='e')
        
        self.password_entry = tk.Entry(
            password_frame,
            show='*',
            font=('Microsoft YaHei', 12),
            width=20
        )
        self.password_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(
            password_frame,
            text="确认密码:",
            font=('Microsoft YaHei', 12),
            bg='#ecf0f1'
        ).grid(row=1, column=0, padx=10, pady=5, sticky='e')
        
        self.confirm_password_entry = tk.Entry(
            password_frame,
            show='*',
            font=('Microsoft YaHei', 12),
            width=20
        )
        self.confirm_password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # 按钮
        button_frame = tk.Frame(self.root, bg='#ecf0f1')
        button_frame.pack(pady=30)
        
        setup_button = tk.Button(
            button_frame,
            text="完成设置",
            font=('Microsoft YaHei', 12),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            command=self.complete_first_setup
        )
        setup_button.pack()
        
        self.password_entry.focus()
        self.root.bind('<Return>', lambda e: self.complete_first_setup())
    
    def complete_first_setup(self):
        """完成首次设置"""
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not password:
            messagebox.showerror("错误", "请输入密码")
            return
        
        if password != confirm_password:
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
        
        if len(password) < 4:
            messagebox.showerror("错误", "密码长度至少4位")
            return
        
        if self.config_manager.set_password(password):
            messagebox.showinfo("成功", "密码设置成功！")
            self.show_main_settings()
        else:
            messagebox.showerror("错误", "密码设置失败")
    
    def show_password_prompt(self):
        """显示密码输入界面"""
        self.clear_window()
        
        # 标题
        title_label = tk.Label(
            self.root,
            text="🔒 家长控制面板",
            font=('Microsoft YaHei', 18, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title_label.pack(pady=50)
        
        # 密码输入
        password_frame = tk.Frame(self.root, bg='#ecf0f1')
        password_frame.pack(pady=30)
        
        tk.Label(
            password_frame,
            text="请输入家长控制密码:",
            font=('Microsoft YaHei', 12),
            bg='#ecf0f1'
        ).pack(pady=10)
        
        self.password_entry = tk.Entry(
            password_frame,
            show='*',
            font=('Microsoft YaHei', 14),
            width=20
        )
        self.password_entry.pack(pady=10)
        
        # 按钮
        button_frame = tk.Frame(self.root, bg='#ecf0f1')
        button_frame.pack(pady=20)
        
        login_button = tk.Button(
            button_frame,
            text="确认",
            font=('Microsoft YaHei', 12),
            bg='#27ae60',
            fg='white',
            padx=30,
            pady=10,
            command=self.verify_password
        )
        login_button.pack(side='left', padx=10)
        
        cancel_button = tk.Button(
            button_frame,
            text="取消",
            font=('Microsoft YaHei', 12),
            bg='#e74c3c',
            fg='white',
            padx=30,
            pady=10,
            command=self.close_window
        )
        cancel_button.pack(side='left', padx=10)
        
        self.password_entry.focus()
        self.root.bind('<Return>', lambda e: self.verify_password())
    
    def verify_password(self):
        """验证密码"""
        password = self.password_entry.get()
        if self.config_manager.verify_password(password):
            self.show_main_settings()
        else:
            messagebox.showerror("错误", "密码错误")
            self.password_entry.delete(0, tk.END)
    
    def show_main_settings(self):
        """显示主设置界面"""
        self.clear_window()
        
        # 标题
        title_label = tk.Label(
            self.root,
            text="⚙️ ScreenGuardian 设置",
            font=('Microsoft YaHei', 18, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title_label.pack(pady=20)
        
        # 设置框架
        settings_frame = tk.LabelFrame(
            self.root,
            text="时间设置",
            font=('Microsoft YaHei', 12, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        settings_frame.pack(pady=20, padx=50, fill='x')
        
        # 工作时长设置
        work_frame = tk.Frame(settings_frame, bg='#ecf0f1')
        work_frame.pack(pady=10, fill='x')
        
        tk.Label(
            work_frame,
            text="连续使用时长（分钟）:",
            font=('Microsoft YaHei', 12),
            bg='#ecf0f1'
        ).pack(side='left')
        
        self.work_duration_var = tk.StringVar(value=str(self.config_manager.config['work_duration']))
        work_spinbox = tk.Spinbox(
            work_frame,
            from_=5,
            to=120,
            textvariable=self.work_duration_var,
            font=('Microsoft YaHei', 12),
            width=10
        )
        work_spinbox.pack(side='right')
        
        # 休息时长设置
        break_frame = tk.Frame(settings_frame, bg='#ecf0f1')
        break_frame.pack(pady=10, fill='x')
        
        tk.Label(
            break_frame,
            text="休息时长（分钟）:",
            font=('Microsoft YaHei', 12),
            bg='#ecf0f1'
        ).pack(side='left')
        
        self.break_duration_var = tk.StringVar(value=str(self.config_manager.config['break_duration']))
        break_spinbox = tk.Spinbox(
            break_frame,
            from_=1,
            to=60,
            textvariable=self.break_duration_var,
            font=('Microsoft YaHei', 12),
            width=10
        )
        break_spinbox.pack(side='right')
        
        # 按钮框架
        button_frame = tk.Frame(self.root, bg='#ecf0f1')
        button_frame.pack(pady=30)
        
        save_button = tk.Button(
            button_frame,
            text="保存设置",
            font=('Microsoft YaHei', 12),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            command=self.save_settings
        )
        save_button.pack(side='left', padx=10)
        
        close_button = tk.Button(
            button_frame,
            text="关闭",
            font=('Microsoft YaHei', 12),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=10,
            command=self.close_window
        )
        close_button.pack(side='left', padx=10)
    
    def save_settings(self):
        """保存设置"""
        try:
            work_duration = int(self.work_duration_var.get())
            break_duration = int(self.break_duration_var.get())
            
            if work_duration < 5 or work_duration > 120:
                messagebox.showerror("错误", "工作时长必须在5-120分钟之间")
                return
            
            if break_duration < 1 or break_duration > 60:
                messagebox.showerror("错误", "休息时长必须在1-60分钟之间")
                return
            
            if self.config_manager.set_durations(work_duration, break_duration):
                messagebox.showinfo("成功", "设置保存成功！")
                self.close_window()
            else:
                messagebox.showerror("错误", "设置保存失败")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def clear_window(self):
        """清空窗口内容"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def close_window(self):
        """关闭窗口"""
        if self.root:
            self.root.destroy()
            self.root = None
