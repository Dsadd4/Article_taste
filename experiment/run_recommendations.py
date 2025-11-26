"""
运行三种推荐方法并保存结果
用于与 true_label 进行对比评估
"""
import sys
import os
import json

# 添加上一级目录到系统路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 在导入 recommendation 之前，修改 CACHE_FILE 和 FAVORITES_FILE
import utils.recommendation as rec_module
# 固定使用 cache_11_26.json 和项目根目录的 favorites.json
rec_module.CACHE_FILE = os.path.join(project_root, 'cache_11_26.json')
rec_module.FAVORITES_FILE = os.path.join(project_root, 'favorites.json')

from utils.recommendation import (
    method_a_keyword_match,
    method_b_embedding_match,
    method_c_agent_recommendation,
    clean_text
)

# 文件路径
CACHE_FILE = os.path.join(project_root, 'cache_11_26.json')
FAVORITES_FILE = os.path.join(project_root, 'favorites.json')
OUTPUT_DIR = os.path.dirname(__file__)


def organize_results_by_journal(results: list) -> dict:
    """
    将推荐结果按期刊组织
    
    参数:
        results: List[Tuple[title, link, score, journal_name]]
    
    返回:
        {journal_name: [list of articles with indices]}
    """
    journal_results = {}
    
    # 加载缓存，用于建立索引映射
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    # 为每个期刊建立文章索引映射（使用清理后的标题和链接作为键）
    journal_article_maps = {}
    for journal_name, source_data in cache.items():
        if isinstance(source_data, dict) and 'data' in source_data:
            articles = source_data['data']
            article_map = {}
            for i, article in enumerate(articles):
                if isinstance(article, (list, tuple)) and len(article) >= 2:
                    title, link = article[0], article[1]
                    # 清理标题并标准化链接
                    title_clean = clean_text(title)
                    link_clean = link.strip()
                    # 使用清理后的标题和链接作为唯一标识
                    article_map[(title_clean, link_clean)] = f"A{i+1}"
                    # 也保存原始标题的映射（以防万一）
                    article_map[(title, link)] = f"A{i+1}"
            journal_article_maps[journal_name] = article_map
    
    # 按期刊分组结果
    for title, link, score, journal_name in results:
        if journal_name not in journal_results:
            journal_results[journal_name] = []
        
        # 查找对应的索引（尝试多种匹配方式）
        article_index = None
        if journal_name in journal_article_maps:
            article_map = journal_article_maps[journal_name]
            # 先尝试原始匹配
            article_index = article_map.get((title, link))
            # 如果失败，尝试清理后的匹配
            if not article_index:
                title_clean = clean_text(title)
                link_clean = link.strip()
                article_index = article_map.get((title_clean, link_clean))
        
        journal_results[journal_name].append({
            'title': title,
            'link': link,
            'score': score,
            'index': article_index  # A1, A2, A3...
        })
    
    # 按分数排序（每个期刊内）
    for journal_name in journal_results:
        journal_results[journal_name].sort(key=lambda x: x['score'], reverse=True)
    
    return journal_results


def run_method_a() -> dict:
    """运行方法A：关键词匹配"""
    print("\n" + "="*60)
    print("方法A：关键词匹配推荐")
    print("="*60)
    
    # 检查收藏夹
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            favorites = json.load(f)
        print(f"收藏夹包含 {len(favorites)} 篇文章")
    else:
        print(f"⚠ 收藏夹文件不存在: {FAVORITES_FILE}")
    
    results = method_a_keyword_match(top_n=20)
    print(f"✓ 方法A完成，共推荐 {len(results)} 篇文章")
    
    if len(results) == 0:
        print("⚠ 警告：方法A未返回任何推荐结果")
        print("可能原因：1) 收藏夹为空 2) 没有匹配的关键词 3) 缓存文件问题")
    
    # 按期刊组织
    organized = organize_results_by_journal(results)
    
    # 转换为与 true_label 类似的格式
    output = {}
    for journal_name, articles in organized.items():
        output[journal_name] = {
            'journal_name': journal_name,
            'selected_indices': [a['index'] for a in articles if a['index']],
            'articles': articles,
            'method': 'keyword_match',
            'count': len(articles)
        }
    
    return output


def run_method_b() -> dict:
    """运行方法B：语义相似度"""
    print("\n" + "="*60)
    print("方法B：语义相似度推荐")
    print("="*60)
    
    # 检查收藏夹
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            favorites = json.load(f)
        print(f"收藏夹包含 {len(favorites)} 篇文章")
    else:
        print(f"⚠ 收藏夹文件不存在: {FAVORITES_FILE}")
    
    result = method_b_embedding_match(top_n=20)
    
    # 检查返回值类型
    if isinstance(result, tuple) and len(result) == 2:
        results, summaries = result
    else:
        results = result if isinstance(result, list) else []
        summaries = {}
    
    print(f"✓ 方法B完成，共推荐 {len(results)} 篇文章")
    
    if len(results) == 0:
        print("⚠ 警告：方法B未返回任何推荐结果")
        print("可能原因：1) 收藏夹为空 2) embedding模型加载失败 3) 缓存文件问题")
    
    # 按期刊组织
    organized = organize_results_by_journal(results)
    
    # 转换为与 true_label 类似的格式
    output = {}
    for journal_name, articles in organized.items():
        output[journal_name] = {
            'journal_name': journal_name,
            'selected_indices': [a['index'] for a in articles if a['index']],
            'articles': articles,
            'method': 'embedding_match',
            'count': len(articles),
            'summaries': summaries.get(journal_name, '')
        }
    
    return output


def run_method_c() -> dict:
    """运行方法C：AI智能推荐"""
    print("\n" + "="*60)
    print("方法C：AI智能推荐")
    print("="*60)
    
    # 方法C返回两个值：results 和 journal_summaries
    result = method_c_agent_recommendation(top_n=5)
    
    # 检查返回值类型
    if isinstance(result, tuple) and len(result) == 2:
        results, journal_summaries = result
    else:
        # 如果只返回一个值（降级情况）
        results = result if isinstance(result, list) else []
        journal_summaries = {}
    
    print(f"✓ 方法C完成，共推荐 {len(results)} 篇文章")
    
    # 按期刊组织
    organized = organize_results_by_journal(results)
    
    # 转换为与 true_label 类似的格式
    output = {}
    for journal_name, articles in organized.items():
        output[journal_name] = {
            'journal_name': journal_name,
            'selected_indices': [a['index'] for a in articles if a['index']],
            'articles': articles,
            'method': 'agent_recommendation',
            'count': len(articles),
            'summary': journal_summaries.get(journal_name, '')
        }
    
    return output


def main():
    """主函数"""
    print("="*60)
    print("运行三种推荐方法")
    print("="*60)
    print(f"使用缓存文件: {CACHE_FILE}")
    print(f"使用收藏夹文件: {FAVORITES_FILE}")
    
    # 检查缓存文件是否存在
    if not os.path.exists(CACHE_FILE):
        print(f"✗ 缓存文件不存在: {CACHE_FILE}")
        return
    
    # 检查收藏夹文件是否存在
    if not os.path.exists(FAVORITES_FILE):
        print(f"⚠ 收藏夹文件不存在: {FAVORITES_FILE}")
        print("方法A和B需要收藏夹文件才能工作")
    else:
        # 检查收藏夹是否为空
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                favorites = json.load(f)
            if not favorites or len(favorites) == 0:
                print("⚠ 收藏夹文件为空，方法A和B可能无法正常工作")
            else:
                print(f"✓ 收藏夹文件存在，包含 {len(favorites)} 篇文章")
        except Exception as e:
            print(f"⚠ 无法读取收藏夹文件: {e}")
    
    all_results = {}
    
    # 运行方法A
    try:
        method_a_results = run_method_a()
        all_results['method_a'] = method_a_results
        
        # 保存方法A结果
        output_file_a = os.path.join(OUTPUT_DIR, 'recommendations_method_a.json')
        with open(output_file_a, 'w', encoding='utf-8') as f:
            json.dump(method_a_results, f, ensure_ascii=False, indent=2)
        print(f"✓ 方法A结果已保存到: {output_file_a}")
    except Exception as e:
        print(f"✗ 方法A执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 运行方法B
    try:
        method_b_results = run_method_b()
        all_results['method_b'] = method_b_results
        
        # 保存方法B结果
        output_file_b = os.path.join(OUTPUT_DIR, 'recommendations_method_b.json')
        with open(output_file_b, 'w', encoding='utf-8') as f:
            json.dump(method_b_results, f, ensure_ascii=False, indent=2)
        print(f"✓ 方法B结果已保存到: {output_file_b}")
    except Exception as e:
        print(f"✗ 方法B执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 运行方法C
    try:
        method_c_results = run_method_c()
        all_results['method_c'] = method_c_results
        
        # 保存方法C结果
        output_file_c = os.path.join(OUTPUT_DIR, 'recommendations_method_c.json')
        with open(output_file_c, 'w', encoding='utf-8') as f:
            json.dump(method_c_results, f, ensure_ascii=False, indent=2)
        print(f"✓ 方法C结果已保存到: {output_file_c}")
    except Exception as e:
        print(f"✗ 方法C执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 保存所有结果到一个文件
    output_file_all = os.path.join(OUTPUT_DIR, 'recommendations_all.json')
    with open(output_file_all, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 所有结果已保存到: {output_file_all}")
    
    # 统计信息
    print("\n" + "="*60)
    print("统计信息")
    print("="*60)
    for method_name, method_results in all_results.items():
        total_journals = len(method_results)
        total_articles = sum(r['count'] for r in method_results.values())
        print(f"{method_name}:")
        print(f"  - 期刊数: {total_journals}")
        print(f"  - 推荐文章总数: {total_articles}")
        print(f"  - 平均每期刊: {total_articles/total_journals:.1f} 篇" if total_journals > 0 else "  - 平均每期刊: 0 篇")


if __name__ == "__main__":
    main()

