import requests
from bs4 import BeautifulSoup
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


#==处理arxiv
def fetch_arxiv():
    try:
        if is_cached('arxiv'):
            return load_cache('arxiv')

        url = "https://arxiv.org/list/cs.AI/recent"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        papers = []
        # 找到所有 dt 标签
        articles = soup.find_all('dt')
        for article in articles:
            # 提取文章链接
            link = f"https://arxiv.org{article.find('a', title='Abstract')['href']}"
            
            # 举例，这是pdf的地址 https://arxiv.org/pdf/2503.10542
            #这是大纲页面的地址 https://arxiv.org/abs/2503.10542
            # 找到对应的 dd 标签
            details = article.find_next_sibling('dd')
            
            if details:
                # 提取标题
                title = details.find('div', class_='list-title').get_text(strip=True).replace('Title:', '').strip()
                
                # 提取作者
                authors = [a.get_text(strip=True) for a in details.find('div', class_='list-authors').find_all('a')]
                
                # 提取主题
                subjects = details.find('div', class_='list-subjects').get_text(strip=True).replace('Subjects:', '').strip()
                papers.append((title,link))
        #debug
        # print(papers)
        
        save_cache('arxiv', papers)
        return papers
    except Exception as e:
        return [(f"Error fetching ArXiv: {str(e)}", "")]
    

def fetch_huggingface():
    try:
        if is_cached('huggingface'):
            return load_cache('huggingface')
        url = "https://huggingface.co/blog"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        papers = []
        for entry in soup.find_all('h2'):
            title = entry.get_text(strip=True)
            link = entry.find_next('a')['href'] if entry.find_next('a') else ""
            papers.append((title, link))
        save_cache('huggingface', papers)
        return papers
        
    except Exception as e:
        return [(f"Error fetching HuggingFace: {str(e)}", "")]


#===处理 bioarxiv系列期刊 ===
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_biorxiv_medrxiv(flag):
    try:
        if flag=='bio':

            if is_cached('biorxiv'):
                return load_cache('biorxiv')
        elif flag == 'med':
            if is_cached('medrxiv'):
                return load_cache('medrxiv')          

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
            if flag=='bio':
                url = f"https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/{offset}"
            elif flag == 'med':
                url = f"https://api.biorxiv.org/details/medrxiv/{start_date}/{end_date}/{offset}"
            response = requests.get(url)
            data = response.json()

            # Process the papers in the current batch
            batch_papers = []
            collection = data.get('collection', [])
            for item in collection:
                # Extract the DOI
                doi = item.get('doi', 'N/A')
                if flag=='bio':
                    link = f"https://www.biorxiv.org/content/{doi}"
                elif flag == 'med':
                    link = f"https://www.medrxiv.org/content/{doi}"

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
                print(f"We are now processing the {offset} papers")
                # Wait for all threads to finish
                for future in as_completed(futures):
                    papers.extend(future.result())

                # If no more papers are fetched, break the loop
                if len(futures) < max_threads or len(futures[-1].result()) == 0:
                    break

        # Save the result to cache

        if flag=='bio':
            save_cache('biorxiv', papers)
        elif flag == 'med':
            save_cache('medrxiv', papers)
        
        return papers

    except Exception as e:
        return [(f"Error fetching bioRxiv/medRxiv: {str(e)}", "")]