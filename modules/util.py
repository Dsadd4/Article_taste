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



import requests
from datetime import datetime, timedelta

def github_scrath(keyword, pages, recentyear):

    cache_name = 'github'

    url = 'https://api.github.com/search/repositories'
    
    # 获取两年前的日期
    recentyear_years_ago = (datetime.utcnow() - timedelta(days=recentyear*365)).strftime('%Y-%m-%d')
    
    params = {
        'q': f'{keyword} created:>{recentyear_years_ago}',  #
        'sort': 'created',
        'order': 'desc',
        'per_page': 100
    }

    # 分页请求
    all_repos = []
    for page in range(1, pages + 1):
        params['page'] = page
        response = requests.get(
            url, 
            params=params, 
            headers={
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': 'token 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'  # 替换为你的token
            }
        )
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.json().get('message')}")
            break
        
        data = response.json()
        items = data.get('items', [])
        if not items:
            break
        all_repos.extend(items)
    all_repos = sorted(all_repos,key=lambda x:-x['stargazers_count'])
    # 输出结果
    output = []
    for repo in all_repos:
        print(f"{repo['name']} - {repo['html_url']} - Stars: {repo['stargazers_count']}")
        output.append([repo['name'],repo['html_url'],repo['stargazers_count']])

    save_cache(cache_name, output)
    print(f'cache {cache_name} saved!')
    # print(f"\nTotal repositories fetched: {len(all_repos)}")
    return output




# # 调用函数，限制为最近两年创建的项目
# github_scrath('website', 2,1)
