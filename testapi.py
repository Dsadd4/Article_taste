 




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
from bs4 import BeautifulSoup

def fetch_nature_biotechnology():
    try:
        if is_cached('nature_biotechnology'):
            return load_cache('nature_biotechnology')
        
        url = "https://www.nature.com/nbt/articles?year=2025"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        papers = []
        
        # 找到所有文章的 li 标签
        articles = soup.find_all('li', class_='app-article-list-row__item')

        for article in articles:
            # print(article)
            # 提取文章的链接
            # link = f"https://www.nature.com{article.find('a', class_='c-card__link u-link-inherit')['href']}"
            link_tag = article.find('a', class_='c-card__link u-link-inherit')
            if link_tag and 'href' in link_tag.attrs:
                link = f"https://www.nature.com{link_tag['href']}"
            else:
                # 如果链接格式不符合预期，则跳出循环
                print("Link format not as expected, skipping article.")
                break
            # 提取标题
            title = article.find('a', class_='c-card__link u-link-inherit').get_text(strip=True)
            
            # 可选：提取摘要
            summary = article.find('div', class_='c-card__summary')  # 定位到包含摘要的 div 标签
            if summary:
                p_tag = summary.find('p')  # 找到 div 标签中的 p 标签
                summary_text = p_tag.get_text(strip=True) if p_tag else "No summary available"
            else:
                summary_text = "No summary available"
            
            # 提取发布日期
            date_published = article.find('time', class_="c-meta__item c-meta__item--block-at-lg" ).get_text(strip=True)
            

            
            papers.append((title, link, summary_text, date_published))
            # assert()
        print(papers)
        assert()
        save_cache('nature_biotechnology', papers)
        return papers
    except Exception as e:
        return [(f"Error fetching Nature Biotechnology: {str(e)}", "", "", "")]


# url = "https://www.nature.com/nbt/articles?year=2025"
# response = requests.get(url)
# soup = BeautifulSoup(response.text, 'html.parser')

# papers = []
# # 找到所有文章的 li 标签
# articles = soup.find_all('li', class_='app-article-list-row__item')

# for article in articles:
#     # print(article)
#     # 提取文章的链接
#     link = f"https://www.nature.com{article.find('a', class_='c-card__link u-link-inherit')['href']}"
    
#     # 提取标题
#     title = article.find('a', class_='c-card__link u-link-inherit').get_text(strip=True)
    
#     # 可选：提取摘要
#     summary = article.find('div', class_='c-card__summary')  # 定位到包含摘要的 div 标签
#     if summary:
#         p_tag = summary.find('p')  # 找到 div 标签中的 p 标签
#         summary_text = p_tag.get_text(strip=True) if p_tag else "No summary available"
#     else:
#         summary_text = "No summary available"
    
#     # 提取发布日期
#     date_published = article.find('time', class_="c-meta__item c-meta__item--block-at-lg" ).get_text(strip=True)
    
#     papers.append((title, link, summary_text, date_published))
#     # assert()
# print(papers)
# assert()



print(fetch_nature_biotechnology())
assert()






# === test part===
import requests
from bs4 import BeautifulSoup
def fetch_nature_biotech():
    try:
        if is_cached('nature_biotech'):
            return load_cache('nature_biotech')
        url = "https://www.nature.com/nbt/articles?year=2025"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup)
        papers = []
        articles = soup.find_all('article', class_='card')
        for article in articles:
            link = article.find('a', class_='card-title')['href']
            title = article.find('a', class_='card-title').get_text(strip=True)
            papers.append((title, f"https://www.nature.com{link}"))
        save_cache('nature_biotech', papers)
        return papers
    except Exception as e:
        return [(f"Error fetching Nature Biotechnology: {str(e)}", "")]

url = "https://www.nature.com/nbt/articles?year=2025"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
with open("output.html", "w", encoding="utf-8") as f:
    f.write(soup.prettify())

print(soup)
# articles = soup.find_all('article', class_='card')
# print(articles )


# print(fetch_nature_biotech())