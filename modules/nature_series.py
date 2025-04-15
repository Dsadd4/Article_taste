
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

# 每批抓取 10 页，每次启动 10 个线程
BATCH_SIZE = 5
MAX_THREADS = 5
MAX_PAGES = 100  # 最多抓100页，防止无限爬取

# conda activate scrath_new

# === CONFIGURATION ===
CONFIG_FILE = 'config.json'
CACHE_FILE = 'cache.json'

# Load configuration
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        CONFIG = json.load(f)
else:
    CONFIG = {"keywords": []}


#=== 处理nature系列期刊 ===
# 映射 journal_name 到期刊缩写
JOURNAL_MAPPING = {
    'nature_biotechnology': 'nbt',
    'nature_methods': 'nmeth',
    'nature_machine_intelligence': 'natmachintell',
    'nature': 'nature',
    'nature_computer_science': 'natcomputsci',
    'nature_communications': 'ncomms'
}




def sanitize_filename(filename):
    # 去除不合法的文件名字符
    return re.sub(r'[\/:*?"<>|]', '', filename)

def create_download_dir():
    today = datetime.today().strftime('%Y-%m-%d')
    download_path = os.path.join(os.getcwd(), 'download', today)
    if not os.path.exists(download_path):
        os.makedirs(download_path, exist_ok=True)
    return download_path

def download_pdf(title, link):
    try:
        download_path = create_download_dir()
        pdf_link = link.replace('/abs/', '/pdf/')

        #debug
        print(f"we now try to download{pdf_link } ")

        response = requests.get(pdf_link)
        if response.status_code == 200:
            sanitized_title = sanitize_filename(title)
            filename = os.path.join(download_path, f"{sanitized_title}.pdf")
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Downloaded: {filename}")
        else:
            print(f"❌ Failed to download: {pdf_link} (Status Code: {response.status_code})")
    except Exception as e:
        print(f"❌ Error downloading {link}: {str(e)}")


import concurrent.futures
import requests
from bs4 import BeautifulSoup


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


def fetch_page(journal_name, page_number):
    try:
        journal_abbr = JOURNAL_MAPPING[journal_name] 
        url = f"https://www.nature.com/{journal_abbr}/articles?searchType=journalSearch&sort=PubDate&year=2025&page={page_number}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('li', class_='app-article-list-row__item')
        if not articles:
            return []

        papers = []
        for article in articles:
            link_tag = article.find('a', class_='c-card__link u-link-inherit')
            if link_tag and 'href' in link_tag.attrs:
                link = f"https://www.nature.com{link_tag['href']}"
            else:
                continue

            title = link_tag.get_text(strip=True)

            # 摘要
            summary = article.find('div', class_='c-card__summary')
            if summary:
                p_tag = summary.find('p')
                summary_text = p_tag.get_text(strip=True) if p_tag else "No summary available"
            else:
                summary_text = "No summary available"

            # 发布日期
            date_published = article.find('time', class_="c-meta__item c-meta__item--block-at-lg")
            date_published = date_published.get_text(strip=True) if date_published else "No date available"

            papers.append((title, link, summary_text, date_published))

        return papers

    except Exception as e:
        print(f"Error fetching page {page_number}: {e}")
        return []


def fetch_nature_series(journal_name):
    try:
        if is_cached(journal_name):
            return load_cache(journal_name)

        papers = []
        page_number = 1

        while True:
            print(f"🚀 开始抓取第 {page_number} 页到第 {page_number + BATCH_SIZE - 1} 页")

            batch_results = []
            stop_flag = False

            # 使用 ThreadPoolExecutor 进行并行抓取
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                future_to_page = {
                    executor.submit(fetch_page, journal_name, page): page
                    for page in range(page_number, page_number + BATCH_SIZE)
                }
                for future in concurrent.futures.as_completed(future_to_page):
                    page = future_to_page[future]
                    try:
                        result = future.result()
                        if not result:
                            print(f"⚠️ 第 {page} 页为空，可能是末页，准备停止抓取。")
                            stop_flag = True
                        else:
                            batch_results.extend(result)
                    except Exception as e:
                        print(f"⚠️ 抓取第 {page} 页失败: {e}")

            # 合并当前批次结果
            papers.extend(batch_results)

            if stop_flag or page_number + BATCH_SIZE > MAX_PAGES:
                print("✅ 抓取完成！")
                break

            # 更新下一批抓取的起点
            page_number += BATCH_SIZE

        # 保存结果（缓存）
        save_cache(journal_name, papers)
        return papers

    except Exception as e:
        print(f"❌ Error fetching {journal_name}: {e}")
        return [(f"Error fetching {journal_name}: {str(e)}", "", "", "")]
