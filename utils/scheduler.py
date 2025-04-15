import schedule
import time
from modules.arxiv import fetch_arxiv

def job():
    papers = fetch_arxiv()
    print("Fetched papers:", papers)

schedule.every().day.at("09:00").do(job)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
