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


# === MODULES ===
from modules.xiv_scrath import fetch_arxiv, fetch_biorxiv_medrxiv,fetch_huggingface
from modules.nature_series import fetch_nature_series,download_pdf
from modules.science_series import fetch_science

from utils.functions import generate_wordclouds


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



FAVORITES_FILE = 'favorites.json'

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
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
import io
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import matplotlib.pyplot as plt
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QBuffer, QIODevice
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QScrollArea, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QScrollArea, QWidget, QTextBrowser
import webbrowser
from threading import Lock
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtGui import QIcon  


from utils.functions import generate_citation_plot,generate_github_stars_plot,generate_source_distribution
# === GUI ===
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
       

        self.setWindowTitle("Article_taste")
        # 设置窗口图标
        self.setWindowIcon(QIcon('achat.png')) 
        self.setGeometry(100, 100, 2000, 1200)
        self.favorites = self.load_favorites()



         # 创建主布局
        main_layout = QHBoxLayout()  

        #layout默认在左边
        layout = QVBoxLayout()

        # Buttons
        # 创建arxiv与关键信息网站
        self.arxiv_lock = Lock()
        self.arxiv_button = QPushButton("ArXiv")
        self.arxiv_button.clicked.connect(lambda: self.start_fetch_arxiv())
        
        layout.addWidget(self.arxiv_button)

        # self.huggingface_button = QPushButton("HuggingFace")
        # self.huggingface_button.clicked.connect(lambda: self.start_fetch_huggingface())
        # layout.addWidget(self.huggingface_button)


        # 创建nature系列按钮
        self.nbt_lock = Lock()
        self.nbt_button = QPushButton("Nature Biotechnology")
        self.nbt_button.clicked.connect(lambda: self.start_fetch('nature_biotechnology'))
        layout.addWidget(self.nbt_button)

        self.nmd_lock = Lock()
        self.nmeth_button = QPushButton("Nature Methods")
        self.nmeth_button.clicked.connect(lambda: self.start_fetch('nature_methods'))
        layout.addWidget(self.nmeth_button)

        self.nmachinetell_lock = Lock()
        self.nmachintell_button = QPushButton("Nature Machine Intelligence")
        self.nmachintell_button.clicked.connect(lambda: self.start_fetch('nature_machine_intelligence'))
        layout.addWidget(self.nmachintell_button)

        self.na_lock = Lock()
        self.nature_button = QPushButton("Nature")
        self.nature_button.clicked.connect(lambda: self.start_fetch('nature'))
        layout.addWidget(self.nature_button)

        self.ncomputersci_lock = Lock()
        self.ncomputersci_button = QPushButton("Nature Computer Science")
        self.ncomputersci_button.clicked.connect(lambda: self.start_fetch('nature_computer_science'))
        layout.addWidget(self.ncomputersci_button)

        self.ncomms_lock = Lock()
        self.ncomms_button = QPushButton("Nature Communications")
        self.ncomms_button.clicked.connect(lambda: self.start_fetch('nature_communications'))
        layout.addWidget(self.ncomms_button)


        #bioarxiv
        self.bioarxiv_lock = Lock()
        self.bioarxiv_button = QPushButton("Bioarxiv")
        self.bioarxiv_button.clicked.connect(lambda: self.start_fetch_bioarxiv())
        layout.addWidget(self.bioarxiv_button)
        
        #medarxiv
        self.medarxiv_lock = Lock()
        self.medarxiv_button = QPushButton("Medarxiv")
        self.medarxiv_button.clicked.connect(lambda: self.start_fetch_medarxiv())
        layout.addWidget(self.medarxiv_button)

        self.download_button = QPushButton("Download_papers_withhighlight")
        self.download_button.clicked.connect(self.download)
        layout.addWidget(self.download_button)

        #science
        self.science_lock = Lock()
        self.science_button = QPushButton("Science")
        self.science_button.clicked.connect(lambda: self.start_fetch_science())
        layout.addWidget(self.science_button)

        #cell
        self.cell_lock = Lock()
        self.cell_button = QPushButton("Cell")
        self.cell_button.clicked.connect(lambda: self.start_fetch_cell())
        layout.addWidget(self.cell_button)

        #github
        self.github_lock = Lock()  # 添加锁
        self.github_button = QPushButton("GitHub Search")
        self.github_button.clicked.connect(self.start_fetch_github)
        layout.addWidget(self.github_button)


        #scholar
        self.scholar_lock = Lock()
        self.scholar_button = QPushButton("Google Scholar")
        self.scholar_button.clicked.connect(self.start_fetch_scholar)
        layout.addWidget(self.scholar_button)



        self.update_button = QPushButton("更新")
        self.update_button.clicked.connect(self.clear_cache)
        layout.addWidget(self.update_button)


        # ❤️ 收藏夹按钮
        self.favorites_button = QPushButton("📁 查看收藏夹")
        self.favorites_button.clicked.connect(self.show_favorites)
        layout.addWidget(self.favorites_button)

        # 🔥 新按钮触发词云生成

        self.wordcloud_button = QPushButton("生成词云")
        self.wordcloud_button.clicked.connect(self.start_generate_wordcloud)
        layout.addWidget(self.wordcloud_button)

        # 添加可视化按钮
        self.vis_lock = Lock()  # 添加可视化锁
        self.visualization_button = QPushButton("引用量分布")
        self.visualization_button.clicked.connect(self.show_citations_plot)
        layout.addWidget(self.visualization_button)
    
        self.github_vis_button = QPushButton("GitHub Stars分布")
        self.github_vis_button.clicked.connect(self.show_github_plot)
        layout.addWidget(self.github_vis_button)
    
        self.source_vis_button = QPushButton("文章来源分布")
        self.source_vis_button.clicked.connect(self.show_source_distribution)
        layout.addWidget(self.source_vis_button)


        # 结果展示区域
        self.result_area = QTextBrowser()
        self.result_area.setOpenExternalLinks(True)
        self.result_area.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.result_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.result_area.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.result_area)
   
        
        # 创建调试信息显示区域
        self.debug_area = QTextBrowser()
        self.debug_area.setMaximumHeight(150)  # 限制高度
                # 在 __init__ 中设置调试区域样式
        self.debug_area.setStyleSheet("""
            QTextBrowser {
                background-color: #2b2b2b;
                color: #a9b7c6;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
                border: 1px solid #555;
            }
        """)
        layout.addWidget(self.debug_area)
                # 设置输出重定向
        self.output_redirector = OutputRedirector()
        self.output_redirector.outputWritten.connect(self.append_debug_output)
        sys.stdout = self.output_redirector
        
        
        
        # 创建 QGraphicsView 和 QGraphicsScene
        self.graphics_view = QGraphicsView(self)
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)

        self.graphics_view.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform)  # 平滑缩放

        # 创建 QScrollArea 并设置 QGraphicsView
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.graphics_view)
        

        # 添加左侧布局到主布局
        main_layout.addLayout(layout)
        # 添加右侧的 scroll_area 到主布局
        main_layout.addWidget(self.scroll_area)




        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    #可视化函数
    def show_plot(self, file_path):
        """通用显示图表方法"""
        pixmap = QPixmap(file_path)
        pixmap = pixmap.scaled(1800, 1200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.graphics_scene.clear()
        self.graphics_scene.addItem(pixmap_item)

    def show_citations_plot(self):
        if self.vis_lock.locked():
            print("可视化正在进行中，请稍后...")
            return
            
        self.vis_lock.acquire()
        print("正在生成引用量分布图...")
        
        def on_vis_complete(file_path):
            if file_path and os.path.exists(file_path):
                self.show_plot(file_path)
            print("引用量分布图生成完成！")
            self.vis_lock.release()
        
        self.vis_thread = VisualizationThread('citations')
        self.vis_thread.finished.connect(on_vis_complete)
        self.vis_thread.start()

    def show_github_plot(self):
        if self.vis_lock.locked():
            print("可视化正在进行中，请稍后...")
            return
            
        self.vis_lock.acquire()
        print("正在生成GitHub Stars分布图...")
        
        def on_vis_complete(file_path):
            if file_path and os.path.exists(file_path):
                self.show_plot(file_path)
            print("GitHub Stars分布图生成完成！")
            self.vis_lock.release()
        
        self.vis_thread = VisualizationThread('github')
        self.vis_thread.finished.connect(on_vis_complete)
        self.vis_thread.start()

    def show_source_distribution(self):
        if self.vis_lock.locked():
            print("可视化正在进行中，请稍后...")
            return
            
        self.vis_lock.acquire()
        print("正在生成文章来源分布图...")
        
        def on_vis_complete(file_path):
            if file_path and os.path.exists(file_path):
                self.show_plot(file_path)
            print("文章来源分布图生成完成！")
            self.vis_lock.release()
        
        self.vis_thread = VisualizationThread('source')
        self.vis_thread.finished.connect(on_vis_complete)
        self.vis_thread.start()

    # 在 MainWindow 类中添加方法
    def start_fetch_scholar(self):
        if self.scholar_lock.locked():
            print("Scholar 搜索正在进行中，请稍后")
            return
            
        # 创建输入对话框
        keywords, ok = QInputDialog.getText(
            self, 
            'Google Scholar Search', 
            'Enter keywords (separate multiple keywords with comma):'
        )
        
        if ok and keywords:
            self.scholar_lock.acquire()
            keywords_list = [k.strip() for k in keywords.split(',')]
            print(f"开始搜索 Scholar: {keywords_list}")
            
            def on_fetch_complete(results):
                self.show_scholar_results(results)  # 使用新的显示函数
                print("Scholar 搜索完成！")
                self.scholar_lock.release()
            
            self.thread = FetchScholarThread(keywords_list)
            self.thread.result_signal.connect(on_fetch_complete)
            self.thread.start()

    def show_scholar_results(self, results):
        highlighted_results = []
        
        for title, link, author_venue, citations in results:
            title = insert_changeline(title)
            # 创建带有引用数和作者信息的HTML
            if any(keyword.lower() in title.lower() for keyword in CONFIG["keywords"]):
                result_html = f'''
                    <div style="margin-bottom: 10px">
                        <b><a href="{link}" target="_blank" style="color:red;font-size:20px;">{title}</a></b>
                        <br>
                        <span style="color:#666;font-size:14px">{author_venue}</span>
                        <br>
                        <span style="color:#009688;font-size:14px">引用数: {citations}</span>
                    </div>
                '''
            else:
                result_html = f'''
                    <div style="margin-bottom: 10px">
                        <a href="{link}" target="_blank" style="color:black;font-size:16px;">{title}</a>
                        <br>
                        <span style="color:#666;font-size:14px">{author_venue}</span>
                        <br>
                        <span style="color:#009688;font-size:14px">引用数: {citations}</span>
                    </div>
                '''
            
            highlighted_results.append(result_html)
        
        self.result_area.setHtml("<br>".join(highlighted_results))






    def append_debug_output(self, text):
        self.debug_area.append(text.strip())
        # 自动滚动到底部
        self.debug_area.verticalScrollBar().setValue(
            self.debug_area.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        # 恢复标准输出
        sys.stdout = sys.__stdout__
        # ...existing closeEvent code...

    def wheelEvent(self, event):
        """实现缩放功能"""
        # 获取当前缩放因子
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        
        # 对 QGraphicsView 进行缩放
        # self.graphics_view.scale(factor, factor)

    def start_generate_wordcloud(self):
        print("正在生成词云，请稍候...")  # 显示提示信息
        self.wordcloud_thread = WordCloudThread(set_column=3)
        self.wordcloud_thread.finished.connect(self.on_wordcloud_finished)
        self.wordcloud_thread.start()

    def on_wordcloud_finished(self, file_path):
        if file_path and os.path.exists(file_path):
            # 加载图片
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(1800, 1200,transformMode=Qt.SmoothTransformation)
            # 将图片添加到 QGraphicsScene
            pixmap_item = QGraphicsPixmapItem(pixmap)
            self.graphics_scene.clear()  # 清除旧的图形项
            self.graphics_scene.addItem(pixmap_item)



    
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
        # print(len(results[0]))

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

    
    def git_results(self, results):
        highlighted_results = []
        # print(len(results[0]))

        # Title,link,stars = zip(*results)
    
        for title, link,stars in results:
            title = insert_changeline(title)
            if any(keyword.lower() in title.lower() for keyword in CONFIG["keywords"]):
                result_html = f'<b><a href="{link}" target="_blank" style="color:red;font-size:20px;">{title} stars:{stars}</a></b>'
            else:
                result_html = f'<a href="{link}" target="_blank" style="color:black;font-size:16px;">{title} stars:{stars}</a>'
            
            highlighted_results.append(result_html)
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
    

    # github
    def start_fetch_github(self):
        if self.github_lock.locked():
            print("GitHub 搜索正在进行中，请稍后")
            return
            
        # 创建输入对话框
        keyword, ok = QInputDialog.getText(
            self, 
            'GitHub Search', 
            'Enter keyword:'
        )
        
        if ok and keyword:
            self.github_lock.acquire()
            print(f"开始搜索 GitHub: {keyword}")
            
            def on_fetch_complete(results):
                self.git_results(results)  # 使用专门的 git_results 方法显示
                print("GitHub 搜索完成！")
                self.github_lock.release()
            
            self.thread = FetchgithubThread(keyword)
            self.thread.result_signal.connect(on_fetch_complete)
            self.thread.start()

    def start_fetch_bioarxiv(self):
        if self.bioarxiv_lock.locked():
            print("bioarxiv 抓取正在进行中，请稍后")
            return
            
        self.bioarxiv_lock.acquire()
        print("开始抓取bioarxiv数据...")
        
        def on_fetch_complete(results):
            self.show_results(results)
            print("bioarxiv 抓取完成！")
            self.bioarxiv_lock.release()
        
        self.thread = FetchbioarxivThread()
        self.thread.result_signal.connect(on_fetch_complete)
        self.thread.start()


    def start_fetch(self, journal_name):
        # 创建 journal_name 到对应 lock 的映射
        lock_mapping = {
            'nature_biotechnology': self.nbt_lock,
            'nature_methods': self.nmd_lock,
            'nature_machine_intelligence': self.nmachinetell_lock,
            'nature': self.na_lock,
            'nature_computer_science': self.ncomputersci_lock,
            'nature_communications': self.ncomms_lock
        }
        
        # 获取对应的锁
        current_lock = lock_mapping.get(journal_name)
        
        if current_lock.locked():
            print(f"{journal_name} 抓取正在进行中，请稍后")
            return
            
        current_lock.acquire()
        print(f"开始抓取 {journal_name} 数据...")
        
        def on_fetch_complete(results):
            self.show_results(results)
            print(f"{journal_name} 抓取完成！")
            current_lock.release()
        
        self.thread = FetchNatureThread(journal_name)
        self.thread.result_signal.connect(on_fetch_complete)
        self.thread.start()

    def start_fetch_arxiv(self):
        if self.arxiv_lock.locked():
            print("ArXiv 抓取正在进行中，请稍后")
            return
        
        self.arxiv_lock.acquire()
        print("开始抓取ArXiv数据...")
        
        def on_fetch_complete(results):
            self.show_results(results)
            print("ArXiv 抓取完成！")
            self.arxiv_lock.release()
        
        self.thread = FetcharxivThread()
        self.thread.result_signal.connect(on_fetch_complete)
        self.thread.start()


    def start_fetch_huggingface(self):
        
        self.thread = FethuggingfaceThread()  
        self.thread.result_signal.connect(self.show_results)  # 绑定信号到回调函数
        self.thread.start()  # 启动线程
        


    def start_fetch_medarxiv(self):
        if not hasattr(self, 'medarxiv_lock'):
            self.medarxiv_lock = Lock()
            
        if self.medarxiv_lock.locked():
            print("Medarxiv 抓取正在进行中，请稍后")
            return
            
        self.medarxiv_lock.acquire()
        print("开始抓取Medarxiv数据...")
        
        def on_fetch_complete(results):
            self.show_results(results)
            print("Medarxiv 抓取完成！")
            self.medarxiv_lock.release()
        
        self.thread = FetchmedarxivThread()
        self.thread.result_signal.connect(on_fetch_complete)
        self.thread.start()

    def start_fetch_cell(self):
           
        if self.cell_lock.locked():
            print("Cell 抓取正在进行中，请稍后")
            return
            
        self.cell_lock.acquire()
        print("开始抓取Cell数据...")
        
        def on_fetch_complete(results):
            self.show_results(results)
            print("Cell 抓取完成！")
            self.cell_lock.release()
        
        self.thread = FetchcellThread()
        self.thread.result_signal.connect(on_fetch_complete)
        self.thread.start()

    def start_fetch_science(self):
        if not hasattr(self, 'science_lock'):
            self.science_lock = Lock()
            
        if self.science_lock.locked():
            print("Science 抓取正在进行中，请稍后")
            return
            
        self.science_lock.acquire()
        print("开始抓取Science数据...")
        
        def on_fetch_complete(results):
            self.show_results(results)
            print("Science 抓取完成！")
            self.science_lock.release()
        
        self.thread = FetchscienceThread()
        self.thread.result_signal.connect(on_fetch_complete)
        self.thread.start()


# 在文件开头添加
from io import StringIO
from PyQt5.QtCore import QObject, pyqtSignal

class OutputRedirector(QObject):
    outputWritten = pyqtSignal(str)

    def write(self, text):
        self.outputWritten.emit(str(text))
    
    def flush(self):
        pass



# === utils ====

class VisualizationThread(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, vis_type):
        super().__init__()
        self.vis_type = vis_type
        
    def run(self):
        try:
            if self.vis_type == 'citations':
                file_path = generate_citation_plot()
            elif self.vis_type == 'github':
                file_path = generate_github_stars_plot()
            elif self.vis_type == 'source':
                file_path = generate_source_distribution()
            else:
                file_path = None
                
            self.finished.emit(file_path)
        except Exception as e:
            print(f"Visualization error: {str(e)}")
            self.finished.emit(None)


from modules.others import fetch_scholar
# 首先添加 ScholarThread 类
class FetchScholarThread(QThread):
    result_signal = pyqtSignal(list)

    def __init__(self, keywords, num_pages=10):
        super().__init__()
        self.keywords = keywords
        self.num_pages = num_pages

    def run(self):
        try:
            results = fetch_scholar(self.keywords, self.num_pages)
            self.result_signal.emit(results)
        except Exception as e:
            self.result_signal.emit([("Error fetching from Scholar", "", "Error", 0)])


from modules.util import github_scrath

# 首先修改 FetchgithubThread 类
class FetchgithubThread(QThread):
    result_signal = pyqtSignal(list)

    def __init__(self, keyword):  # 修改构造函数，接收关键字参数
        super().__init__()
        self.keyword = keyword

    def run(self):  # 修改 run 方法，移除参数
        try:
            result = github_scrath(self.keyword, 5, 3)
            self.result_signal.emit(result)
        except Exception as e:
            self.result_signal.emit([("Error fetching github", "", 0)])

from modules.cell_series import fetch_cell
class FetchcellThread(QThread):
    result_signal = pyqtSignal(list)  # 定义信号，传递抓取结果

    def __init__(self):
        super().__init__()
        self.journal_name = 'Cell'

    def run(self):
        try:
            # 调用 fetch_nature_series 抓取数据
            result = fetch_cell(5)
            self.result_signal.emit(result)  # 发送信号，将结果传回主线程
        except Exception as e:
            self.result_signal.emit([(f"Error fetching {self.journal_name}: {str(e)}", "", "", "")])


class FetchscienceThread(QThread):
    result_signal = pyqtSignal(list)  # 定义信号，传递抓取结果

    def __init__(self):
        super().__init__()
        # self.journal_name = journal_name

    def run(self):
        try:
            # 调用 fetch_nature_series 抓取数据
            result = fetch_science(5)
            self.result_signal.emit(result)  # 发送信号，将结果传回主线程
        except Exception as e:
            self.result_signal.emit([(f"Error fetching {self.journal_name}: {str(e)}", "", "", "")])


class WordCloudThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, set_column=4):
        super().__init__()
        self.set_column = set_column

    def run(self):
        file_path = generate_wordclouds(self.set_column)
        self.finished.emit(file_path)  # 将生成的文件路径传回主线程



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




def insert_changeline(title):
    setlens = 88
    for i in range(setlens,len(title),setlens):
        title= title[:i]+'<br>'+title[i:]
    return title

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



class FetchbioarxivThread(QThread):
    result_signal = pyqtSignal(list)  # 定义信号，传递抓取结果

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            # 调用 fetch_nature_series 抓取数据
            result = fetch_biorxiv_medrxiv('bio')
            self.result_signal.emit(result)  # 发送信号，将结果传回主线程
        except Exception as e:
            self.result_signal.emit([(f"Error fetching {self.journal_name}: {str(e)}", "", "", "")])

class FetchmedarxivThread(QThread):
    result_signal = pyqtSignal(list)  # 定义信号，传递抓取结果

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            # 调用 fetch_nature_series 抓取数据
            result = fetch_biorxiv_medrxiv('med')
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

def back_up_data():
    File_names = ['favorites.json','cache.json']

from utils.utils import back_up_data

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
    file_names = ['favorites.json', 'cache.json']
    back_up_data(file_names)
    main()
