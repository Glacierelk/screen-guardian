import json
import hashlib
import os
from datetime import datetime

class ConfigManager:
    def __init__(self, config_file='screen_guardian_config.json'):
        self.config_file = config_file
        self.default_config = {
            'work_duration': 45,  # 工作时长（分钟）
            'break_duration': 15,  # 休息时长（分钟）
            'password_hash': '',   # 密码哈希
            'first_run': True,
            'last_session': None
        }
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.default_config, **json.load(f)}
            except Exception as e:
                print(f"配置文件加载失败: {e}")
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"配置文件保存失败: {e}")
            return False
    
    def set_password(self, password):
        """设置密码"""
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.config['password_hash'] = password_hash
        self.config['first_run'] = False
        return self.save_config()
    
    def verify_password(self, password):
        """验证密码"""
        if self.config['first_run']:
            return True  # 首次运行不需要密码
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return password_hash == self.config['password_hash']
    
    def get_work_duration(self):
        """获取工作时长（秒）"""
        return self.config['work_duration'] * 60
    
    def get_break_duration(self):
        """获取休息时长（秒）"""
        return self.config['break_duration'] * 60
    
    def set_durations(self, work_minutes, break_minutes):
        """设置时长"""
        self.config['work_duration'] = work_minutes
        self.config['break_duration'] = break_minutes
        return self.save_config()
    
    def is_first_run(self):
        """是否首次运行"""
        return self.config['first_run']
