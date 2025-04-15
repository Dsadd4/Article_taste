import time
import logging
import os
from CloudflareBypasser import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions

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
    options.set_argument("--window-position=-32000,-32000")
     
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
# from utils import save_cache

from modules.util import save_cache,load_cache,load_all_cache,is_cached


def fetch_cell(maxissue):
    try:
        journal_name = 'cell'
        if is_cached(journal_name):
            return load_cache(journal_name)
        
        papers = []
        url = 'https://www.cell.com/cell/archive'
        f = pass_the(url)

        sp = BeautifulSoup(f, 'html.parser')

        issues = sp.find('li',class_ = 'accordion__tab accordion__closed').find('ul',class_='rlist list-of-issues__list').find_all('a')

        begin_issues = 1
        for sing_is in issues:
            part_link = sing_is.get('href')
            link = 'https://www.cell.com'+ part_link
            # print(link)
            f2 = pass_the(link)
            sp = BeautifulSoup(f2,'html.parser')
            sp = str(sp)
            #<a href="/cell/fulltext/S0092-8674(25)00100-X">Distinct mismatch-repair complex genes set neuronal CAG-repeat expansion rate to drive selective pathogenesis in HD mice</a>
            patterns = r'<a href="/cell/fulltext/([^"]+)">([^<>]+)</a>'
            ret = re.findall(patterns,sp)
            
            for doi,title in ret:
                if title == 'Full-Text HTML':
                    continue
                # print("-----------------------------------")
                artlink = 'https://www.cell.com/cell/abstract/'+doi
                # print(artlink)
                # print(title)
                if title.count(' ')>=2:
                    papers.append((title,artlink)) 
            if begin_issues>maxissue:
                break
            begin_issues+=1
        save_cache(journal_name, papers)
        print(f'cache {journal_name} saved!')
    except Exception as e:
        print(f"we failed at {journal_name}")

    # print(papers)
    return papers

# fetch_cell(5)