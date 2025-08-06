# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox

class PasswordDialog:
    def __init__(self, config_manager, title="密码验证", message="请输入管理员密码："):
        self.config_manager = config_manager
        self.title = title
        self.message = message
        self.result = False
        self.root = None
        
    def show(self):
        """显示密码对话框"""
        self.root = tk.Toplevel()
        self.root.title(self.title)
        self.root.geometry("350x180")
        self.root.resizable(False, False)
        
        # 设置窗口始终在最前面
        self.root.attributes('-topmost', True)
        self.root.grab_set()
        
        # 设置窗口图标和样式
        try:
            # 隐藏窗口直到完全设置好
            self.root.withdraw()
        except:
            pass
        
        # 居中显示
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.root.winfo_screenheight() // 2) - (180 // 2)
        self.root.geometry(f"350x180+{x}+{y}")
        
        # 创建界面
        self.create_widgets()
        
        # 显示窗口
        self.root.deiconify()
        self.root.focus_force()
        
        # 等待用户输入
        self.root.wait_window()
        
        return self.result
    
    def create_widgets(self):
        """创建界面元素"""
        # 主容器
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 消息标签
        message_label = tk.Label(
            main_frame, 
            text=self.message, 
            font=("Microsoft YaHei", 11),
            bg='#f0f0f0',
            wraplength=300,
            justify='center'
        )
        message_label.pack(pady=(0, 15))
        
        # 密码输入框
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(
            main_frame, 
            textvariable=self.password_var,
            show="*",
            font=("Microsoft YaHei", 12),
            width=25,
            relief='solid',
            bd=1
        )
        password_entry.pack(pady=10)
        password_entry.focus_set()
        
        # 绑定回车键
        password_entry.bind('<Return>', self.verify_password)
        
        # 按钮框架
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=15)
        
        # 确定按钮
        ok_button = tk.Button(
            button_frame,
            text="确定",
            command=self.verify_password,
            font=("Microsoft YaHei", 10),
            width=10,
            bg='#4CAF50',
            fg='white',
            relief='flat',
            cursor='hand2'
        )
        ok_button.pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        cancel_button = tk.Button(
            button_frame,
            text="取消",
            command=self.cancel,
            font=("Microsoft YaHei", 10),
            width=10,
            bg='#f44336',
            fg='white',
            relief='flat',
            cursor='hand2'
        )
        cancel_button.pack(side=tk.LEFT, padx=10)
        
        # 处理窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def verify_password(self, event=None):
        """验证密码"""
        password = self.password_var.get()
        
        if not password:
            messagebox.showerror("错误", "请输入密码！")
            return
        
        if self.config_manager.verify_password(password):
            self.result = True
            self.root.destroy()
        else:
            messagebox.showerror("错误", "密码错误！")
            self.password_var.set("")
    
    def cancel(self):
        """取消"""
        self.result = False
        self.root.destroy()

def show_password_dialog(config_manager, title="密码验证", message="请输入管理员密码："):
    """显示密码对话框的便捷函数"""
    dialog = PasswordDialog(config_manager, title, message)
    return dialog.show()
