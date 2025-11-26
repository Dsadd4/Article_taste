"""
推荐系统模块
实现三种推荐方法：关键词匹配、语义相似度、AI智能推荐
"""
import os
import json
import re
import sys
from collections import Counter
from typing import List, Tuple, Dict
import time
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

# LangChain相关功能暂时移除，方法B和C待实现
# 后续可以通过直接调用API（如Qwen、OpenAI等）来实现，无需LangChain依赖
LANGCHAIN_AVAILABLE = False

# 停用词列表（英文）
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
    'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 
    'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
    'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
    'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's',
    't', 'can', 'will', 'just', 'don', 'should', 'now'
}

# 中文停用词
CHINESE_STOP_WORDS = {
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
    '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
    '看', '好', '自己', '这', '那', '为', '以', '与', '及', '或', '但', '而',
    '如果', '因为', '所以', '虽然', '然而', '此外', '另外', '同时', '首先',
    '其次', '最后', '总之', '因此', '所以', '由于', '通过', '基于', '根据'
}

CACHE_FILE = 'cache.json'
FAVORITES_FILE = 'favorites.json'


def clean_text(text: str) -> str:
    """清理文本，去除HTML标签和特殊字符"""
    # 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 去除特殊字符，保留字母、数字、空格和常见标点
    text = re.sub(r'[^\w\s\-]', ' ', text)
    # 转换为小写
    text = text.lower()
    return text.strip()


def extract_keywords_from_favorites() -> Dict[str, float]:
    """
    从收藏夹中提取关键词及其权重
    返回: {keyword: weight} 字典
    """
    if not os.path.exists(FAVORITES_FILE):
        return {}
    
    with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
        favorites = json.load(f)
    
    if not favorites:
        return {}
    
    all_words = []
    
    for fav_item in favorites:
        # 处理两种格式：list格式 [title_html, link] 或 tuple格式 (title, link)
        if isinstance(fav_item, (list, tuple)) and len(fav_item) >= 1:
            title = fav_item[0]  # 第一个元素是标题（可能包含HTML）
            title_clean = clean_text(title)
            # 分词（简单按空格分割，后续可以改进）
            words = title_clean.split()
            # 过滤停用词和短词
            words = [w for w in words if len(w) > 2 and w not in STOP_WORDS and w not in CHINESE_STOP_WORDS]
            all_words.extend(words)
    
    # 计算词频
    word_freq = Counter(all_words)
    total_words = sum(word_freq.values())
    
    # 计算TF权重（词频 / 总词数）
    keywords = {}
    for word, freq in word_freq.items():
        keywords[word] = freq / total_words if total_words > 0 else 0
    
    return keywords


def calculate_keyword_match_score(title: str, keywords: Dict[str, float]) -> float:
    """
    计算文章标题与关键词的匹配分数
    """
    title_clean = clean_text(title)
    title_words = title_clean.split()
    
    score = 0.0
    matched_keywords = []
    
    for word in title_words:
        if word in keywords:
            score += keywords[word]
            matched_keywords.append(word)
    
    # 奖励匹配多个关键词的情况
    if len(matched_keywords) > 1:
        score *= (1 + len(matched_keywords) * 0.1)
    
    return score


def method_a_keyword_match(top_n: int = 20) -> List[Tuple[str, str, float, str]]:
    """
    方法A：关键词匹配推荐
    按期刊分组，每个期刊返回5篇推荐文章
    
    参数:
        top_n: 总返回前N篇推荐文章（实际按期刊分配，每个期刊5篇）
    
    返回:
        List[Tuple[title, link, score, source]] - 推荐文章列表
    """
    # 提取收藏夹关键词
    keywords = extract_keywords_from_favorites()
    
    if not keywords:
        return []
    
    # 加载所有缓存的文章
    if not os.path.exists(CACHE_FILE):
        return []
    
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    # 按期刊分组处理
    top_n_per_journal = 5
    all_recommendations = []
    
    for source, source_data in cache.items():
        if isinstance(source_data, dict) and 'data' in source_data:
            articles = source_data['data']
            journal_articles = []
            
            for article in articles:
                if isinstance(article, (list, tuple)) and len(article) >= 2:
                    title = article[0]
                    link = article[1]
                    # 计算匹配分数
                    score = calculate_keyword_match_score(title, keywords)
                    if score > 0:  # 只保留有匹配的文章
                        journal_articles.append((title, link, score, source))
            
            # 按分数排序
            journal_articles.sort(key=lambda x: x[2], reverse=True)
            
            # 每个期刊返回Top 5
            all_recommendations.extend(journal_articles[:top_n_per_journal])
    
    # 按分数全局排序（可选）
    all_recommendations.sort(key=lambda x: x[2], reverse=True)
    
    # 返回所有推荐的文章（每个期刊最多5篇）
    return all_recommendations


def get_favorites_titles() -> List[str]:
    """获取收藏夹中的所有标题（清理后的）"""
    if not os.path.exists(FAVORITES_FILE):
        return []
    
    with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
        favorites = json.load(f)
    
    titles = []
    for fav_item in favorites:
        if isinstance(fav_item, (list, tuple)) and len(fav_item) >= 1:
            title = fav_item[0]
            title_clean = clean_text(title)
            titles.append(title_clean)
    
    return titles


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """计算余弦相似度"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def _process_single_journal_embedding(args: Tuple[str, List, np.ndarray, int]) -> List[Tuple[str, str, float, str]]:
    """
    处理单个期刊的embedding推荐（用于多进程）
    
    参数:
        args: (journal_name, articles, favorite_avg_vector, top_n_per_journal)
    
    返回:
        推荐的文章列表
    """
    journal_name, articles, favorite_avg_vector, top_n_per_journal = args
    
    try:
        # 在每个进程中重新导入（多进程需要）
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from sentence_transformers import SentenceTransformer
        
        print(f"\n[进程] 处理期刊: {journal_name}, 文章数: {len(articles)}")
        
        # 加载embedding模型（每个进程独立加载）
        model_name = "paraphrase-MiniLM-L3-v2"
        try:
            model = SentenceTransformer(model_name)
        except Exception:
            model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # 收集该期刊的文章并计算相似度
        journal_articles = []
        
        for article in articles:
            if isinstance(article, (list, tuple)) and len(article) >= 2:
                title = article[0]
                link = article[1]
                title_clean = clean_text(title)
                
                try:
                    # 向量化文章标题
                    article_embedding = model.encode([title_clean], show_progress_bar=False)[0]
                    # 计算与收藏夹平均向量的相似度
                    similarity = cosine_similarity(
                        np.array(favorite_avg_vector),
                        np.array(article_embedding)
                    )
                    
                    if similarity > 0:  # 只保留有相似度的文章
                        journal_articles.append((title, link, float(similarity), journal_name))
                except Exception as e:
                    continue
        
        # 按相似度排序
        journal_articles.sort(key=lambda x: x[2], reverse=True)
        
        # 返回该期刊的Top N
        return journal_articles[:top_n_per_journal]
        
    except Exception as e:
        print(f"[进程] {journal_name} - 处理出错: {str(e)}")
        return []


def method_b_embedding_match(top_n: int = 20) -> Tuple[List[Tuple[str, str, float, str]], Dict[str, str]]:
    """
    方法B：语义相似度推荐（多进程版本）
    
    使用轻量级embedding模型（paraphrase-MiniLM-L3-v2，约40MB）
    按期刊分组，多进程并行处理，每个期刊返回top-5文章
    
    参数:
        top_n: 总返回前N篇推荐文章（实际按期刊分配，每个期刊5篇）
    
    返回:
        (推荐文章列表, summaries字典)
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("sentence-transformers未安装，降级到关键词匹配")
        print("请运行: pip install sentence-transformers")
        results = method_a_keyword_match(top_n)
        return results, {}
    
    # 获取收藏夹标题
    favorite_titles = get_favorites_titles()
    if not favorite_titles:
        return [], {}
    
    # 在主进程中加载模型并向量化收藏夹（避免每个进程都加载）
    model_name = "paraphrase-MiniLM-L3-v2"
    print(f"正在加载embedding模型: {model_name}...")
    
    try:
        model = SentenceTransformer(model_name)
        print("模型加载成功！")
    except Exception as e:
        print(f"模型加载失败: {str(e)}")
        print("尝试使用备用模型: all-MiniLM-L6-v2")
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e2:
            print(f"备用模型也加载失败: {str(e2)}")
            results = method_a_keyword_match(top_n)
            return results, {}
    
    # 向量化收藏夹文章
    try:
        print(f"正在向量化 {len(favorite_titles)} 篇收藏文章...")
        favorite_embeddings = model.encode(favorite_titles, show_progress_bar=False)
        # 计算平均向量作为用户兴趣向量
        favorite_avg_vector = np.mean(favorite_embeddings, axis=0)
        print("收藏夹向量化完成")
    except Exception as e:
        print(f"向量化收藏夹失败: {str(e)}")
        results = method_a_keyword_match(top_n)
        return results, {}
    
    # 加载所有缓存的文章
    if not os.path.exists(CACHE_FILE):
        return [], {}
    
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    # 按期刊分组
    journal_groups = {}
    for source, source_data in cache.items():
        if isinstance(source_data, dict) and 'data' in source_data:
            articles = source_data['data']
            if articles:
                journal_groups[source] = articles
    
    if not journal_groups:
        return [], {}
    
    # 准备多进程参数（每个期刊5篇）
    top_n_per_journal = 5
    process_args = []
    for journal_name, articles in journal_groups.items():
        process_args.append((
            journal_name,
            articles,
            favorite_avg_vector,
            top_n_per_journal
        ))
    
    all_recommendations = []
    
    # 使用多进程并行处理各个期刊
    max_workers = min(len(journal_groups), os.cpu_count() or 4)
    print(f"\n使用 {max_workers} 个进程并行处理 {len(journal_groups)} 个期刊...")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_journal = {
            executor.submit(_process_single_journal_embedding, args): args[0] 
            for args in process_args
        }
        
        # 收集结果
        for future in as_completed(future_to_journal):
            journal_name = future_to_journal[future]
            try:
                recommendations = future.result()
                all_recommendations.extend(recommendations)
                print(f"✓ {journal_name} 处理完成，获得 {len(recommendations)} 篇推荐")
            except Exception as e:
                print(f"✗ {journal_name} 处理失败: {str(e)}")
                continue
    
    # 按相似度全局排序（可选，如果希望跨期刊排序）
    all_recommendations.sort(key=lambda x: x[2], reverse=True)
    
    # 返回所有推荐的文章（每个期刊最多5篇，不限制总数量）
    return all_recommendations, {}


def analyze_favorites_with_llm(favorite_titles: List[str]) -> Dict[str, any]:
    """
    使用LLM分析收藏夹，提取研究兴趣和关键词（待实现）
    
    后续实现方案：
    1. 直接调用Qwen API（无需LangChain）
    2. 或调用OpenAI API
    3. 分析收藏夹内容，提取研究兴趣
    """
    # 暂时使用关键词提取方法
    print("LLM分析功能暂未实现，使用关键词提取方法")
    return extract_keywords_from_favorites()


def extract_journal_from_link(link: str) -> str:
    """
    从链接中提取期刊名称
    参考按钮名称和缓存key进行匹配
    """
    link_lower = link.lower()
    
    # Nature系列期刊（需要精确匹配）
    if 'nature.com' in link_lower:
        if '/nbt/' in link_lower or 'nature-biotechnology' in link_lower:
            return 'nature_biotechnology'
        elif '/nmeth/' in link_lower or 'nature-methods' in link_lower:
            return 'nature_methods'
        elif '/natmachintell/' in link_lower or 'nature-machine-intelligence' in link_lower:
            return 'nature_machine_intelligence'
        elif '/natcomputsci/' in link_lower or 'nature-computer-science' in link_lower:
            return 'nature_computer_science'
        elif '/ncomms/' in link_lower or 'nature-communications' in link_lower:
            return 'nature_communications'
        elif '/nature/' in link_lower:
            return 'nature'
        else:
            return 'nature'  # 默认nature
    
    # Science系列
    elif 'science.org' in link_lower:
        return 'Science'
    
    # Cell系列
    elif 'cell.com' in link_lower:
        return 'cell'
    
    # ArXiv系列
    elif 'arxiv.org' in link_lower:
        if 'biorxiv' in link_lower:
            return 'bioarxiv'
        elif 'medrxiv' in link_lower:
            return 'medarxiv'
        else:
            return 'arxiv'
    
    # GitHub
    elif 'github.com' in link_lower:
        return 'github'
    
    # Google Scholar
    elif 'scholar.google' in link_lower or 'scholar.google.com' in link_lower:
        return 'scholar'
    
    # HuggingFace (虽然按钮被注释了，但保留支持)
    elif 'huggingface.co' in link_lower:
        return 'huggingface'
    
    else:
        return 'other'


def _process_single_journal(args: Tuple[str, List, List[str], str, int]) -> List[Tuple[str, str, float, str]]:
    """
    处理单个期刊的推荐（用于多进程）
    
    参数:
        args: (journal_name, articles, favorite_titles, prompt_template, llm_top_n)
    
    返回:
        推荐的文章列表
    """
    journal_name, articles, favorite_titles, prompt_template, llm_top_n = args
    
    try:
        # 在每个进程中重新导入（多进程需要）
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from utils.chat_engine import chat_engine
        
        print(f"\n[进程] 处理期刊: {journal_name}, 文章数: {len(articles)}")
        
        # 限制文章数量，避免prompt过长
        max_articles = min(300, len(articles))
        articles_to_recommend = articles[:max_articles]
        
        # 构建prompt
        # 收藏夹文献（编号1-15）
        favorites_text = "\n".join([f"{i+1}. {title}" for i, title in enumerate(favorite_titles)])
        
        # 新文章（编号A1, A2, A3...）
        new_articles_text = "\n".join([
            f"A{i+1}. {clean_text(article[0])}" 
            for i, article in enumerate(articles_to_recommend)
            if isinstance(article, (list, tuple)) and len(article) >= 2
        ])
        
        full_prompt = f"""{prompt_template}

My favorites collection (representing my research interests):
{favorites_text}

New papers from {journal_name} journal (candidates for recommendation):
{new_articles_text}

Please recommend the most relevant papers from the new journal list."""
        
        # 初始化chat_engine（每个进程独立）
        engine = chat_engine()
        
        # 调用LLM
        response = engine.chat_with_LLM(
            task="文献推荐",
            prompt=full_prompt,
            model_type="qwen-flash"
        )
        
        # 解析JSON响应
        response = response.strip()
        # 移除可能的markdown代码块标记
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        # 解析JSON
        result = json.loads(response)
        selected_indices = result.get('selected_indices', [])
        summary = result.get('summary', '')
        
        print(f"[进程] {journal_name} - LLM推荐了 {len(selected_indices)} 篇文章")
        
        # 根据编号映射回文章
        article_map = {}
        for i, article in enumerate(articles_to_recommend):
            if isinstance(article, (list, tuple)) and len(article) >= 2:
                article_map[f"A{i+1}"] = article
        
        # 获取推荐的文章（限制为top_n个）
        recommendations = []
        for idx in selected_indices[:llm_top_n]:
            if idx in article_map:
                title, link = article_map[idx][0], article_map[idx][1]
                # 使用固定分数1.0（因为是LLM推荐的）
                recommendations.append((title, link, 1.0, journal_name))
        
        # 返回推荐结果和summary
        return {
            'recommendations': recommendations,
            'summary': summary,
            'journal_name': journal_name,
            'count': len(recommendations)
        }
        
    except json.JSONDecodeError as e:
        print(f"[进程] {journal_name} - 解析JSON失败: {str(e)}")
        return []
    except Exception as e:
        print(f"[进程] {journal_name} - 处理出错: {str(e)}")
        return []


def method_c_agent_recommendation(top_n: int = 5) -> List[Tuple[str, str, float, str]]:
    """
    方法C：AI智能推荐
    
    实现逻辑：
    1. 按期刊分组处理
    2. 随机选择15篇收藏夹文献作为用户兴趣
    3. 对每个期刊，调用LLM推荐top-5文章
    4. 返回所有推荐的文章
    
    参数:
        top_n: 每个期刊返回前N篇推荐文章（固定为5，LLM推荐top-5）
    
    返回:
        List[Tuple[title, link, score, source]] - 推荐文章列表
    """
    # 方法C固定推荐top-5
    llm_top_n = 5
    import random
    import yaml
    
    # 导入chat_engine
    try:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from utils.chat_engine import chat_engine
    except ImportError:
        print("无法导入chat_engine，降级到关键词匹配")
        return method_a_keyword_match(top_n)
    
    # 获取收藏夹
    if not os.path.exists(FAVORITES_FILE):
        return []
    
    with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
        favorites = json.load(f)
    
    if not favorites:
        return []
    
    # 随机选择15篇收藏夹文献
    sample_size = min(15, len(favorites))
    sampled_favorites = random.sample(favorites, sample_size)
    
    # 清理收藏夹标题（去除HTML标签）
    favorite_titles = []
    for fav_item in sampled_favorites:
        if isinstance(fav_item, (list, tuple)) and len(fav_item) >= 1:
            title = fav_item[0]
            title_clean = clean_text(title)
            favorite_titles.append(title_clean)
    
    # 加载prompt模板
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'experiment', 'prompt.yaml')
    if not os.path.exists(prompt_path):
        print(f"Prompt文件不存在: {prompt_path}")
        return method_a_keyword_match(top_n)
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_data = yaml.safe_load(f)
        prompt_template = prompt_data.get('recommendation_prompt', '')
    except Exception as e:
        print(f"加载prompt失败: {str(e)}")
        return method_a_keyword_match(top_n)
    
    # 加载缓存数据
    if not os.path.exists(CACHE_FILE):
        return []
    
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    # 按期刊分组
    journal_groups = {}
    for source, source_data in cache.items():
        if isinstance(source_data, dict) and 'data' in source_data:
            articles = source_data['data']
            if articles:
                journal_groups[source] = articles
    
    if not journal_groups:
        return []
    
    # 准备多进程参数
    process_args = []
    for journal_name, articles in journal_groups.items():
        process_args.append((
            journal_name,
            articles,
            favorite_titles,
            prompt_template,
            llm_top_n
        ))
    
    all_recommendations = []
    journal_summaries = {}  # 存储每个期刊的summary
    
    # 使用多进程并行处理各个期刊
    max_workers = min(len(journal_groups), os.cpu_count() or 4)  # 限制进程数
    print(f"\n使用 {max_workers} 个进程并行处理 {len(journal_groups)} 个期刊...")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_journal = {
            executor.submit(_process_single_journal, args): args[0] 
            for args in process_args
        }
        
        # 收集结果
        for future in as_completed(future_to_journal):
            journal_name = future_to_journal[future]
            try:
                result = future.result()
                if isinstance(result, dict):
                    recommendations = result.get('recommendations', [])
                    summary = result.get('summary', '')
                    all_recommendations.extend(recommendations)
                    if summary:
                        journal_summaries[journal_name] = summary
                    print(f"✓ {journal_name} 处理完成，获得 {len(recommendations)} 篇推荐")
                else:
                    # 兼容旧格式
                    all_recommendations.extend(result)
                    print(f"✓ {journal_name} 处理完成，获得 {len(result)} 篇推荐")
            except Exception as e:
                print(f"✗ {journal_name} 处理失败: {str(e)}")
                continue
    
    # 返回推荐结果和summaries
    return all_recommendations, journal_summaries


def auto_select_method(favorites_count: int) -> str:
    """
    根据收藏夹数量自动选择推荐方法
    
    参数:
        favorites_count: 收藏夹文章数量
    
    返回:
        推荐方法名称: 'keyword', 'embedding', 'agent'
    """
    if favorites_count < 3:
        return 'keyword'
    elif favorites_count < 10:
        return 'embedding'
    else:
        return 'agent'


def get_recommendations(method: str = 'auto', top_n: int = 20) -> Tuple[List[Tuple[str, str, float, str]], str, Dict[str, str]]:
    """
    获取推荐文章
    
    参数:
        method: 推荐方法 ('auto', 'keyword', 'embedding', 'agent')
        top_n: 返回前N篇推荐文章
    
    返回:
        (推荐文章列表, 实际使用的方法)
    """
    # 加载收藏夹数量
    favorites_count = 0
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            favorites = json.load(f)
            favorites_count = len(favorites) if isinstance(favorites, list) else 0
    
    # 自动选择方法
    if method == 'auto':
        method = auto_select_method(favorites_count)
    
    # 根据方法调用相应的推荐函数
    journal_summaries = {}
    if method == 'keyword':
        results = method_a_keyword_match(top_n)
        actual_method = '关键词匹配'
    elif method == 'embedding':
        results, _ = method_b_embedding_match(top_n)
        actual_method = '语义相似度'
        if not results:
            # 如果embedding方法未实现，降级到keyword
            results = method_a_keyword_match(top_n)
            actual_method = '关键词匹配（降级）'
    elif method == 'agent':
        results, journal_summaries = method_c_agent_recommendation(top_n)
        actual_method = 'AI智能推荐'
        if not results:
            # 如果agent方法未实现，降级到embedding或keyword
            results, _ = method_b_embedding_match(top_n)
            journal_summaries = {}
            if not results:
                results = method_a_keyword_match(top_n)
                actual_method = '关键词匹配（降级）'
            else:
                actual_method = '语义相似度（降级）'
    else:
        results = method_a_keyword_match(top_n)
        actual_method = '关键词匹配'
    
    return results, actual_method, journal_summaries

