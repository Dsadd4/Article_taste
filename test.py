import time
import logging
import os
from CloudflareBypasser import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions
from modules.cell_series import fetch_cell






# assert(0)
# fetch_cell(5)

# assert(0)
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cloudflare_bypass.log', mode='w')
    ]
)

def get_chromium_options(browser_path: str, arguments: list) -> ChromiumOptions:
    """
    Configures and returns Chromium options.
    
    :param browser_path: Path to the Chromium browser executable.
    :param arguments: List of arguments for the Chromium browser.
    :return: Configured ChromiumOptions instance.
    """
    options = ChromiumOptions().auto_port()
    options.set_paths(browser_path=browser_path)
    for argument in arguments:
        options.set_argument(argument)
    return options

import random
def mimic_human_behavior(driver):
    try:
        # 随机滚动页面
        scroll_y = random.randint(100, 800)
        driver.run_js(f"window.scrollTo(0, {scroll_y});")
        time.sleep(random.uniform(0.5, 1.5))

        # 使用 JavaScript 执行更自然的滚动
        driver.run_js(f"window.scrollBy(0, {random.randint(50, 300)});")
        time.sleep(random.uniform(0.5, 1.5))

        # # 模拟随机点击（模拟真实用户行为）
        # x = random.randint(100, 800)
        # y = random.randint(100, 600)
        # driver.run_js(f"""
        #     var evt = new MouseEvent('click', {{
        #         bubbles: true,
        #         cancelable: true,
        #         clientX: {x},
        #         clientY: {y}
        #     }});
        #     document.elementFromPoint({x}, {y}).dispatchEvent(evt);
        # """)
        logging.info(f"Simulated human scroll and click at ({x}, {y}).")

    except Exception as e:
        logging.warning(f"Failed to mimic human behavior: {str(e)}")







def pass_the(url):
    # Chromium Browser Path
    # isHeadless = os.getenv('HEADLESS', 'false').lower() == 'true'
    
    # if isHeadless:
    #     from pyvirtualdisplay import Display
    #     display = Display(visible=0, size=(1920, 1080))
    #     display.start()

    browser_path = os.getenv('CHROME_PATH', "/usr/bin/google-chrome")
    
    # Windows Example
    # browser_path = os.getenv('CHROME_PATH', r"C:/Program Files/Google/Chrome/Application/chrome.exe")

    # Arguments to make the browser better for automation and less detectable.

    arguments = [
        "--start-minimized",
    "-no-first-run",
    "-force-color-profile=srgb",
    "-metrics-recording-only",
    "-password-store=basic",
    "-use-mock-keychain",
    "-export-tagged-pdf",
    "-no-default-browser-check",
    "-disable-background-mode",
    "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
    "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
    "-deny-permission-prompts",
    "-disable-gpu",
    "-accept-lang=en-US",
    "-incognito",  # 使用隐身模式
    "-disable-extensions",  # 禁用扩展，减少指纹
    "-disable-blink-features=AutomationControlled",  # 移除 "webdriver" 标志
    "--disable-infobars",  # 移除提示栏
    "--disable-dev-shm-usage",  # 防止内存溢出
    "--remote-debugging-port=9222",  # 远程调试支持
    "--disable-software-rasterizer",  # 禁用软件光栅化
    "--mute-audio"  # 禁用音频，减少资源占用
    ]

    options = get_chromium_options(browser_path, arguments)
    #这里决定是否打开窗口,打开是为了看效果
    # options.set_argument("--window-position=-32000,-32000")
     
    options.set_argument('--disable-background-timer-throttling')
    options.set_argument('--disable-backgrounding-occluded-windows')
    options.set_argument('--disable-renderer-backgrounding')

    #这里决定是否打开窗口,打开是为了看效果
    # options.headless(True) 
    
    # Initialize the browser
    driver = ChromiumPage(addr_or_opts=options)

    # print(dir(driver))


   


    try:
        logging.info('Navigating to the demo page.')
        driver.get(url)
        mimic_human_behavior(driver)

        # Where the bypass starts
        logging.info('Starting Cloudflare bypass.')
        cf_bypasser = CloudflareBypasser(driver)

        # If you are solving an in-page captcha (like the one here: https://seleniumbase.io/apps/turnstile), use cf_bypasser.click_verification_button() directly instead of cf_bypasser.bypass().
        # It will automatically locate the button and click it. Do your own check if needed.
        

        cf_bypasser.bypass()
        

        logging.info("Enjoy the content!")
        logging.info("Title of the page: %s", driver.title)
        # 获取页面HTML内容
        html_content = driver.html  # 使用html属性
        with open('ex.html','w',encoding='utf-8') as f:
            f.write(html_content)


    except Exception as e:
        logging.error("An error occurred: %s", str(e))

    driver.quit()


    return html_content 



from bs4 import BeautifulSoup
import re
maxidx = 3
def fetch_science(maxissue):
    papers = []
    url = 'https://www.science.org/loi/science'
    f = pass_the(url)

    sp = BeautifulSoup(f, 'html.parser')
    md = sp.find('div',class_ = 'row mt-4')
    md = str(md)
    # print(md)

    patterns = r'href=".*?"'
    htmls = re.findall(patterns, md)
    print(htmls)
    idx = 0



    for urp in htmls:
        patterns = r'"(.*)"'
        pur = re.findall(patterns,urp)[0]
        url = 'https://www.science.org'+ pur
        # print(urp)
        # break
        # url = 'https://www.science.org/toc/science/387/6738'
        html_r = pass_the(url)
        sp = BeautifulSoup(html_r, 'html.parser')
        sp = str(sp)
        patterns = r'<a[^>]*href="/doi/([^"]+)"[^>]*>([^<>]*)</a>'
        ret = re.findall(patterns,sp)
        for doi,title in ret:
            if title.count(' ')>=2:
                papers.append((title,'https://www.science.org/doi/'+doi))
        
        idx +=1 

        print(f'We now catch issue {idx}')
        if idx>= maxissue:
            break
    print(papers)
    return papers

url="https://academicpositions.com/find-jobs?positions[0]=phd&fields[0]=computer-science-mf"
html_content = pass_the(url)
# soup = BeautifulSoup(html_content, 'html.parser')
print(html_content)
with open('ex.html','w',encoding='utf-8') as f:
    f.write(html_content)

assert(0)

def fetch_scholar(keywords, num_pages=10):
    """
    获取多个关键词的Google Scholar搜索结果
    :param keywords: 关键词列表
    :param num_pages: 每个关键词搜索的页数
    :return: 结果列表 [(title, link, author_venue, citations)]
    """
    all_articles = []
    
    for keyword in keywords:
        # 将关键词转换为Google Scholar搜索格式
        search_query = '+'.join(keyword.split())
        print(f"\nSearching for: {keyword}")
        
        for page in range(num_pages):
            start_idx = page * 10
            url = f"https://scholar.google.com/scholar?start={start_idx}&q={search_query}&hl=zh-CN&as_sdt=0,5"
            print(f"Fetching page {page + 1}/{num_pages}...")
            
            try:
                html_content = pass_the(url)
                soup = BeautifulSoup(html_content, 'html.parser')
                
                for result in soup.select('.gs_ri'):
                    try:
                        # 获取标题和链接
                        title_tag = result.select_one('.gs_rt a')
                        if not title_tag:
                            continue
                        
                        title = title_tag.text.strip()
                        link = title_tag['href']
                        
                        # 获取作者、期刊和年份信息
                        author_venue = result.select_one('.gs_a')
                        author_venue_text = author_venue.text if author_venue else "N/A"
                        
                        # 获取引用数
                        citations = 0
                        cite_tag = result.select_one('.gs_fl')
                        if cite_tag:
                            cite_match = re.search(r'被引用次数：(\d+)', cite_tag.text)
                            if cite_match:
                                citations = int(cite_match.group(1))
                        
                        # 将结果添加为元组
                        all_articles.append((title, link, author_venue_text, citations))
                        
                    except Exception as e:
                        print(f"Error parsing result: {e}")
                
                time.sleep(random.uniform(0.5, 1))
                
            except Exception as e:
                print(f"Error fetching page {page + 1}: {e}")
                continue
    
    # 按引用次数排序
    all_articles.sort(key=lambda x: x[3], reverse=True)
    return all_articles

# 使用示例
keywords = ['protein language model', 'biology', 'cell']
results = fetch_scholar(keywords, num_pages=2)
print(f"\nTotal articles found: {len(results)}")

# 打印排序后的结果
for idx, (title, link, author_venue, citations) in enumerate(results, 1):
    print(f"\nArticle {idx}:")
    print(f"Title: {title}")
    print(f"Authors & Venue: {author_venue}")
    print(f"Citations: {citations}")
    print(f"Link: {link}")
    print("-" * 50)