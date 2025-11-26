"""
生成 true_label 的脚本
为每个期刊调用 GPT-3.5，基于真实研究兴趣生成20个推荐文献作为 ground truth
"""
import sys
import os
import json
import yaml
import re

# 添加上一级目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.chat_engine import chat_with_gpt
from utils.recommendation import clean_text

# 文件路径
CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'cache_11_26.json')
PROMPT_FILE = os.path.join(os.path.dirname(__file__), 'prompt.yaml')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'true_labels.json')


def load_prompt_config():
    """加载 prompt 配置"""
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config.get('true_label_generation_prompt', ''), config.get('My_true_intersting', '')


def build_prompt_for_journal(prompt_template: str, my_interests: str, journal_name: str, articles: list) -> str:
    """
    为特定期刊构建完整的 prompt
    
    参数:
        prompt_template: true_label_generation_prompt 模板
        my_interests: My_true_intersting 内容
        journal_name: 期刊名称
        articles: 该期刊的文章列表，格式为 [[title, link], ...]
    
    返回:
        完整的 prompt 字符串
    """
    # 构建文献列表（编号 A1, A2, A3...）
    articles_text = "\n".join([
        f"A{i+1}. {clean_text(article[0])}" 
        for i, article in enumerate(articles)
        if isinstance(article, (list, tuple)) and len(article) >= 2
    ])
    
    # 构建完整 prompt
    full_prompt = f"""{prompt_template}

My true research interests (My_true_intersting):
{my_interests}

Papers from {journal_name} journal (candidates for selection):
{articles_text}

Please select exactly 20 papers that are most relevant to my research interests."""
    
    return full_prompt


def parse_llm_response(response: str) -> dict:
    """
    解析 LLM 返回的 JSON 响应
    
    参数:
        response: LLM 返回的原始响应
    
    返回:
        解析后的字典，包含 selected_indices 和 reasoning
    """
    # 清理响应文本
    response = response.strip()
    
    # 移除可能的 markdown 代码块标记
    if response.startswith("```json"):
        response = response[7:]
    elif response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
    response = response.strip()
    
    # 尝试解析 JSON
    try:
        result = json.loads(response)
        return result
    except json.JSONDecodeError as e:
        # 如果直接解析失败，尝试提取 JSON 部分
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return result
            except:
                pass
        print(f"JSON 解析失败: {e}")
        print(f"响应内容: {response[:500]}...")
        return {}


def generate_true_labels_for_journal(journal_name: str, articles: list, prompt_template: str, my_interests: str) -> dict:
    """
    为单个期刊生成 true_label
    
    参数:
        journal_name: 期刊名称
        articles: 该期刊的文章列表
        prompt_template: prompt 模板
        my_interests: 研究兴趣
    
    返回:
        包含 true_label 信息的字典
    """
    print(f"\n{'='*60}")
    print(f"正在处理期刊: {journal_name}")
    print(f"文章数量: {len(articles)}")
    print(f"{'='*60}")
    
    # 构建 prompt
    full_prompt = build_prompt_for_journal(prompt_template, my_interests, journal_name, articles)
    
    # 调用 GPT-3.5
    try:
        print(f"正在调用 GPT-3.5 生成 true_label...")
        # 注意：根据 chat_with_gpt 的注释，可能需要使用 "gpt-4o-mini" 代替 "gpt-3.5-turbo"
        # 如果遇到模型错误，请尝试修改为 "gpt-4o-mini"
        response, usage = chat_with_gpt(
            task="生成真实标签",
            prompt=full_prompt,
            model="gpt-3.5-turbo",  # 如果失败，可尝试改为 "gpt-4o-mini"
            temperature=0.3  # 降低温度以获得更稳定的结果
        )
        
        # 解析响应
        result = parse_llm_response(response)
        
        if 'selected_indices' in result:
            selected_indices = result['selected_indices']
            reasoning = result.get('reasoning', '')
            
            print(f"✓ 成功生成 {len(selected_indices)} 个 true_label")
            print(f"Token 使用: {usage.get('total_tokens', 'N/A')}")
            
            return {
                'journal_name': journal_name,
                'selected_indices': selected_indices,
                'reasoning': reasoning,
                'total_articles': len(articles),
                'usage': usage
            }
        else:
            print(f"✗ 响应格式不正确，缺少 selected_indices")
            return None
            
    except Exception as e:
        print(f"✗ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    print("="*60)
    print("True Label 生成脚本")
    print("="*60)
    
    # 加载配置
    print("\n1. 加载配置...")
    prompt_template, my_interests = load_prompt_config()
    if not prompt_template or not my_interests:
        print("✗ 无法加载 prompt 配置")
        return
    
    print(f"✓ Prompt 模板已加载")
    print(f"✓ 研究兴趣: {my_interests[:100]}...")
    
    # 加载缓存数据
    print("\n2. 加载缓存数据...")
    if not os.path.exists(CACHE_FILE):
        print(f"✗ 缓存文件不存在: {CACHE_FILE}")
        return
    
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    # 按期刊分组
    journal_groups = {}
    for source, source_data in cache.items():
        if isinstance(source_data, dict) and 'data' in source_data:
            articles = source_data['data']
            if articles and len(articles) > 0:
                journal_groups[source] = articles
    
    print(f"✓ 找到 {len(journal_groups)} 个期刊")
    for journal_name in journal_groups.keys():
        print(f"  - {journal_name}: {len(journal_groups[journal_name])} 篇文章")
    
    # 加载已有结果（如果存在）
    existing_results = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing_results = json.load(f)
            print(f"✓ 发现已有结果文件，包含 {len(existing_results)} 个期刊")
        except:
            print("⚠ 无法读取已有结果文件，将重新生成")
    
    # 为每个期刊生成 true_label
    print("\n3. 开始生成 true_label...")
    all_results = existing_results.copy()  # 从已有结果开始
    total_journals = len(journal_groups)
    processed = 0
    skipped = 0
    
    import time
    for idx, (journal_name, articles) in enumerate(journal_groups.items(), 1):
        # 如果已有结果，跳过
        if journal_name in existing_results:
            print(f"\n进度: [{idx}/{total_journals}] {journal_name} - 跳过（已有结果）")
            skipped += 1
            continue
        
        print(f"\n进度: [{idx}/{total_journals}]")
        result = generate_true_labels_for_journal(
            journal_name, 
            articles, 
            prompt_template, 
            my_interests
        )
        
        if result:
            all_results[journal_name] = result
            processed += 1
        
        # 添加延迟，避免 API 限流（最后一个不需要延迟）
        if idx < total_journals:
            time.sleep(1)
    
    # 保存结果
    print("\n4. 保存结果...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 结果已保存到: {OUTPUT_FILE}")
    print(f"\n{'='*60}")
    print("生成完成！统计信息:")
    print(f"{'='*60}")
    print(f"本次新处理: {processed} 个期刊")
    print(f"跳过已有: {skipped} 个期刊")
    print(f"总计: {len(all_results)}/{total_journals} 个期刊")
    
    # 统计信息
    if all_results:
        total_selected = sum(len(r['selected_indices']) for r in all_results.values())
        avg_selected = total_selected / len(all_results)
        print(f"总共生成了 {total_selected} 个 true_label")
        print(f"平均每个期刊: {avg_selected:.1f} 个 true_label")
        
        # 显示每个期刊的统计
        print("\n各期刊详情:")
        for journal_name, result in all_results.items():
            print(f"  - {journal_name}: {len(result['selected_indices'])} 个 true_label")


if __name__ == "__main__":
    main()

