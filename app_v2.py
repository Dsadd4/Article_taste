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

# === MODULES ===


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
    

import requests
from bs4 import BeautifulSoup

def fetch_nature_biotechnology():
    try:
        if is_cached('nature_biotechnology'):
            return load_cache('nature_biotechnology')

        papers = []
        page_number = 1  # 从第一页开始

        while True:
            url = f"https://www.nature.com/nbt/articles?searchType=journalSearch&sort=PubDate&year=2025&page={page_number}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 找到所有文章的 li 标签
            articles = soup.find_all('li', class_='app-article-list-row__item')

            if not articles:
                break  # 如果当前页面没有文章，说明所有页面都抓取完了

            for article in articles:
                link_tag = article.find('a', class_='c-card__link u-link-inherit')
                if link_tag and 'href' in link_tag.attrs:
                    link = f"https://www.nature.com{link_tag['href']}"
                else:
                    print("Link format not as expected, skipping article.")
                    continue

                title = article.find('a', class_='c-card__link u-link-inherit').get_text(strip=True)

                # 可选：提取摘要
                summary = article.find('div', class_='c-card__summary')
                if summary:
                    p_tag = summary.find('p')
                    summary_text = p_tag.get_text(strip=True) if p_tag else "No summary available"
                else:
                    summary_text = "No summary available"

                # 提取发布日期
                date_published = article.find('time', class_="c-meta__item c-meta__item--block-at-lg").get_text(strip=True)

                papers.append((title, link, summary_text, date_published))

            page_number += 1  # 访问下一页

        save_cache('nature_biotechnology', papers)
        return papers

    except Exception as e:
        return [(f"Error fetching Nature Biotechnology: {str(e)}", "", "", "")]

import requests
from bs4 import BeautifulSoup

# 映射 journal_name 到期刊缩写
JOURNAL_MAPPING = {
    'nature_biotechnology': 'nbt',
    'nature_methods': 'nmeth',
    'nature_machine_intelligence': 'natmachintell',
    'nature': 'nature',
    'nature_computer_science': 'natcomputsci',
    'nature_communications': 'ncomms'
}

def fetch_nature_series(journal_name):
    try:
        if is_cached(journal_name):
            return load_cache(journal_name)

        if journal_name not in JOURNAL_MAPPING:
            raise ValueError(f"Unsupported journal name: {journal_name}")

        papers = []
        page_number = 1  # 从第一页开始

        journal_abbr = JOURNAL_MAPPING[journal_name]  # 根据 journal_name 获取对应的缩写

        while True:
            url = f"https://www.nature.com/{journal_abbr}/articles?searchType=journalSearch&sort=PubDate&year=2025&page={page_number}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 找到所有文章的 li 标签
            articles = soup.find_all('li', class_='app-article-list-row__item')

            if not articles:
                break  # 如果当前页面没有文章，说明所有页面都抓取完了

            for article in articles:
                link_tag = article.find('a', class_='c-card__link u-link-inherit')
                if link_tag and 'href' in link_tag.attrs:
                    link = f"https://www.nature.com{link_tag['href']}"
                else:
                    print("Link format not as expected, skipping article.")
                    continue

                title = article.find('a', class_='c-card__link u-link-inherit').get_text(strip=True)

                # 可选：提取摘要
                summary = article.find('div', class_='c-card__summary')
                if summary:
                    p_tag = summary.find('p')
                    summary_text = p_tag.get_text(strip=True) if p_tag else "No summary available"
                else:
                    summary_text = "No summary available"

                # 提取发布日期
                date_published = article.find('time', class_="c-meta__item c-meta__item--block-at-lg").get_text(strip=True)

                papers.append((title, link, summary_text, date_published))

            page_number += 1  # 访问下一页

        save_cache(journal_name, papers)
        return papers

    except Exception as e:
        return [(f"Error fetching {journal_name}: {str(e)}", "", "", "")]



    




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


from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import Qt
# === GUI ===
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("科研信息抓取助手")
        self.setGeometry(100, 100, 1200, 1200)

        layout = QVBoxLayout()

        # Buttons
        self.arxiv_button = QPushButton("ArXiv")
        self.arxiv_button.clicked.connect(lambda: self.show_results(fetch_arxiv()))
        layout.addWidget(self.arxiv_button)

        self.huggingface_button = QPushButton("HuggingFace")
        self.huggingface_button.clicked.connect(lambda: self.show_results(fetch_huggingface()))
        layout.addWidget(self.huggingface_button)


        #fetch_nature_biotechnology():
        self.nbt_button = QPushButton("Nature biotechnology")
        self.nbt_button.clicked.connect(lambda: self.show_results(fetch_nature_biotechnology()))
        layout.addWidget(self.nbt_button)

        # fetch_nature_methods:
        self.nmeth_button = QPushButton("Nature methods")
        self.nmeth_button.clicked.connect(lambda: self.show_results(fetch_nature_series('nature_methods')))
        layout.addWidget(self.nmeth_button)

        # fetch_nature_machine_intelligence:
        self.nmachintell_button = QPushButton("Nature machine intelligence")
        self.nmachintell_button.clicked.connect(lambda: self.show_results(fetch_nature_series('nature_machine_intelligence')))
        layout.addWidget(self.nmachintell_button)

        # fetch_nature:
        self.nature_button = QPushButton("Nature")
        self.nature_button.clicked.connect(lambda: self.show_results(fetch_nature_series('nature')))
        layout.addWidget(self.nature_button)

        # fetch_nature_computer_science:
        self.ncomputersci_button = QPushButton("Nature computer science")
        self.ncomputersci_button.clicked.connect(lambda: self.show_results(fetch_nature_series('nature_computer_science')))
        layout.addWidget(self.ncomputersci_button)

        # fetch_nature_communications:
        self.ncomms_button = QPushButton("Nature communications")
        self.ncomms_button.clicked.connect(lambda: self.show_results(fetch_nature_series('nature_communications')))
        layout.addWidget(self.ncomms_button)


        self.download_button = QPushButton("Download_papers_withhighlight")
        self.download_button.clicked.connect(self.download)
        layout.addWidget(self.download_button)


        self.update_button = QPushButton("更新")
        self.update_button.clicked.connect(self.clear_cache)
        layout.addWidget(self.update_button)

        # Scrollable area for displaying results
        self.result_area = QScrollArea()
        self.result_label = QLabel("点击按钮获取最新信息")
        self.result_label.setStyleSheet("font-size: 16px;")
        self.result_label.setTextFormat(Qt.RichText)  # 允许解析 HTML 格式
        self.result_label.setOpenExternalLinks(True)  # 允许点击外部链接
        self.result_label.setTextInteractionFlags(Qt.TextBrowserInteraction)  # 允许点击和选择文本


        self.result_area.setWidget(self.result_label)
        self.result_area.setWidgetResizable(True)
        layout.addWidget(self.result_area)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # # 假设你有一个CONFIG字典包含期刊和关键词等配置
        # self.CONFIG = {
        #     "arxiv": {"fields": 2, "keywords": ["AI", "Machine Learning"]},  # arxiv只抓取2项
        #     "nbt": {"fields": 4, "keywords": ["Gene", "DNA", "Lipids"]},     # nbt抓取4项
        #     # 其他期刊的配置
        # }

    def show_results(self, results):
        highlighted_results = []
        
        if(len(results[0])==2):
            for title, link in results:
                title = insert_changeline(title)
                if any(keyword.lower() in title.lower() for keyword in CONFIG["keywords"]):
                    result_html = f'<b><a href="{link}" target="_blank" style="color:red;font-size:20px;">{title}</a></b>'
                else:
                    result_html = f'<a href="{link}" target="_blank" style="color:black;font-size:16px;">{title}</a>'
                
                highlighted_results.append(result_html)
        elif(len(results[0])==4):
            for title, link,__,___ in results:
                title = insert_changeline(title)
                if any(keyword.lower() in title.lower() for keyword in CONFIG["keywords"]):
                    result_html = f'<b><a href="{link}" target="_blank" style="color:red;font-size:20px;">{title}</a></b>'
                else:
                    result_html = f'<a href="{link}" target="_blank" style="color:black;font-size:16px;">{title}</a>'
                
                highlighted_results.append(result_html)

        self.result_label.setText("<br><br>".join(highlighted_results))

    

    def clear_cache(self):
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        self.result_label.setText("缓存已清除！")



    def download(self):
        self.result_label.setText("begin...")
        papers = fetch_arxiv()
        keywords = [kw.lower() for kw in CONFIG["keywords"]]
        
        matched_papers = [(title, link) for title, link in papers if any(kw in title.lower() for kw in keywords)]
        
        print(f"🔍 Found {len(matched_papers)} matching papers")
        
        # 为每篇论文启动一个下载线程
        self.threads = []  # 保存所有的下载线程，以便管理它们
        for title, link in matched_papers:
            download_thread = DownloadThread(title, link)
            download_thread.download_done.connect(self.on_download_done)
            download_thread.start()
            self.threads.append(download_thread)

    def on_download_done(self, message):
        # 每当一个下载完成后调用这个方法
        print(message)  # 打印下载完成的信息，可以更新 UI 来显示

        # 这里可以更新界面，显示下载的进度或完成情况
        self.result_label.setText(message)

    def closeEvent(self, event):
        """确保在应用退出时，所有线程被正确终止"""
        for thread in self.threads:
            thread.terminate()
            thread.wait()
        event.accept()


# === utils ====
def insert_changeline(title):
    setlens = 88
    for i in range(setlens,len(title),setlens):
        title= title[:i]+'<br>'+title[i:]
    return title

from PyQt5.QtCore import QThread, pyqtSignal

class DownloadThread(QThread):
    # 定义一个信号，用于通知下载完成
    download_done = pyqtSignal(str)  # 传递文件名或其他信息

    def __init__(self, title, link, parent=None):
        super().__init__(parent)
        self.title = title
        self.link = link

    def run(self):
        try:
            # 执行下载任务
            download_pdf(self.title, self.link)
            # 下载完成后发出信号
            self.download_done.emit(f"{self.title} 下载完成")
        except Exception as e:
            self.download_done.emit(f"下载失败: {self.title}， 错误: {str(e)}")

    def stop(self):
        """如果需要停止线程，添加一个停止方法"""
        self.terminate()
        self.wait()



# === SYSTEM TRAY ===

def setup(icon):
    icon.visible = True

def run_tray():
    icon = Icon("科研助手", Image.open("icon.png"), menu=Menu(
        MenuItem('显示', lambda icon, item: print("显示窗口")),
        MenuItem('退出', lambda icon, item: icon.stop())
    ))
    icon.run(setup)

# === SCHEDULER ===
def job():
    papers_arxiv = fetch_arxiv()
    papers_hf = fetch_huggingface()
    print("[Arxiv]:", papers_arxiv)
    print("[HuggingFace]:", papers_hf)

schedule.every().day.at("09:00").do(job)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# === AUTO STARTUP ===
def create_shortcut():
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    shortcut_path = os.path.join(startup_folder, '科研助手.lnk')

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = sys.executable
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.Save()

# === MAIN ===
def main():
    create_shortcut()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    import threading
    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=run_tray, daemon=True).start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
