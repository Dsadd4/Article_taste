import time
import logging
import os
from CloudflareBypasser import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions

import os
import sys
import time
import json
import schedule
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget, QScrollArea)
from pystray import Icon, MenuItem, Menu
from PIL import Image
import win32com.client
import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
# Configure loggin

CACHE_FILE = 'cache.json'

# === CACHE HANDLING ===
def save_cache(source, data):
    cache = load_all_cache()
    cache[source] = {"data": data, "timestamp": time.strftime('%Y-%m-%d')}
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def load_cache(source):
    cache = load_all_cache()
    return cache.get(source, {}).get("data", [])

def load_all_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def is_cached(source):
    cache = load_all_cache()
    cached_date = cache.get(source, {}).get("timestamp", "")
    return cached_date == time.strftime('%Y-%m-%d')


import os
import shutil
from datetime import datetime

def back_up_data(file_names):
   
    backup_dir = 'backup'
    # 获取当前日期和时间
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    hour_str = now.strftime('%H')
    
    # 创建备份目录（如果不存在）
    date_backup_dir = os.path.join(backup_dir, date_str)
    os.makedirs(date_backup_dir, exist_ok=True)
    
    for file_name in file_names:
        if os.path.exists(file_name):
            # 构造新文件名，添加小时标注
            base_name, ext = os.path.splitext(file_name)
            new_file_name = f"{base_name}_{hour_str}{ext}"
            dest_path = os.path.join(date_backup_dir, new_file_name)
            
            # 复制文件
            shutil.copy(file_name, dest_path)
            print(f"Backed up '{file_name}' to '{dest_path}'")
        else:
            print(f"Warning: '{file_name}' not found, skipping.")
