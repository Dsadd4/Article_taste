 




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




response = requests.get("https://www.cell.com/cell/issue?pii=S0092-8674(24)X0002-1")

print(response.text)


from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式
driver = webdriver.Chrome(options=options)

url = 'https://www.cell.com/cell/issue?pii=S0092-8674(24)X0002-1'
driver.get(url)
print(driver.page_source)  # 获取页面内容
driver.quit()

assert(0)














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











import math
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_wordclouds(set_column=4):
    cache = load_all_cache()
    if not cache:
        print("No data in cache.")
        return
    
    row = math.ceil(len(cache) / set_column)  # 向上取整，防止遗漏
    figures, ax = plt.subplots(row, set_column, figsize=(set_column * 5, row * 3))

    # 标准化 ax 为二维数组，防止出现一维或标量情况
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
        
        text, *_ = zip(*data)  # 只取第一列
        titles = list(text)
        text = " ".join(titles)
        
        # 生成词云
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        
        # 绘制词云
        ax[row_number][column_number].imshow(wordcloud, interpolation='bilinear')
        ax[row_number][column_number].axis('off')  # 关闭坐标轴
        ax[row_number][column_number].set_title(item)  # 添加标题
        
        column_number += 1
        if column_number == set_column:  # 列满时换行
            column_number = 0
            row_number += 1
    
    # 删除多余的空白子图
    for i in range(row_number * set_column + column_number, row * set_column):
        figures.delaxes(ax[i // set_column][i % set_column])

    plt.tight_layout()
    plt.show()

# 加载缓存


# 调用函数
generate_wordclouds()






assert(0)


import requests

import requests
from datetime import datetime, timedelta
import requests
from datetime import datetime, timedelta
import concurrent.futures

import requests
from datetime import datetime, timedelta
import concurrent.futures

import requests
from datetime import datetime, timedelta

import requests
from datetime import datetime, timedelta

def fetch_biorxiv_medrxiv():
    try:
        if is_cached('biorxiv_medrxiv'):
            return load_cache('biorxiv_medrxiv')

        # Get today's date
        today = datetime.today()

        # Calculate the date for one week ago from today
        one_week_ago = today - timedelta(weeks=1)

        # Format the dates to the required string format for the API (YYYY-MM-DD)
        start_date = one_week_ago.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')

        papers = []
        offset = 0  # Start from the first batch
        while True:
            # Create the URL with the dynamic date range and the offset
            url = f"https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/{offset}"
            response = requests.get(url)
            data = response.json()

            # Check if there are any papers in the response
            collection = data.get('collection', [])
            if not collection:
                break  # Exit the loop if no more papers are found

            # Process the papers in the current batch
            for item in collection:
                # Extract the DOI
                doi = item.get('doi', 'N/A')
                link = f"https://www.biorxiv.org/content/{doi}"

                # Extract the title
                title = item.get('title', 'N/A')

                # Extract the publication date
                date = item.get('date', 'N/A')

                # Create the paper tuple and add it to the list
                papers.append((title, link, date, []))

            # Increment the offset for the next batch
            offset += 100
            print(offset)
        # Save the result to cache
        save_cache('biorxiv_medrxiv', papers)
        return papers

    except Exception as e:
        return [(f"Error fetching bioRxiv/medRxiv: {str(e)}", "")]








import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_biorxiv_medrxiv():
    try:
        if is_cached('biorxiv_medrxiv'):
            return load_cache('biorxiv_medrxiv')

        # Get today's date
        today = datetime.today()

        # Calculate the date for one week ago from today
        one_week_ago = today - timedelta(weeks=1)

        # Format the dates to the required string format for the API (YYYY-MM-DD)
        start_date = one_week_ago.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')

        papers = []
        max_threads = 3  # Number of threads to use
        offset = 0  # Start from the first batch

        def fetch_batch(offset):
            # Create the URL with the dynamic date range and the offset
            url = f"https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/{offset}"
            response = requests.get(url)
            data = response.json()

            # Process the papers in the current batch
            batch_papers = []
            collection = data.get('collection', [])
            for item in collection:
                # Extract the DOI
                doi = item.get('doi', 'N/A')
                link = f"https://www.biorxiv.org/content/{doi}"

                # Extract the title
                title = item.get('title', 'N/A')

                # Extract the publication date
                date = item.get('date', 'N/A')

                # Create the paper tuple and add it to the list
                batch_papers.append((title, link, date, []))
            return batch_papers

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            while True:
                # Dispatch multiple requests
                for i in range(max_threads):
                    futures.append(executor.submit(fetch_batch, offset))
                    offset += 100  # Increment offset for the next batch
                print(offset)
                # Wait for all threads to finish
                for future in as_completed(futures):
                    papers.extend(future.result())

                # If no more papers are fetched, break the loop
                if len(futures) < max_threads or len(futures[-1].result()) == 0:
                    break

        # Save the result to cache
        save_cache('biorxiv_medrxiv', papers)
        return papers

    except Exception as e:
        return [(f"Error fetching bioRxiv/medRxiv: {str(e)}", "")]



print(fetch_biorxiv_medrxiv())
assert(0)


from paperscraper.get_dumps import biorxiv, medrxiv, chemrxiv

biorxiv(start_date="2025-03-01", end_date="2025-03-02")
assert(0)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# 设置 WebDriver 路径
driver = webdriver.Chrome()

# 打开目标网页
driver.get("https://www.biorxiv.org/content/early/recent?page=3")

# 等待页面加载
driver.implicitly_wait(10)

# 找到并模拟点击
button = driver.find_element(By.ID, "button-id")  # 根据页面元素定位
action = ActionChains(driver)
action.click(button).perform()

# 等待并抓取网页内容
print(driver.page_source)

# 关闭浏览器
driver.quit()



assert(0)






from playwright.sync_api import sync_playwright

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto("https://www.biorxiv.org/content/early/recent?page=3", timeout=60000)

        # 等待页面加载并点击按钮
        try:
            page.wait_for_selector("text='Verify'", timeout=20000)
            page.click("text='Verify'")
            print("点击按钮成功")
        except Exception as e:
            print(f"未找到按钮或点击失败: {e}")

        # 获取HTML内容
        html = page.content()
        print(html)

        browser.close()

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth
import time

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync  # 使用正确的导入
import time

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # 使用 stealth_sync 来应用反检测功能
        stealth_sync(page)

        # 访问目标页面
        page.goto("https://www.biorxiv.org/content/early/recent?page=3", timeout=60000)

        try:
            # 等待并点击标签
            label = page.locator('label.cb-lb')
            label.wait_for(state="visible", timeout=10000)
            label.click()

            print("点击标签成功")

            # 等待页面加载完成
            page.wait_for_load_state('networkidle')

        except Exception as e:
            print(f"未找到标签或点击失败: {e}")

        # 获取HTML内容
        html = page.content()
        print(html)

        browser.close()

scrape()






assert(0)








import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time

# 每批抓取 10 页，每次启动 10 个线程
BATCH_SIZE = 10
MAX_THREADS = 10
MAX_PAGES = 100  # 最多抓取 100 页


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 配置浏览器
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 不显示窗口
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 启动浏览器
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 打开目标网页
url = "https://www.biorxiv.org/content/early/recent?page=1"
driver.get(url)

# 获取加载后的网页内容
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# 打印内容
print(soup.prettify())

# 关闭浏览器
driver.quit()



with open("example.html",'w',encoding='utf-8') as f:
    f.write(str(soup))

def fetch_page_biorxiv(page_number):
    try:
        url = f"https://www.biorxiv.org/content/early/recent?page={page_number}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ 第 {page_number} 页获取失败，状态码: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        with open("example.html",'w',encoding='utf-8') as f:
            f.write(str(soup))
        
        articles = soup.find_all('div', class_='highwire-cite highwire-cite-highwire-article highwire-citation-biorxiv-article-pap-list clearfix')
        if not articles:
            print(f"⚠️ 第 {page_number} 页没有找到文章，可能是末页。")
            return []

        papers = []
        for article in articles:
            # 标题和链接
            link_tag = article.find('a', class_='highwire-cite-linked-title')
            if link_tag and 'href' in link_tag.attrs:
                link = f"https://www.biorxiv.org{link_tag['href']}"
                title = link_tag.find('span', class_='highwire-cite-title').get_text(strip=True)
            else:
                continue

            # 摘要
            summary_tag = article.find('div', class_='highwire-cite-snippet')
            summary = summary_tag.get_text(strip=True) if summary_tag else "No summary available"

            # 发布日期
            date_tag = article.find('span', class_='highwire-cite-metadata-date')
            date_published = date_tag.get_text(strip=True) if date_tag else "No date available"

            papers.append((title, link, summary, date_published))

        return papers

    except Exception as e:
        print(f"❌ 抓取第 {page_number} 页出错: {e}")
        return []


def fetch_biorxiv():
    try:
        if is_cached('biorxiv'):
            return load_cache('biorxiv')

        papers = []
        page_number = 1

        while True:
            print(f"🚀 开始抓取第 {page_number} 页到第 {page_number + BATCH_SIZE - 1} 页")

            batch_results = []
            stop_flag = False

            # 使用 ThreadPoolExecutor 进行并行抓取
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                future_to_page = {
                    executor.submit(fetch_page_biorxiv, page): page
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
                        print(f"❌ 抓取第 {page} 页失败: {e}")

            # 合并当前批次结果
            papers.extend(batch_results)

            if stop_flag or page_number + BATCH_SIZE > MAX_PAGES:
                print("✅ 抓取完成！")
                break

            # 更新下一批抓取的起点
            page_number += BATCH_SIZE

        # 保存结果（缓存）
        save_cache('biorxiv', papers)
        return papers

    except Exception as e:
        print(f"❌ Error fetching biorxiv: {e}")
        return [(f"Error fetching biorxiv: {str(e)}", "", "", "")]


# 调用函数
if __name__ == "__main__":
    start_time = time.time()
    papers = fetch_biorxiv()
    end_time = time.time()
    print(f"✅ 抓取完成，共 {len(papers)} 篇文章，耗时 {end_time - start_time:.2f} 秒")

    # 打印前 5 条记录
    for paper in papers[:5]:
        print(f"📌 标题: {paper[0]}\n🔗 链接: {paper[1]}\n📄 摘要: {paper[2]}\n📅 日期: {paper[3]}\n{'-'*50}")




assert(0)


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