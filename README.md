<!-- Language Switcher -->
<p align="right">
  <a href="#english-version">English</a> | <a href="#chinese-version">中文</a>
</p>

# <a id="english-version"></a>Article Taste - Scientific Paper Tracker

## Overview

Article Taste is a comprehensive desktop application for tracking and managing scientific papers across multiple platforms. Built with PyQt5, this tool helps researchers stay updated with the latest publications from ArXiv, Nature journals, bioRxiv, medRxiv, Science, Cell, and more.

<img src="achat.png" alt="Application Screenshot" width="200"/>

## Applicaiton window

<img src="./img/window.PNG" alt="Application Screenshot" width="600"/>

## Features

- **Multi-source paper tracking**: Monitor publications from numerous scientific platforms in one place
- **Smart keyword highlighting**: Papers containing your keywords of interest are automatically highlighted in red
- **Favorites system**: Save interesting papers to your collection for future reference
- **Publication analytics**: Visualize citation distributions, GitHub stars, and source distributions
- **Word cloud generation**: Generate word clouds from paper titles to identify trending topics
- **PDF download**: Automatically download papers containing your keywords
- **Google Scholar integration**: Search Google Scholar with customizable keywords
- **GitHub repository search**: Find relevant code repositories related to your research

## Installation

### Prerequisites
- Python 3.8+
- Conda (recommended for environment management)
- Google Chrome browser (required for Science and Cell journal access)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/article_taste.git
cd article_taste
```

2. Create and activate a conda environment:
```bash
conda create -n paper_tracker python=3.8
conda activate paper_tracker
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
or
```bash
conda env create -f environment.yml
```

4. Configure Chrome:
   - Install Chrome from the [official website](https://www.google.com/chrome/)
   - Set the Chrome path via environment variable:
     - Windows: `setx CHROME_PATH "C:\Program Files\Google\Chrome\Application\chrome.exe"`
     - macOS: `export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`
     - Linux: `export CHROME_PATH="/usr/bin/google-chrome"`
   - Or modify the path directly in `modules/cell_series.py`

5. Run the application:
```bash
python current_app.py
```

## Usage

### Configuration

Edit the `config.json` file to customize your experience:

```json
{
  "keywords": ["machine learning", "deep learning", "reinforcement learning"],
  "conference": [
    ["CVPR 2025", "https://cvpr2025.thecvf.com/"],
    ["ICML 2025", "https://icml.cc/"]
  ]
}
```

### Main Interface

- **Left panel**: Source selection buttons for different journals and repositories
- **Center panel**: Article display area with clickable links
- **Right panel**: Visualization area and conference information
- **Bottom panel**: Debug console with real-time status updates

### Paper Browsing

1. Click on any source button (ArXiv, Nature, bioRxiv, etc.) to fetch recent papers
2. Papers containing your keywords will be highlighted in red
3. Click on any paper title to open it in your browser
4. Right-click on a paper and select "Add to favorites" to save it

### Visualizations

- **Generate Word Cloud**: Create a visual representation of frequent terms in paper titles
- **Citation Distribution**: View the distribution of citation counts among papers
- **GitHub Stars Distribution**: Analyze popularity of GitHub repositories
- **Source Distribution**: See a breakdown of papers by their sources

## Project Structure

```
├── current_app.py         # Main application file
├── config.json            # Configuration file
├── modules/               # Source-specific modules
│   ├── xiv_scrath.py      # ArXiv, bioRxiv, and medRxiv handlers
│   ├── nature_series.py   # Nature journals handlers
│   ├── science_series.py  # Science journal handler
│   ├── cell_series.py     # Cell journal handler
│   ├── others.py          # Google Scholar handler
│   └── util.py            # GitHub search utilities
├── utils/                 # Utility functions
│   ├── functions.py       # Visualization generators
│   └── utils.py           # Backup utilities
├── favorites.json         # Saved favorite papers
└── cache.json             # Cache for faster loading
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt5 for the GUI framework
- BeautifulSoup for web scraping capabilities
- Matplotlib and WordCloud for visualization features
- [paperscraper](https://github.com/jannisborn/paperscraper) project which inspired our bioRxiv integration
- [CloudflareBypassForScraping](https://github.com/sarperavci/CloudflareBypassForScraping) library that enabled access to Science and Cell journals
- All contributors whose open-source work made this project possible

---

*Stay updated with the latest scientific research effortlessly!*

---

# <a id="chinese-version"></a>Article Taste - 科学论文追踪器

## 概述

Article Taste 是一款用于跨平台追踪和管理科学论文的综合桌面应用。基于 PyQt5 构建，帮助科研人员及时获取 ArXiv、Nature 期刊、bioRxiv、medRxiv、Science、Cell 等平台的最新论文。

<img src="achat.png" alt="Application Screenshot" width="200"/>

## 应用窗口

<img src="./img/window.PNG" alt="Application Screenshot" width="600"/>

## 功能特色

- **多平台论文追踪**：一站式监控多个科学平台的最新论文
- **智能关键词高亮**：包含关注关键词的论文自动以红色高亮显示
- **收藏系统**：可将感兴趣的论文收藏，便于日后查阅
- **论文分析可视化**：支持引用分布、GitHub 星标、来源分布等可视化
- **词云生成**：根据论文标题生成词云，洞察研究热点
- **PDF 自动下载**：自动下载包含关键词的论文
- **谷歌学术集成**：可自定义关键词搜索 Google Scholar
- **GitHub 仓库搜索**：查找与研究相关的代码仓库

## 安装方法

### 环境要求
- Python 3.8+
- Conda（推荐用于环境管理）
- Google Chrome 浏览器（访问 Science 和 Cell 期刊必需）

### 安装步骤
1. 克隆仓库：
```bash
git clone https://github.com/yourusername/article_taste.git
cd article_taste
```

2. 创建并激活 conda 环境：
```bash
conda create -n paper_tracker python=3.8
conda activate paper_tracker
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```
或
```bash
conda env create -f environment.yml
```

4. 配置 Chrome：
   - 从[官网下载](https://www.google.com/chrome/)并安装 Chrome
   - 通过环境变量设置 Chrome 路径：
     - Windows: `setx CHROME_PATH "C:\Program Files\Google\Chrome\Application\chrome.exe"`
     - macOS: `export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`
     - Linux: `export CHROME_PATH="/usr/bin/google-chrome"`
   - 或直接在 `modules/cell_series.py` 中修改路径

5. 运行应用：
```bash
python current_app.py
```

## 使用说明

### 配置

编辑 `config.json` 文件自定义体验：

```json
{
  "keywords": ["machine learning", "deep learning", "reinforcement learning"],
  "conference": [
    ["CVPR 2025", "https://cvpr2025.thecvf.com/"],
    ["ICML 2025", "https://icml.cc/"]
  ]
}
```

### 主界面

- **左侧面板**：不同期刊和仓库的源选择按钮
- **中间面板**：论文展示区，支持点击跳转
- **右侧面板**：可视化区域和会议信息
- **底部面板**：调试控制台，实时状态更新

### 论文浏览

1. 点击任一源按钮（如 ArXiv、Nature、bioRxiv 等）获取最新论文
2. 包含关键词的论文将以红色高亮
3. 点击论文标题可在浏览器中打开
4. 右键论文选择“添加到收藏”进行保存

### 可视化

- **生成词云**：可视化论文标题中的高频词
- **引用分布**：查看论文引用数量分布
- **GitHub 星标分布**：分析相关仓库的受欢迎程度
- **来源分布**：统计各来源论文数量

## 项目结构

```
├── current_app.py         # 主程序文件
├── config.json            # 配置文件
├── modules/               # 各平台处理模块
│   ├── xiv_scrath.py      # ArXiv、bioRxiv、medRxiv 处理
│   ├── nature_series.py   # Nature 期刊处理
│   ├── science_series.py  # Science 期刊处理
│   ├── cell_series.py     # Cell 期刊处理
│   ├── others.py          # Google Scholar 处理
│   └── util.py            # GitHub 搜索工具
├── utils/                 # 工具函数
│   ├── functions.py       # 可视化生成
│   └── utils.py           # 备份工具
├── favorites.json         # 收藏论文
└── cache.json             # 加载缓存
```

## 贡献

欢迎贡献代码！请提交 Pull Request。

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 鸣谢

- PyQt5 图形界面框架
- BeautifulSoup 网页解析
- Matplotlib 和 WordCloud 可视化
- [paperscraper](https://github.com/jannisborn/paperscraper) 项目为 bioRxiv 集成提供灵感
- [CloudflareBypassForScraping](https://github.com/sarperavci/CloudflareBypassForScraping) 库助力 Science 和 Cell 期刊访问
- 所有开源贡献者

---

*让你轻松掌握最新科学研究进展！*