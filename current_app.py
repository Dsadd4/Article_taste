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

from utils.functions import generate_wordclouds, load_all_cache
from utils.recommendation import get_recommendations


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
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QScrollArea, QWidget, QTextBrowser, QTextEdit, QLineEdit
import webbrowser
from threading import Lock
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtGui import QIcon  


from utils.functions import generate_citation_plot,generate_github_stars_plot,generate_source_distribution
# === GUI ===
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
       
        # Apply a global stylesheet for the application
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 16px;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QTextBrowser {
                background-color: #ffffff;
                color: #333333;
                font-family: Arial, sans-serif;
                font-size: 14px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
            }
            QLabel {
                font-size: 16px;
                color: #333333;
            }
            QScrollArea {
                border: none;
            }
        """)

        self.setWindowTitle("Article_taste")
        # 设置窗口图标
        self.setWindowIcon(QIcon('achat.png')) 
        self.setGeometry(100, 100, 2000, 1200)
        self.favorites = self.load_favorites()
        
        # 初始化聊天历史记录（用于多轮对话）
        self.chat_history_messages = []  # 存储格式: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        self.current_chat_session_id = None  # 当前聊天会话ID（用于保存）



         # 创建主布局
        main_layout = QHBoxLayout()  

        #layout默认在左边

        button_scroll = QScrollArea()
        button_scroll.setWidgetResizable(True)
        # button_scroll.setStyleSheet("background-color: #f5f5f5; border: none;")
        button_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 需要时显示滚动条
        button_scroll.setMaximumHeight(600)  # 增加高度限制，确保能看到更多按钮
        button_scroll.setFixedWidth(300)  # 设置固定宽度
        button_container = QWidget()
        layout = QVBoxLayout(button_container)

        collections_rightoflayout = QVBoxLayout()



        layout2 = QVBoxLayout()
        


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
        
        # 推荐系统按钮
        self.recommend_lock = Lock()
        self.recommend_button = QPushButton("智能推荐")
        self.recommend_button.clicked.connect(lambda: self.start_recommendation('auto'))
        layout.addWidget(self.recommend_button)
        
        self.recommend_keyword_button = QPushButton("推荐（关键词）")
        self.recommend_keyword_button.clicked.connect(lambda: self.start_recommendation('keyword'))
        layout.addWidget(self.recommend_keyword_button)
        
        self.recommend_embedding_button = QPushButton("推荐（语义）")
        self.recommend_embedding_button.clicked.connect(lambda: self.start_recommendation('embedding'))
        layout.addWidget(self.recommend_embedding_button)
        
        self.recommend_agent_button = QPushButton("推荐（AI）")
        self.recommend_agent_button.clicked.connect(lambda: self.start_recommendation('agent'))
        layout.addWidget(self.recommend_agent_button)
        
        layout.addStretch()



        button_scroll.setWidget(button_container)

        # 用于展示自己所关注的重要网站
        # 首先再创造一个layout，使得展示的网站在按钮区域的右边，充分利用空间
        # 创建一个新的布局
        layout_firstrow = QHBoxLayout()
        # 创建一个标签用于展示网站
        self.hotsite_area = QTextBrowser()
        self.hotsite_area.setOpenExternalLinks(True)
       
        # 添加网站信息内容
        hotsite_html = self.load_hotsite_info()
        self.hotsite_area.setHtml(hotsite_html)
        self.hotsite_area.setOpenExternalLinks(True)


        layout_firstrow.addWidget(button_scroll)
        layout_firstrow.addWidget(self.hotsite_area)
       
        # 设置样式
        layout_firstrow.setContentsMargins(0, 0, 0, 0)  # 去掉边距
        layout_firstrow.setSpacing(0)  # 去掉间距
        
        #创建容器来包含布局
        layout_firstrow_container = QWidget()
        layout_firstrow_container.setLayout(layout_firstrow)
      
        layout_firstrow_container.setFixedHeight(300)  # 设置固定高度




        
        # 添加按钮到布局
        # layout2.addWidget(button_scroll)
       

        layout2.addWidget(layout_firstrow_container)

        # 结果展示区域
        self.result_area = QTextBrowser()
        self.result_area.setOpenExternalLinks(True)
        self.result_area.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.result_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.result_area.customContextMenuRequested.connect(self.show_context_menu)
        


       

        layout2.addWidget(self.result_area)
   
        






        # 创建调试信息显示区域
        self.debug_area = QTextBrowser()
        self.debug_area.setMaximumHeight(150)  # 限制高度
                # 在 __init__ 中设置调试区域样式
        self.debug_area.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #dcdcdc;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout2.addWidget(self.debug_area)
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

        # 创建一个垂直布局来容纳图形视图、聊天区域和会议信息
        right_layout = QVBoxLayout()

        # 添加图形视图
        right_layout.addWidget(self.graphics_view)

        # 创建聊天区域
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(2, 5, 5, 5)  # 减少左边距
        chat_layout.setSpacing(5)
        
        # 聊天标题和操作按钮（水平布局）
        title_layout = QHBoxLayout()
        chat_title = QLabel("小A")
        chat_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                padding: 5px;
            }
        """)
        title_layout.addWidget(chat_title)
        
        # 新开聊天按钮
        self.new_chat_button = QPushButton("新对话")
        self.new_chat_button.setFixedWidth(70)
        self.new_chat_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 12px;
                border-radius: 5px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.new_chat_button.clicked.connect(self.new_chat_session)
        title_layout.addWidget(self.new_chat_button)
        
        # 保存聊天记录按钮
        self.save_chat_button = QPushButton("保存")
        self.save_chat_button.setFixedWidth(60)
        self.save_chat_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                font-size: 12px;
                border-radius: 5px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.save_chat_button.clicked.connect(self.save_chat_history)
        title_layout.addWidget(self.save_chat_button)
        
        title_layout.addStretch()  # 添加弹性空间
        chat_layout.addLayout(title_layout)
        
        # 对话历史显示区域
        self.chat_history = QTextBrowser()
        self.chat_history.setMaximumHeight(399)
        self.chat_history.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                color: #333333;
                font-family: Arial, sans-serif;
                font-size: 28px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px 0px 5px 0px !important;
            }
        """)
        # 设置文档边距为0，减少左侧空白
        self.chat_history.document().setDocumentMargin(0)
        # 设置默认样式表，消除body和html的默认边距
        self.chat_history.document().setDefaultStyleSheet("""
            body { margin: 0; padding: 0; }
            html { margin: 0; padding: 0; }
            p { margin: 0; padding: 0; margin-bottom: 10px; }
            div { margin: 0; padding: 0; }
        """)
        self.chat_history.setHtml("<body style='margin: 0; padding: 0;'><p style='color:#666; margin: 0; padding: 0; margin-bottom: 10px;'>我是您的小助手！您可以问我关于文章、期刊、研究等相关问题。</p></body>")
        chat_layout.addWidget(self.chat_history)
        
        # 输入区域（水平布局）
        input_layout = QHBoxLayout()
        
        # 输入框
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(60)
        self.chat_input.setPlaceholderText("输入您的问题... (Ctrl+Enter发送)")
        self.chat_input.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #333333;
                font-family: Arial, sans-serif;
                font-size: 28px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        # 绑定Ctrl+Enter快捷键发送消息
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        send_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self.chat_input)
        send_shortcut.activated.connect(self.send_chat_message)
        input_layout.addWidget(self.chat_input)
        
        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.setFixedWidth(60)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        self.send_button.clicked.connect(self.send_chat_message)
        input_layout.addWidget(self.send_button)
        
        chat_layout.addLayout(input_layout)
        
        # 将聊天区域添加到右侧布局
        right_layout.addWidget(chat_container)

        # 创建并添加会议信息面板
        self.conference_info = QTextBrowser()
        self.conference_info.setMaximumHeight(300)
        self.conference_info.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f9fa;
                color: #495057;
                font-family: Arial, sans-serif;
                font-size: 14px;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 8px;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        """)

        # 添加会议信息内容
        conference_html = self.load_conference_info()
        self.conference_info.setHtml(conference_html)
        self.conference_info.setOpenExternalLinks(True)

        right_layout.addWidget(self.conference_info)

        # 创建一个容器 widget 来持有右侧布局
        right_container = QWidget()
        right_container.setLayout(right_layout)

        # 创建 QScrollArea 并设置容器 widget
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(right_container)


        # 添加左侧布局到主布局
        main_layout.addLayout(layout2)
        # 添加右侧的 scroll_area 到主布局
        main_layout.addWidget(self.scroll_area)




        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        print("Welcome to Article_taste！")
    #读取配置信息
   
    def load_conference_info(self):
        if os.path.exists('config.json'):
            conference_info = json.load(open('config.json', 'r', encoding='utf-8'))['conference']
       
            conference_info = [f"<p>• <a href='{info[1]}' style='font-size: 18px;'>{info[0]}</a></p>" for info in conference_info]
            conference_info = "<h3 style='color: #333; margin-bottom: 10px;'>Conference board</h3><div style='margin-left: 10px;'>" + "".join(conference_info)+ "</div>"
  
        return conference_info
    
    def load_hotsite_info(self):
        if os.path.exists('config.json'):
            hotsite_info = json.load(open('config.json', 'r', encoding='utf-8'))['important_site']
            hotsite_info = [f"<a href='{info[1]}' style='font-size: 18px;color:#332'>{info[0]}</a> <span style='color:#128; font-size: 18px'>|</span> " for info in hotsite_info]
            hotsite_info = "<h3 style=' margin-bottom: 5px;'>Hotsite</h3><div style='margin-left: 10px;'>" + "".join(hotsite_info)+ "</div>"
        return hotsite_info

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
    
    def restore_stdout(self):
        # 恢复标准输出（在需要时调用）
        sys.stdout = sys.__stdout__

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

    # 聊天相关方法
    def send_chat_message(self):
        """发送聊天消息"""
        message = self.chat_input.toPlainText().strip()
        if not message:
            return
        
        message_lower = message.lower()
        
        # 检查是否是推荐请求
        is_recommend_request = any(word in message_lower for word in ['推荐', 'recommend', '推荐文章', '相关文章'])
        
        # 显示用户消息
        self.append_chat_message("用户", message)
        
        # 将用户消息添加到历史记录
        self.chat_history_messages.append({"role": "user", "content": message})
        
        # 清空输入框
        self.chat_input.clear()
        
        # 如果是推荐请求，直接触发推荐功能
        if is_recommend_request:
            # 禁用发送按钮
            self.send_button.setEnabled(False)
            self.send_button.setText("推荐中...")
            
            # 根据收藏数量自动选择方法
            favorites_count = len(self.favorites)
            if favorites_count < 3:
                method = 'keyword'
            elif favorites_count < 10:
                method = 'embedding'
            else:
                method = 'agent'
            
            # 显示AI响应
            method_names = {'keyword': '关键词匹配', 'embedding': '语义相似度', 'agent': 'AI智能推荐'}
            response_text = f"好的！我将使用{method_names.get(method, '自动选择')}方法为您推荐文章。\n\n根据您当前有{favorites_count}篇收藏，我选择了最适合的推荐方法。\n\n正在为您生成推荐..."
            self.append_chat_message("AI助手", response_text)
            
            # 将AI响应添加到历史记录
            self.chat_history_messages.append({"role": "assistant", "content": response_text})
            
            # 触发推荐
            self.start_recommendation(method)
            
            # 恢复发送按钮
            self.send_button.setEnabled(True)
            self.send_button.setText("发送")
            return
        
        # 禁用发送按钮，防止重复发送
        self.send_button.setEnabled(False)
        self.send_button.setText("思考中...")
        
        # 启动AI响应线程（传入历史消息）
        self.chat_thread = ChatAgentThread(message, self.get_chat_context(), self.chat_history_messages[:-1])  # 传入除当前消息外的历史
        self.chat_thread.response_signal.connect(self.on_chat_response)
        self.chat_thread.start()
    
    def format_markdown_to_html(self, text):
        """将Markdown格式转换为美观的HTML"""
        import re
        
        if not text:
            return ""
        
        # 先保护代码块，避免被其他规则处理
        code_blocks = []
        def save_code_block(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks)-1}__"
        
        text = re.sub(r'```[\s\S]*?```', save_code_block, text)
        
        # 保护行内代码
        inline_codes = []
        def save_inline_code(match):
            inline_codes.append(match.group(0))
            return f"__INLINE_CODE_{len(inline_codes)-1}__"
        
        text = re.sub(r'`[^`]+`', save_inline_code, text)
        
        # 转义HTML特殊字符
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # 按行处理
        lines = text.split('\n')
        result_lines = []
        in_ul = False
        in_ol = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 处理标题（必须在行首）
            if re.match(r'^#{1,3}\s+', stripped):
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                
                if stripped.startswith('###'):
                    title_text = re.sub(r'^###\s+', '', stripped)
                    result_lines.append(f'<h3 style="color: #0078d7; margin: 12px 0 6px 0; font-size: 18px; font-weight: bold;">{title_text}</h3>')
                elif stripped.startswith('##'):
                    title_text = re.sub(r'^##\s+', '', stripped)
                    result_lines.append(f'<h2 style="color: #005a9e; margin: 14px 0 7px 0; font-size: 20px; font-weight: bold;">{title_text}</h2>')
                elif stripped.startswith('#'):
                    title_text = re.sub(r'^#\s+', '', stripped)
                    result_lines.append(f'<h1 style="color: #004578; margin: 16px 0 8px 0; font-size: 22px; font-weight: bold;">{title_text}</h1>')
                continue
            
            # 处理无序列表
            if re.match(r'^[-*]\s+', stripped):
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                if not in_ul:
                    result_lines.append('<ul style="margin: 8px 0; padding-left: 25px; list-style-type: disc;">')
                    in_ul = True
                item_text = re.sub(r'^[-*]\s+', '', stripped)
                result_lines.append(f'<li style="margin: 4px 0; line-height: 1.5;">{item_text}</li>')
                continue
            
            # 处理有序列表
            if re.match(r'^\d+\.\s+', stripped):
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if not in_ol:
                    result_lines.append('<ol style="margin: 8px 0; padding-left: 25px;">')
                    in_ol = True
                item_text = re.sub(r'^\d+\.\s+', '', stripped)
                result_lines.append(f'<li style="margin: 4px 0; line-height: 1.5;">{item_text}</li>')
                continue
            
            # 普通行
            if in_ul:
                result_lines.append('</ul>')
                in_ul = False
            if in_ol:
                result_lines.append('</ol>')
                in_ol = False
            
            if stripped:  # 非空行
                result_lines.append(line)
            else:  # 空行作为段落分隔
                result_lines.append('<br>')
        
        # 关闭未关闭的列表
        if in_ul:
            result_lines.append('</ul>')
        if in_ol:
            result_lines.append('</ol>')
        
        text = '\n'.join(result_lines)
        
        # 处理粗体 **text** 或 __text__
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong style="font-weight: bold; color: #333;">\1</strong>', text)
        text = re.sub(r'__([^_]+)__', r'<strong style="font-weight: bold; color: #333;">\1</strong>', text)
        
        # 处理斜体 *text*（不在粗体内部）
        text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em style="font-style: italic;">\1</em>', text)
        
        # 恢复代码块
        for i, code_block in enumerate(code_blocks):
            code_content = code_block.replace('```', '').strip()
            text = text.replace(f'__CODE_BLOCK_{i}__', 
                              f'<pre style="background-color: #f5f5f5; padding: 12px; border-radius: 5px; overflow-x: auto; margin: 8px 0; border-left: 3px solid #0078d7;"><code style="font-family: monospace; font-size: 13px;">{code_content}</code></pre>')
        
        # 恢复行内代码
        for i, inline_code in enumerate(inline_codes):
            code_content = inline_code.replace('`', '')
            text = text.replace(f'__INLINE_CODE_{i}__', 
                              f'<code style="background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 13px; color: #d63384;">{code_content}</code>')
        
        # 处理换行：将连续换行转换为段落分隔
        text = re.sub(r'<br>\s*<br>+', '</p><p style="margin: 8px 0; line-height: 1.6;">', text)
        text = '<p style="margin: 5px 0; line-height: 1.6;">' + text + '</p>'
        
        # 清理多余的段落标签和换行
        text = re.sub(r'</p>\s*<p[^>]*>', '<br><br>', text)
        text = re.sub(r'^<p[^>]*>', '', text)
        text = re.sub(r'</p>$', '', text)
        text = re.sub(r'<br>\s*<br>\s*<br>+', '<br><br>', text)  # 限制连续换行
        
        return text
    
    def append_chat_message(self, sender, message):
        """添加聊天消息到历史记录"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 格式化消息内容（如果是AI助手，转换Markdown）
        if sender == "AI助手":
            formatted_message = self.format_markdown_to_html(message)
        else:
            # 用户消息也做基本格式化（转义HTML）
            formatted_message = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
        
        if sender == "用户":
            html = f'''<div style="margin: 0; padding: 0; margin-bottom: 15px; text-align: left;">
<div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); color: #333; padding: 12px 16px; border-radius: 12px; display: inline-block; max-width: 85%; word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
<div style="line-height: 1.6;">{formatted_message}</div>
</div>
<div style="margin-top: 4px;">
<span style="color: #999; font-size: 11px;">{timestamp}</span>
</div>
</div>'''
        else:
            html = f'''<div style="margin: 0; padding: 0; margin-bottom: 15px; text-align: left;">
<div style="background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%); color: #333; padding: 12px 16px; border-radius: 12px; display: inline-block; max-width: 85%; word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #0078d7;">
<div style="margin-bottom: 6px;">
<b style="color: #0078d7; font-size: 14px;"> {sender}</b>
</div>
<div style="line-height: 1.6; color: #333;">{formatted_message}</div>
</div>
<div style="margin-top: 4px;">
<span style="color: #999; font-size: 11px;">{timestamp}</span>
</div>
</div>'''
        
        # 使用moveCursor和insertHtml代替setHtml，避免重新解析整个HTML
        cursor = self.chat_history.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertHtml(html)
        
        # 自动滚动到底部
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )
    
    def on_chat_response(self, response):
        """处理AI响应"""
        self.append_chat_message("AI助手", response)
        # 将AI响应添加到历史记录
        self.chat_history_messages.append({"role": "assistant", "content": response})
        # 恢复发送按钮
        self.send_button.setEnabled(True)
        self.send_button.setText("发送")
    
    def get_chat_context(self):
        """获取聊天上下文（收藏夹、缓存数据等）"""
        context = {
            "favorites_count": len(self.favorites),
            "cache_sources": list(load_all_cache().keys()) if os.path.exists(CACHE_FILE) else []
        }
        return context
    
    def new_chat_session(self):
        """新开聊天会话"""
        # 如果当前有聊天记录，先保存
        if self.chat_history_messages:
            reply = QMessageBox.question(
                self, 
                '新开对话', 
                '是否保存当前对话记录？',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.save_chat_history()
            elif reply == QMessageBox.Cancel:
                return  # 取消操作
        
        # 清空聊天历史
        self.chat_history_messages = []
        self.current_chat_session_id = None
        
        # 清空显示区域
        self.chat_history.setHtml("<body style='margin: 0 !important; padding: 0 !important;'><p style='color:#666; margin: 0 !important; padding: 0 !important;'>我是您的小助手！您可以问我关于文章、期刊、研究等相关问题。</p></body>")
        
        print("已开启新对话")
    
    def save_chat_history(self):
        """保存聊天记录到history_recorder目录"""
        if not self.chat_history_messages:
            QMessageBox.information(self, "提示", "当前没有聊天记录可保存。")
            return
        
        # 确保history_recorder目录存在
        history_dir = "history_recorder"
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)
        
        # 生成文件名（使用时间戳）
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_{timestamp}.json"
        filepath = os.path.join(history_dir, filename)
        
        # 准备保存的数据
        chat_data = {
            "session_id": self.current_chat_session_id or timestamp,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "messages": self.chat_history_messages
        }
        
        # 保存到文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "保存成功", f"聊天记录已保存到：\n{filepath}")
            print(f"聊天记录已保存：{filepath}")
            
            # 更新当前会话ID
            self.current_chat_session_id = timestamp
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存聊天记录时出错：\n{str(e)}")
            print(f"保存聊天记录失败：{str(e)}")
    
    # 推荐系统相关方法
    def start_recommendation(self, method='auto'):
        """启动推荐系统"""
        if self.recommend_lock.locked():
            print("推荐正在进行中，请稍后...")
            return
        
        if not self.favorites:
            self.result_area.setText("⚠️ 您的收藏夹为空，无法进行推荐。请先收藏一些感兴趣的文章。")
            return
        
        self.recommend_lock.acquire()
        method_name = {'auto': '自动选择', 'keyword': '关键词匹配', 'embedding': '语义相似度', 'agent': 'AI智能推荐'}.get(method, '自动选择')
        print(f"开始使用{method_name}方法进行推荐...")
        
        def on_recommend_complete(results, actual_method, journal_summaries):
            self.show_recommendations(results, actual_method, journal_summaries)
            print(f"推荐完成！使用了{actual_method}方法")
            
            # 将summary显示到聊天框（仅方法C有summary）
            if journal_summaries and actual_method == 'AI智能推荐':
                for journal_name, summary in journal_summaries.items():
                    if summary:
                        count = sum(1 for r in results if r[3] == journal_name)
                        message = f"📚 {journal_name}\n\n我为您选取了 {count} 篇相关文章。\n\n推荐理由：\n{summary}"
                        self.append_chat_message("AI助手", message)
            
            self.recommend_lock.release()
            # 确保发送按钮恢复正常状态
            if hasattr(self, 'send_button'):
                self.send_button.setEnabled(True)
                self.send_button.setText("发送")
        
        self.recommend_thread = RecommendationThread(method)
        self.recommend_thread.result_signal.connect(on_recommend_complete)
        self.recommend_thread.start()
    
    def show_recommendations(self, results, method, journal_summaries=None):
        """显示推荐结果（按期刊分类）"""
        if not results:
            self.result_area.setText(f"使用{method}方法未找到推荐文章。请确保：\n1. 收藏夹中有文章\n2. 缓存中有文章数据\n3. 文章与您的收藏有相关性")
            return
        
        if journal_summaries is None:
            journal_summaries = {}
        
        html_results = []
        html_results.append(f"<h3 style='color: #0078d7; margin-bottom: 15px;'>📚 推荐文章（使用{method}方法，共{len(results)}篇）</h3>")
        
        # 按期刊分组
        journal_groups = {}
        for title, link, score, source in results:
            if source not in journal_groups:
                journal_groups[source] = []
            journal_groups[source].append((title, link, score))
        
        # 按期刊展示
        article_idx = 1
        for journal_name, articles in journal_groups.items():
            # 期刊标题
            count = len(articles)
            html_results.append(f'''
                <div style="margin-top: 20px; margin-bottom: 10px;">
                    <h4 style="color: #005a9e; font-size: 18px; font-weight: bold; border-bottom: 2px solid #0078d7; padding-bottom: 5px;">
                        📁 {journal_name} ({count}篇)
                    </h4>
                </div>
            ''')
            
            # 该期刊的文章列表
            for title, link, score in articles:
                # 格式化分数显示
                score_str = f"{score:.3f}" if isinstance(score, float) else str(score)
                
                # 高亮显示匹配度高的文章
                if score > 0.1:
                    title_style = "color:red;font-size:18px;font-weight:600;"
                else:
                    title_style = "color:black;font-size:16px;"
                
                title = insert_changeline(title)
                
                result_html = f'''
                    <div style="margin-bottom: 15px; padding: 10px; border-left: 3px solid #0078d7; background-color: #f8f9fa; margin-left: 20px;">
                        <div style="margin-bottom: 5px;">
                            <span style="background-color: #0078d7; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px; margin-right: 8px;">#{article_idx}</span>
                            <a href="{link}" target="_blank" style="{title_style}">{title}</a>
                        </div>
                        <div style="color: #666; font-size: 12px; margin-top: 5px;">
                            <span style="margin-right: 15px;">📊 匹配度: {score_str}</span>
                        </div>
                    </div>
                '''
                html_results.append(result_html)
                article_idx += 1
        
        self.result_area.setHtml("<br>".join(html_results))

    
    def show_context_menu(self, pos):
        import re
        print("右键菜单事件触发")
        menu = QMenu(self)

        add_fav_action = QAction("添加到收藏夹", self)
        add_fav_action.triggered.connect(self.add_to_favorites)
        menu.addAction(add_fav_action)

        # 获取鼠标位置对应的文章链接和标题
        link, title = self.get_link_and_title_under_cursor(pos)
        title = re.sub(r'<.*?>', '', title)  # 去除HTML标签
        
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

    # 用来展示结果的函数
    def show_results(self, results):
        highlighted_results = []
        # print(len(results[0]))

        if len(results[0]) == 2:  # 处理标题和链接
            #我们这里可以首先进行排序，把包含keyword的放在前面
            results = sorted(results, key=lambda x: any(keyword.lower() in x[0].lower() for keyword in CONFIG["keywords"]), reverse=True)

            for title, link in results:
                title = insert_changeline(title)
                if any(keyword.lower() in title.lower() for keyword in CONFIG["keywords"]):
                    result_html = f'''
                        <div style="margin-bottom: 10px; font-size: 18px;">
                            <b><a href="{link}" target="_blank" style="color: red;">{title}</a></b>
                        </div>
                    '''
                else:
                    result_html = f'''
                        <div style="margin-bottom: 10px; font-size: 16px;">
                            <a href="{link}" target="_blank" style="color: black;">{title}</a>
                        </div>
                    '''
                
                highlighted_results.append(result_html)
        
        elif len(results[0]) == 4:  # 处理包含四个元素的数据
            results = sorted(results, key=lambda x: any(keyword.lower() in x[0].lower() for keyword in CONFIG["keywords"]), reverse=True)
            for title, link, __, ___ in results:
                title = insert_changeline(title)
                if any(keyword.lower() in title.lower() for keyword in CONFIG["keywords"]):
                    result_html = f'''
                        <div style="margin-bottom: 10px; font-size: 18px;">
                            <b><a href="{link}" target="_blank" style="color: red;">{title}</a></b>
                        </div>
                    '''
                else:
                    result_html = f'''
                        <div style="margin-bottom: 10px; font-size: 16px;">
                            <a href="{link}" target="_blank" style="color: black;">{title}</a>
                        </div>
                    '''
                
                highlighted_results.append(result_html)
        
        # 假设使用 QTextBrowser 来显示 HTML
        self.result_area.setHtml("<br>".join(highlighted_results))

    
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
        # 恢复标准输出
        sys.stdout = sys.__stdout__
        
        # for thread in self.threads:
        #     thread.terminate()
        #     thread.wait()
        self.save_favorites()
        
        # 如果有关闭时的聊天记录，询问是否保存
        if self.chat_history_messages:
            reply = QMessageBox.question(
                self, 
                '退出应用', 
                '是否保存当前对话记录？',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.save_chat_history()
        
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


# 推荐系统线程类
class RecommendationThread(QThread):
    result_signal = pyqtSignal(list, str, dict)  # 定义信号，传递推荐结果、方法和summaries
    
    def __init__(self, method='auto'):
        super().__init__()
        self.method = method
    
    def run(self):
        try:
            results, actual_method, journal_summaries = get_recommendations(self.method, top_n=20)
            self.result_signal.emit(results, actual_method, journal_summaries)
        except Exception as e:
            print(f"推荐系统错误: {str(e)}")
            self.result_signal.emit([], f"错误: {str(e)}", {})


# 聊天AI线程类
class ChatAgentThread(QThread):
    response_signal = pyqtSignal(str)  # 定义信号，传递AI响应
    
    def __init__(self, user_message, context=None, history_messages=None):
        super().__init__()
        self.user_message = user_message
        self.context = context or {}
        self.history_messages = history_messages or []  # 历史对话消息
    
    def run(self):
        try:
            response = self.generate_response(self.user_message, self.context, self.history_messages)
            self.response_signal.emit(response)
        except Exception as e:
            error_msg = f"抱歉，处理您的请求时出现错误: {str(e)}"
            self.response_signal.emit(error_msg)
    
    def generate_response(self, message, context, history_messages):
        """生成AI响应（使用chat_engine进行多轮对话）"""
        from utils.chat_engine import chat_engine
        
        # 构建系统提示词（包含上下文信息）
        system_context = []
        
        # 添加收藏夹信息
        fav_count = context.get('favorites_count', 0)
        if fav_count > 0:
            system_context.append(f"用户当前有 {fav_count} 篇收藏的文章。")
        
        # 添加缓存数据源信息
        cache_sources = context.get('cache_sources', [])
        if cache_sources:
            sources_str = '、'.join(cache_sources[:5])
            system_context.append(f"当前缓存的数据来源包括：{sources_str}。")
        
        # 构建完整的系统提示
        system_prompt = f"""你是一个专业的科研助手，可以帮助用户：
1. 分析收藏夹偏好和推荐相关文章
2. 回答关于期刊和文章的问题
3. 协助进行文献检索
4. 生成词云和可视化分析

{chr(10).join(system_context) if system_context else ''}

请用友好、专业的方式回答用户的问题。如果用户询问关于收藏、期刊、推荐等功能，请提供具体的操作指导。"""
        
        # 使用chat_engine进行多轮对话
        engine = chat_engine()
        
        # 调用chat_with_LLM，传入历史消息
        response = engine.chat_with_LLM(
            task="科研助手对话",
            prompt=message,
            model_type="qwen-flash",
            history_messages=history_messages
        )
        
        return response








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
