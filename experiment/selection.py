import sys,json
import os
# 上一级目录加入到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
cache = json.load(open('../cache.json', 'r'))
# print(cache.keys())

from utils.chat_engine import chat_engine

chat_engine = chat_engine()
response = chat_engine.chat_with_LLM("文献管理", "你好，千问", "qwen-flash")
print(response)








