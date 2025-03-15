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




import concurrent.futures
import requests
from bs4 import BeautifulSoup


# 每批抓取 10 页，每次启动 10 个线程
BATCH_SIZE = 20
MAX_THREADS = 20
MAX_PAGES = 100  # 最多抓100页，防止无限爬取

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

import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QScrollArea, QWidget, QMenu, QAction, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMenu, QAction, QVBoxLayout, QWidget, QPushButton, QTextBrowser, QMainWindow
from PyQt5.QtCore import Qt


FAVORITES_FILE = 'favorites.json'
# === GUI ===
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Article_taste")
        self.setGeometry(100, 100, 1200, 1200)
        self.favorites = self.load_favorites()
        layout = QVBoxLayout()

        # Buttons

        # 创建arxiv与关键信息网站
        self.arxiv_button = QPushButton("ArXiv")
        self.arxiv_button.clicked.connect(lambda: self.start_fetch_arxiv())
        layout.addWidget(self.arxiv_button)

        self.huggingface_button = QPushButton("HuggingFace")
        self.huggingface_button.clicked.connect(lambda: self.start_fetch_huggingface())
        layout.addWidget(self.huggingface_button)


        # 创建nature系列按钮
        self.nbt_button = QPushButton("Nature Biotechnology")
        self.nbt_button.clicked.connect(lambda: self.start_fetch('nature_biotechnology'))
        layout.addWidget(self.nbt_button)

        self.nmeth_button = QPushButton("Nature Methods")
        self.nmeth_button.clicked.connect(lambda: self.start_fetch('nature_methods'))
        layout.addWidget(self.nmeth_button)

        self.nmachintell_button = QPushButton("Nature Machine Intelligence")
        self.nmachintell_button.clicked.connect(lambda: self.start_fetch('nature_machine_intelligence'))
        layout.addWidget(self.nmachintell_button)

        self.nature_button = QPushButton("Nature")
        self.nature_button.clicked.connect(lambda: self.start_fetch('nature'))
        layout.addWidget(self.nature_button)

        self.ncomputersci_button = QPushButton("Nature Computer Science")
        self.ncomputersci_button.clicked.connect(lambda: self.start_fetch('nature_computer_science'))
        layout.addWidget(self.ncomputersci_button)

        self.ncomms_button = QPushButton("Nature Communications")
        self.ncomms_button.clicked.connect(lambda: self.start_fetch('nature_communications'))
        layout.addWidget(self.ncomms_button)


        self.download_button = QPushButton("Download_papers_withhighlight")
        self.download_button.clicked.connect(self.download)
        layout.addWidget(self.download_button)


        self.update_button = QPushButton("更新")
        self.update_button.clicked.connect(self.clear_cache)
        layout.addWidget(self.update_button)


        # ❤️ 收藏夹按钮
        self.favorites_button = QPushButton("📁 查看收藏夹")
        self.favorites_button.clicked.connect(self.show_favorites)
        layout.addWidget(self.favorites_button)


    

                # 结果展示区域
        self.result_area = QTextBrowser()
        self.result_area.setOpenExternalLinks(True)
        self.result_area.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.result_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.result_area.customContextMenuRequested.connect(self.show_context_menu)

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

        # ✅ 右键菜单（用于添加到收藏夹）
    def show_context_menu(self, pos):
        print("右键菜单事件触发")
        menu = QMenu(self)

        add_fav_action = QAction("添加到收藏夹", self)
        add_fav_action.triggered.connect(self.add_to_favorites)
        menu.addAction(add_fav_action)

        # 获取鼠标位置对应的文章链接和标题
        link, title = self.get_link_and_title_under_cursor(pos)
        print(f"链接: {link}, 标题: {title}")  # 打印查看获取的链接和标题

        if link and title:
            self.current_link = link
            self.current_title = title
            menu.exec_(self.result_area.mapToGlobal(pos))
        else:
            self.current_link = None
            self.current_title = None

    def get_link_and_title_under_cursor(self, pos):
        # 获取鼠标所在位置的光标
        cursor = self.result_area.cursorForPosition(pos)
        cursor.select(cursor.WordUnderCursor)
        selected_text = cursor.selectedText()

        # 获取所有链接和对应的标题
        link_pattern = r'href="(.*?)"'
        title_pattern = r'>(.*?)</a>'
        links = re.findall(link_pattern, self.result_area.toHtml())
        titles = re.findall(title_pattern, self.result_area.toHtml())

        # 调试输出
        # print(f"选中的文本: {selected_text}")
        # print(f"提取的链接: {links}")
        # print(f"提取的标题: {titles}")

        # 遍历链接和标题
        for title, link in zip(titles, links):
            # 如果选中的文本与标题匹配，则返回对应的链接
            if selected_text and selected_text in title:
                return link, title

        return None, None
    
    def add_to_favorites(self):
        if self.current_link and self.current_title:
            # 存储到收藏夹中
            if (self.current_title, self.current_link) not in self.favorites:
                self.favorites.append((self.current_title, self.current_link))
                self.save_favorites()
                print(f"✅ 已收藏: {self.current_title}")
            else:
                print(f"⚠️ 已经收藏过了: {self.current_title}")
                
            
        # ✅ 显示收藏夹内容
    def show_favorites(self):
        if not self.favorites:
            self.result_area.setText("❤️ 收藏夹为空")
        else:
            favorites_html = []
            for title, link in self.favorites:
                favorites_html.append(f'<a href="{link}" target="_blank" style="color:blue;font-size:16px;">{title}</a>')
            self.result_area.setHtml("<br><br>".join(favorites_html))

    # ✅ 加载收藏夹
    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    # ✅ 保存收藏夹
    def save_favorites(self):
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, indent=4, ensure_ascii=False)


    def show_results(self, results):
        highlighted_results = []
        
        if len(results[0]) == 2:  # 处理标题和链接
            for title, link in results:
                title = insert_changeline(title)
                if any(keyword.lower() in title.lower() for keyword in CONFIG["keywords"]):
                    result_html = f'<b><a href="{link}" target="_blank" style="color:red;font-size:20px;">{title}</a></b>'
                else:
                    result_html = f'<a href="{link}" target="_blank" style="color:black;font-size:16px;">{title}</a>'
                
                highlighted_results.append(result_html)
        
        elif len(results[0]) == 4:  # 处理包含四个元素的数据
            for title, link, __, ___ in results:
                title = insert_changeline(title)
                if any(keyword.lower() in title.lower() for keyword in CONFIG["keywords"]):
                    result_html = f'<b><a href="{link}" target="_blank" style="color:red;font-size:20px;">{title}</a></b>'
                else:
                    result_html = f'<a href="{link}" target="_blank" style="color:black;font-size:16px;">{title}</a>'
                
                highlighted_results.append(result_html)
        
        # 假设使用 QTextBrowser 来显示 HTML
        self.result_area.setHtml("<br><br>".join(highlighted_results))

    

    def clear_cache(self):
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        self.result_area.setText("缓存已清除！")



    def download(self):
        self.result_area.setText("begin...")
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
        self.result_area.setText(message)

    def closeEvent(self, event):
        """确保在应用退出时，所有线程被正确终止"""
        # for thread in self.threads:
        #     thread.terminate()
        #     thread.wait()
        self.save_favorites()
        
        event.accept()
    

    def start_fetch(self, journal_name):
        self.thread = FetchNatureThread(journal_name)  
        self.thread.result_signal.connect(self.show_results)  # 绑定信号到回调函数
        self.thread.start()  # 启动线程

    def start_fetch_arxiv(self):
        self.thread = FetcharxivThread()  
        self.thread.result_signal.connect(self.show_results)  # 绑定信号到回调函数
        self.thread.start()  # 启动线程

    def start_fetch_huggingface(self):
        self.thread = FethuggingfaceThread()  
        self.thread.result_signal.connect(self.show_results)  # 绑定信号到回调函数
        self.thread.start()  # 启动线程

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




from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

class FetchNatureThread(QThread):
    result_signal = pyqtSignal(list)  # 定义信号，传递抓取结果

    def __init__(self, journal_name):
        super().__init__()
        self.journal_name = journal_name

    def run(self):
        try:
            # 调用 fetch_nature_series 抓取数据
            result = fetch_nature_series(self.journal_name)
            self.result_signal.emit(result)  # 发送信号，将结果传回主线程
        except Exception as e:
            self.result_signal.emit([(f"Error fetching {self.journal_name}: {str(e)}", "", "", "")])


class FetcharxivThread(QThread):
    result_signal = pyqtSignal(list)  # 定义信号，传递抓取结果

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            # 调用 fetch_nature_series 抓取数据
            result = fetch_arxiv()
            self.result_signal.emit(result)  # 发送信号，将结果传回主线程
        except Exception as e:
            self.result_signal.emit([(f"Error fetching {self.journal_name}: {str(e)}", "", "", "")])

class FethuggingfaceThread(QThread):
    result_signal = pyqtSignal(list)  # 定义信号，传递抓取结果

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            # 调用 fetch_nature_series 抓取数据
            result = fetch_huggingface()
            self.result_signal.emit(result)  # 发送信号，将结果传回主线程
        except Exception as e:
            self.result_signal.emit([(f"Error fetching {self.journal_name}: {str(e)}", "", "", "")])


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
