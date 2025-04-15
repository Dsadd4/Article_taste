import math
from wordcloud import WordCloud
import matplotlib.pyplot as plt
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

# === CONFIGURATION ===
CONFIG_FILE = 'config.json'
CACHE_FILE = 'cache.json'

# Load configuration
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        CONFIG = json.load(f)
else:
    CONFIG = {"keywords": []}


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


import matplotlib.pyplot as plt
from wordcloud import WordCloud
import math


def generate_wordclouds(set_column=4):
    cache = load_all_cache()
    if not cache:
        print("No data in cache.")
        return None
    
    # 计算行数
    row = math.ceil(len(cache) / set_column)
    
    # 设置整体图表的尺寸，保持一个合理的宽高比
    fig_width = set_column * 5  # 每列5英寸
    fig_height = row * 2      # 每行4英寸
    figures, ax = plt.subplots(row, set_column, figsize=(fig_width, fig_height))

    # 计算每个词云的合适尺寸
    # dpi=300时的像素尺寸
    cloud_width = int((fig_width * 300) / set_column * 0.8)   # 80%的子图宽度
    cloud_height = int((fig_height * 300) / row * 0.8)        # 80%的子图高度

    if row == 1:
        ax = [ax]
    if set_column == 1:
        ax = [[a] for a in ax]

    row_number = 0
    column_number = 0

    for item in cache.keys():
        data = load_cache(item)
        if not data:
            continue
        
        text, *_ = zip(*data)
        titles = list(text)
        text = " ".join(titles)
        
        # 使用计算得到的尺寸创建词云
        wordcloud = WordCloud(
            width=cloud_width, 
            height=cloud_height,
            background_color='white',
            max_font_size=min(cloud_width, cloud_height) // 3,  # 根据尺寸调整最大字体
            min_font_size=8  # 设置最小字体确保可读性
        ).generate(text)
        
        ax[row_number][column_number].imshow(wordcloud, interpolation='bilinear')
        ax[row_number][column_number].axis('off')
        ax[row_number][column_number].set_title(item, pad=10)  # 添加一些标题边距
        
        column_number += 1
        if column_number == set_column:
            column_number = 0
            row_number += 1
    
    # 删除多余的空白子图
    for i in range(row_number * set_column + column_number, row * set_column):
        figures.delaxes(ax[i // set_column][i % set_column])

    # 调整子图之间的间距
    plt.tight_layout(pad=3.0)  # 增加间距，防止词云重叠

    # 保存图片
    file_path = './wordcloud.png'
    figures.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
    plt.close(figures)

    return file_path


def generate_citation_plot():
    """生成引用量分布图"""
    cache = load_all_cache()
    scholar_data = cache.get('scholar', {}).get('data', [])
    
    if not scholar_data:
        print("No Google Scholar data in cache.")
        return None
    
    # 提取引用数据
    titles = []
    citations = []
    for title, _, _, citation in scholar_data:
        if citation > 0:  # 只显示有引用的论文
            titles.append(title[:50] + '...' if len(title) > 50 else title)
            citations.append(citation)
    
    # 创建柱状图
    fig, ax = plt.subplots(figsize=(30, 10))
    bars = ax.bar(range(len(citations)), citations)
    
    # 设置标签和标题
    ax.set_xlabel('Papers')
    ax.set_ylabel('Citations')
    ax.set_title('Citation Distribution')
    
    # 设置x轴标签
    ax.set_xticks(range(len(titles)))
    ax.set_xticklabels(titles, rotation=45, ha='right')
    
    # 在柱子上显示具体数值
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    file_path = './citations.png'
    plt.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return file_path

def generate_github_stars_plot():
    """生成GitHub stars分布图"""
    cache = load_all_cache()
    github_data = cache.get('github', {}).get('data', [])
    
    if not github_data:
        print("No GitHub data in cache.")
        return None
    
    # 提取stars数据
    repos = []
    stars = []
    for title, _, star_count in github_data[0:100]:
        repos.append(title[:30] + '...' if len(title) > 30 else title)
        stars.append(int(star_count))
    
    # 创建柱状图
    fig, ax = plt.subplots(figsize=(30, 10))
    bars = ax.bar(range(len(stars)), stars)
    
    # 设置标签和标题
    ax.set_xlabel('Repositories')
    ax.set_ylabel('Stars')
    ax.set_title('GitHub Repository Stars Distribution')
    
    # 设置x轴标签
    ax.set_xticks(range(len(repos)))
    ax.set_xticklabels(repos, rotation=45, ha='right')
    
    # 在柱子上显示具体数值
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    file_path = './github_stars.png'
    plt.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return file_path

def generate_source_distribution():
    """生成文章来源分布饼图"""
    cache = load_all_cache()
    '''首先指定搜索对象'''
    target_object = ['github', 'scholar']

    # 统计每个来源的文章数量
    source_counts = {}
    for source, data in cache.items():
        if source not in target_object:  # 排除非期刊来源
            count = len(data.get('data', []))
            if count > 0:
                source_counts[source] = count
    
    if not source_counts:
        print("No journal data in cache.")
        return None
    
    # 创建饼图
    fig, ax = plt.subplots(figsize=(10, 10))
    wedges, texts, autotexts = ax.pie(source_counts.values(), 
                                     labels=source_counts.keys(),
                                     autopct='%1.1f%%',
                                     textprops={'fontsize': 12})
    
    # 设置标题
    ax.set_title('Distribution of Articles by Source')
    
    # 添加图例
    ax.legend(wedges, source_counts.keys(),
             title="Sources",
             loc="center left",
             bbox_to_anchor=(1, 0, 0.5, 1))
    
    # 保存图片
    file_path = './source_distribution.png'
    plt.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return file_path