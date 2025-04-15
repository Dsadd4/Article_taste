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


# 每批抓取 10 页，每次启动 10 个线程
BATCH_SIZE = 20
MAX_THREADS = 20
MAX_PAGES = 100  # 最多抓100页，防止无限爬取


#==处理arxiv
def fetch_arxiv():
    url = "https://arxiv.org/list/cs.AI/recent"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    papers = []
    for entry in soup.find_all('div', class_='list-title'):
        title = entry.get_text(strip=True)
        papers.append(title)
    
    return papers






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






