"""
评估三种推荐方法的表现并生成 Nature 风格的可视化图表
"""
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from typing import Dict, List, Tuple
from collections import defaultdict
import seaborn as sns

# 设置 Nature 风格的图表参数
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'Arial',
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 13,
    'axes.linewidth': 1.0,
    'grid.linewidth': 0.5,
    'lines.linewidth': 2.0,
    'patch.linewidth': 1.0,
    'xtick.major.width': 1.0,
    'ytick.major.width': 1.0,
    'xtick.minor.width': 0.5,
    'ytick.minor.width': 0.5,
    'xtick.major.size': 5,
    'ytick.major.size': 5,
    'xtick.minor.size': 3,
    'ytick.minor.size': 3,
})

# Nature 风格的颜色（专业、清晰）
NATURE_COLORS = {
    'method_a': '#2E86AB',  # 蓝色
    'method_b': '#A23B72',  # 紫红色
    'method_c': '#F18F01',  # 橙色
    'method_a_label': 'Keyword Match',
    'method_b_label': 'Semantic Similarity',
    'method_c_label': 'AI Agent'
}


def load_data():
    """加载 true_label 和推荐结果"""
    base_dir = os.path.dirname(__file__)
    
    # 加载 true_label
    with open(os.path.join(base_dir, 'true_labels.json'), 'r', encoding='utf-8') as f:
        true_labels = json.load(f)
    
    # 加载三种方法的推荐结果
    with open(os.path.join(base_dir, 'recommendations_method_a.json'), 'r', encoding='utf-8') as f:
        method_a = json.load(f)
    
    with open(os.path.join(base_dir, 'recommendations_method_b.json'), 'r', encoding='utf-8') as f:
        method_b = json.load(f)
    
    with open(os.path.join(base_dir, 'recommendations_method_c.json'), 'r', encoding='utf-8') as f:
        method_c = json.load(f)
    
    return true_labels, method_a, method_b, method_c


def precision_at_k(recommended: List[str], relevant: List[str], k: int) -> float:
    """计算 Precision@K"""
    if k == 0:
        return 0.0
    recommended_k = set(recommended[:k])
    relevant_set = set(relevant)
    if len(recommended_k) == 0:
        return 0.0
    return len(recommended_k & relevant_set) / len(recommended_k)


def recall_at_k(recommended: List[str], relevant: List[str], k: int) -> float:
    """计算 Recall@K"""
    if len(relevant) == 0:
        return 0.0
    recommended_k = set(recommended[:k])
    relevant_set = set(relevant)
    return len(recommended_k & relevant_set) / len(relevant_set)


def f1_at_k(recommended: List[str], relevant: List[str], k: int) -> float:
    """计算 F1@K"""
    prec = precision_at_k(recommended, relevant, k)
    rec = recall_at_k(recommended, relevant, k)
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


def ndcg_at_k(recommended: List[str], relevant: List[str], k: int) -> float:
    """计算 NDCG@K"""
    if k == 0 or len(relevant) == 0:
        return 0.0
    
    recommended_k = recommended[:k]
    relevant_set = set(relevant)
    
    # 计算 DCG
    dcg = 0.0
    for i, item in enumerate(recommended_k, 1):
        if item in relevant_set:
            dcg += 1.0 / np.log2(i + 1)
    
    # 计算 IDCG（理想情况下的 DCG）
    idcg = 0.0
    for i in range(1, min(k, len(relevant)) + 1):
        idcg += 1.0 / np.log2(i + 1)
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def mrr(recommended: List[str], relevant: List[str]) -> float:
    """计算 Mean Reciprocal Rank"""
    relevant_set = set(relevant)
    for i, item in enumerate(recommended, 1):
        if item in relevant_set:
            return 1.0 / i
    return 0.0


def evaluate_method(true_labels: Dict, recommendations: Dict, method_name: str) -> Dict:
    """
    评估单个方法的表现
    
    返回:
        {
            'by_journal': {journal_name: {metrics...}},
            'overall': {metrics...}
        }
    """
    results = {
        'by_journal': {},
        'overall': {
            'precision@5': [],
            'recall@5': [],
            'f1@5': [],
            'ndcg@5': [],
            'mrr': [],
            'precision@10': [],
            'recall@10': [],
            'f1@10': [],
            'ndcg@10': [],
            'precision@20': [],
            'recall@20': [],
            'f1@20': [],
            'ndcg@20': []
        }
    }
    
    # 按期刊评估
    for journal_name, true_data in true_labels.items():
        if journal_name not in recommendations:
            continue
        
        true_indices = set(true_data['selected_indices'])
        rec_data = recommendations[journal_name]
        rec_indices = rec_data.get('selected_indices', [])
        
        if len(rec_indices) == 0:
            continue
        
        # 计算各种指标
        metrics = {
            'precision@5': precision_at_k(rec_indices, list(true_indices), 5),
            'recall@5': recall_at_k(rec_indices, list(true_indices), 5),
            'f1@5': f1_at_k(rec_indices, list(true_indices), 5),
            'ndcg@5': ndcg_at_k(rec_indices, list(true_indices), 5),
            'mrr': mrr(rec_indices, list(true_indices)),
            'precision@10': precision_at_k(rec_indices, list(true_indices), 10),
            'recall@10': recall_at_k(rec_indices, list(true_indices), 10),
            'f1@10': f1_at_k(rec_indices, list(true_indices), 10),
            'ndcg@10': ndcg_at_k(rec_indices, list(true_indices), 10),
            'precision@20': precision_at_k(rec_indices, list(true_indices), 20),
            'recall@20': recall_at_k(rec_indices, list(true_indices), 20),
            'f1@20': f1_at_k(rec_indices, list(true_indices), 20),
            'ndcg@20': ndcg_at_k(rec_indices, list(true_indices), 20),
            'num_recommended': len(rec_indices),
            'num_relevant': len(true_indices),
            'num_intersection': len(set(rec_indices) & true_indices)
        }
        
        results['by_journal'][journal_name] = metrics
        
        # 累积到整体统计
        for key in ['precision@5', 'recall@5', 'f1@5', 'ndcg@5', 'mrr',
                    'precision@10', 'recall@10', 'f1@10', 'ndcg@10',
                    'precision@20', 'recall@20', 'f1@20', 'ndcg@20']:
            results['overall'][key].append(metrics[key])
    
    # 计算整体平均值
    for key in results['overall']:
        if isinstance(results['overall'][key], list):
            results['overall'][key] = {
                'mean': np.mean(results['overall'][key]) if results['overall'][key] else 0.0,
                'std': np.std(results['overall'][key]) if results['overall'][key] else 0.0,
                'median': np.median(results['overall'][key]) if results['overall'][key] else 0.0
            }
    
    return results


def create_comparison_figures(eval_results: Dict):
    """创建对比图表"""
    
    methods = ['method_a', 'method_b', 'method_c']
    method_labels = [NATURE_COLORS[f'{m}_label'] for m in methods]
    colors = [NATURE_COLORS[m] for m in methods]
    
    # 准备数据
    metrics_data = {
        'Precision@5': [],
        'Recall@5': [],
        'F1@5': [],
        'NDCG@5': [],
        'MRR': [],
        'Precision@10': [],
        'Recall@10': [],
        'F1@10': [],
        'NDCG@10': [],
        'Precision@20': [],
        'Recall@20': [],
        'F1@20': [],
        'NDCG@20': []
    }
    
    errors_data = {key: [] for key in metrics_data.keys()}
    
    for method in methods:
        overall = eval_results[method]['overall']
        metrics_data['Precision@5'].append(overall['precision@5']['mean'])
        errors_data['Precision@5'].append(overall['precision@5']['std'])
        metrics_data['Recall@5'].append(overall['recall@5']['mean'])
        errors_data['Recall@5'].append(overall['recall@5']['std'])
        metrics_data['F1@5'].append(overall['f1@5']['mean'])
        errors_data['F1@5'].append(overall['f1@5']['std'])
        metrics_data['NDCG@5'].append(overall['ndcg@5']['mean'])
        errors_data['NDCG@5'].append(overall['ndcg@5']['std'])
        metrics_data['MRR'].append(overall['mrr']['mean'])
        errors_data['MRR'].append(overall['mrr']['std'])
        metrics_data['Precision@10'].append(overall['precision@10']['mean'])
        errors_data['Precision@10'].append(overall['precision@10']['std'])
        metrics_data['Recall@10'].append(overall['recall@10']['mean'])
        errors_data['Recall@10'].append(overall['recall@10']['std'])
        metrics_data['F1@10'].append(overall['f1@10']['mean'])
        errors_data['F1@10'].append(overall['f1@10']['std'])
        metrics_data['NDCG@10'].append(overall['ndcg@10']['mean'])
        errors_data['NDCG@10'].append(overall['ndcg@10']['std'])
        metrics_data['Precision@20'].append(overall['precision@20']['mean'])
        errors_data['Precision@20'].append(overall['precision@20']['std'])
        metrics_data['Recall@20'].append(overall['recall@20']['mean'])
        errors_data['Recall@20'].append(overall['recall@20']['std'])
        metrics_data['F1@20'].append(overall['f1@20']['mean'])
        errors_data['F1@20'].append(overall['f1@20']['std'])
        metrics_data['NDCG@20'].append(overall['ndcg@20']['mean'])
        errors_data['NDCG@20'].append(overall['ndcg@20']['std'])
    
    # 图1: 主要指标对比（@5）
    fig1, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig1.suptitle('Performance Comparison at Top-5 Recommendations', fontsize=13, fontweight='bold')
    
    x_pos = np.arange(len(methods))
    width = 0.6
    
    # Precision@5
    axes[0, 0].bar(x_pos, [metrics_data['Precision@5'][i] for i in range(3)], 
                   width, yerr=[errors_data['Precision@5'][i] for i in range(3)],
                   color=colors, alpha=0.8, capsize=5, error_kw={'linewidth': 1.5})
    axes[0, 0].set_ylabel('Precision@5', fontsize=11)
    axes[0, 0].set_xticks(x_pos)
    axes[0, 0].set_xticklabels(method_labels, fontsize=10)
    axes[0, 0].set_ylim([0, max(metrics_data['Precision@5']) * 1.2])
    axes[0, 0].grid(True, alpha=0.3, linestyle='--')
    axes[0, 0].spines['top'].set_visible(False)
    axes[0, 0].spines['right'].set_visible(False)
    
    # Recall@5
    axes[0, 1].bar(x_pos, [metrics_data['Recall@5'][i] for i in range(3)], 
                   width, yerr=[errors_data['Recall@5'][i] for i in range(3)],
                   color=colors, alpha=0.8, capsize=5, error_kw={'linewidth': 1.5})
    axes[0, 1].set_ylabel('Recall@5', fontsize=11)
    axes[0, 1].set_xticks(x_pos)
    axes[0, 1].set_xticklabels(method_labels, fontsize=10)
    axes[0, 1].set_ylim([0, max(metrics_data['Recall@5']) * 1.2])
    axes[0, 1].grid(True, alpha=0.3, linestyle='--')
    axes[0, 1].spines['top'].set_visible(False)
    axes[0, 1].spines['right'].set_visible(False)
    
    # F1@5
    axes[1, 0].bar(x_pos, [metrics_data['F1@5'][i] for i in range(3)], 
                   width, yerr=[errors_data['F1@5'][i] for i in range(3)],
                   color=colors, alpha=0.8, capsize=5, error_kw={'linewidth': 1.5})
    axes[1, 0].set_ylabel('F1@5', fontsize=11)
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(method_labels, fontsize=10)
    axes[1, 0].set_ylim([0, max(metrics_data['F1@5']) * 1.2])
    axes[1, 0].grid(True, alpha=0.3, linestyle='--')
    axes[1, 0].spines['top'].set_visible(False)
    axes[1, 0].spines['right'].set_visible(False)
    
    # NDCG@5
    axes[1, 1].bar(x_pos, [metrics_data['NDCG@5'][i] for i in range(3)], 
                   width, yerr=[errors_data['NDCG@5'][i] for i in range(3)],
                   color=colors, alpha=0.8, capsize=5, error_kw={'linewidth': 1.5})
    axes[1, 1].set_ylabel('NDCG@5', fontsize=11)
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(method_labels, fontsize=10)
    axes[1, 1].set_ylim([0, max(metrics_data['NDCG@5']) * 1.2])
    axes[1, 1].grid(True, alpha=0.3, linestyle='--')
    axes[1, 1].spines['top'].set_visible(False)
    axes[1, 1].spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(__file__), 'figure1_performance_top5.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ 已保存: figure1_performance_top5.png")
    
    # 图2: 综合性能对比热力图
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig2.suptitle('Comprehensive Performance Comparison', fontsize=13, fontweight='bold')
    
    # 左图：主要指标对比（分组柱状图）
    metric_names = ['Precision@5', 'Recall@5', 'F1@5', 'NDCG@5', 'MRR']
    x_metrics = np.arange(len(metric_names))
    width = 0.25
    
    for i, method in enumerate(methods):
        values = [
            metrics_data['Precision@5'][i],
            metrics_data['Recall@5'][i],
            metrics_data['F1@5'][i],
            metrics_data['NDCG@5'][i],
            metrics_data['MRR'][i]
        ]
        errors = [
            errors_data['Precision@5'][i],
            errors_data['Recall@5'][i],
            errors_data['F1@5'][i],
            errors_data['NDCG@5'][i],
            errors_data['MRR'][i]
        ]
        ax1.bar(x_metrics + i*width, values, width, yerr=errors,
                label=method_labels[i], color=colors[i], alpha=0.8, 
                capsize=3, error_kw={'linewidth': 1.2})
    
    ax1.set_xlabel('Metrics', fontsize=11)
    ax1.set_ylabel('Score', fontsize=11)
    ax1.set_xticks(x_metrics + width)
    ax1.set_xticklabels(metric_names, fontsize=10)
    ax1.legend(fontsize=9, frameon=True, fancybox=True, shadow=True)
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.set_ylim([0, 1.0])
    
    # 右图：性能热力图
    heatmap_data = np.array([
        [metrics_data['Precision@5'][i], metrics_data['Recall@5'][i], 
         metrics_data['F1@5'][i], metrics_data['NDCG@5'][i], metrics_data['MRR'][i]]
        for i in range(3)
    ])
    
    im = ax2.imshow(heatmap_data, aspect='auto', cmap='YlOrRd', vmin=0, vmax=1)
    ax2.set_xticks(np.arange(len(metric_names)))
    ax2.set_yticks(np.arange(len(method_labels)))
    ax2.set_xticklabels(metric_names, fontsize=10)
    ax2.set_yticklabels(method_labels, fontsize=10)
    ax2.set_xlabel('Metrics', fontsize=11)
    ax2.set_ylabel('Methods', fontsize=11)
    
    # 添加数值标注
    for i in range(len(method_labels)):
        for j in range(len(metric_names)):
            text = ax2.text(j, i, f'{heatmap_data[i, j]:.3f}',
                           ha="center", va="center", color="black", fontsize=9, fontweight='bold')
    
    # 添加颜色条
    cbar = plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label('Score', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(__file__), 'figure2_comprehensive_performance.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ 已保存: figure2_comprehensive_performance.png")
    
    # 图3: 按期刊的详细对比
    # 获取所有期刊名称
    all_journals = set()
    for method in methods:
        all_journals.update(eval_results[method]['by_journal'].keys())
    all_journals = sorted(list(all_journals))
    
    if len(all_journals) > 0:
        # 选择前12个期刊进行可视化（如果太多）
        journals_to_plot = all_journals[:12]
        
        fig3, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig3.suptitle('Performance by Journal (Top-5 Recommendations)', fontsize=13, fontweight='bold')
        
        x_journal = np.arange(len(journals_to_plot))
        width = 0.25
        
        # Precision@5 by journal
        for i, method in enumerate(methods):
            prec_values = [eval_results[method]['by_journal'].get(j, {}).get('precision@5', 0) 
                          for j in journals_to_plot]
            axes[0, 0].bar(x_journal + i*width, prec_values, width, 
                           label=method_labels[i], color=colors[i], alpha=0.8)
        axes[0, 0].set_xlabel('Journal', fontsize=11)
        axes[0, 0].set_ylabel('Precision@5', fontsize=11)
        axes[0, 0].set_xticks(x_journal + width)
        axes[0, 0].set_xticklabels([j.replace('_', ' ').title() for j in journals_to_plot], 
                                   rotation=45, ha='right', fontsize=9)
        axes[0, 0].legend(fontsize=9)
        axes[0, 0].grid(True, alpha=0.3, linestyle='--', axis='y')
        axes[0, 0].spines['top'].set_visible(False)
        axes[0, 0].spines['right'].set_visible(False)
        
        # Recall@5 by journal
        for i, method in enumerate(methods):
            rec_values = [eval_results[method]['by_journal'].get(j, {}).get('recall@5', 0) 
                         for j in journals_to_plot]
            axes[0, 1].bar(x_journal + i*width, rec_values, width, 
                           label=method_labels[i], color=colors[i], alpha=0.8)
        axes[0, 1].set_xlabel('Journal', fontsize=11)
        axes[0, 1].set_ylabel('Recall@5', fontsize=11)
        axes[0, 1].set_xticks(x_journal + width)
        axes[0, 1].set_xticklabels([j.replace('_', ' ').title() for j in journals_to_plot], 
                                   rotation=45, ha='right', fontsize=9)
        axes[0, 1].legend(fontsize=9)
        axes[0, 1].grid(True, alpha=0.3, linestyle='--', axis='y')
        axes[0, 1].spines['top'].set_visible(False)
        axes[0, 1].spines['right'].set_visible(False)
        
        # F1@5 by journal
        for i, method in enumerate(methods):
            f1_values = [eval_results[method]['by_journal'].get(j, {}).get('f1@5', 0) 
                         for j in journals_to_plot]
            axes[1, 0].bar(x_journal + i*width, f1_values, width, 
                           label=method_labels[i], color=colors[i], alpha=0.8)
        axes[1, 0].set_xlabel('Journal', fontsize=11)
        axes[1, 0].set_ylabel('F1@5', fontsize=11)
        axes[1, 0].set_xticks(x_journal + width)
        axes[1, 0].set_xticklabels([j.replace('_', ' ').title() for j in journals_to_plot], 
                                   rotation=45, ha='right', fontsize=9)
        axes[1, 0].legend(fontsize=9)
        axes[1, 0].grid(True, alpha=0.3, linestyle='--', axis='y')
        axes[1, 0].spines['top'].set_visible(False)
        axes[1, 0].spines['right'].set_visible(False)
        
        # NDCG@5 by journal
        for i, method in enumerate(methods):
            ndcg_values = [eval_results[method]['by_journal'].get(j, {}).get('ndcg@5', 0) 
                          for j in journals_to_plot]
            axes[1, 1].bar(x_journal + i*width, ndcg_values, width, 
                           label=method_labels[i], color=colors[i], alpha=0.8)
        axes[1, 1].set_xlabel('Journal', fontsize=11)
        axes[1, 1].set_ylabel('NDCG@5', fontsize=11)
        axes[1, 1].set_xticks(x_journal + width)
        axes[1, 1].set_xticklabels([j.replace('_', ' ').title() for j in journals_to_plot], 
                                   rotation=45, ha='right', fontsize=9)
        axes[1, 1].legend(fontsize=9)
        axes[1, 1].grid(True, alpha=0.3, linestyle='--', axis='y')
        axes[1, 1].spines['top'].set_visible(False)
        axes[1, 1].spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(os.path.join(os.path.dirname(__file__), 'figure3_performance_by_journal.png'), 
                    dpi=300, bbox_inches='tight', facecolor='white')
        print("✓ 已保存: figure3_performance_by_journal.png")
    
    # 图4: MRR 对比
    fig4, ax = plt.subplots(figsize=(8, 6))
    fig4.suptitle('Mean Reciprocal Rank (MRR) Comparison', fontsize=13, fontweight='bold')
    
    x_pos = np.arange(len(methods))
    mrr_values = [metrics_data['MRR'][i] for i in range(3)]
    mrr_errors = [errors_data['MRR'][i] for i in range(3)]
    
    bars = ax.bar(x_pos, mrr_values, width=0.6, yerr=mrr_errors,
                  color=colors, alpha=0.8, capsize=5, error_kw={'linewidth': 1.5})
    ax.set_ylabel('MRR', fontsize=11)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(method_labels, fontsize=10)
    ax.set_ylim([0, max(mrr_values) * 1.2])
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars, mrr_values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + mrr_errors[i] + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(__file__), 'figure4_mrr_comparison.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ 已保存: figure4_mrr_comparison.png")


def save_evaluation_results(eval_results: Dict):
    """保存评估结果到 JSON 文件"""
    output_file = os.path.join(os.path.dirname(__file__), 'evaluation_results.json')
    
    # 转换 numpy 类型为 Python 原生类型
    def convert_numpy(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: convert_numpy(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(item) for item in obj]
        return obj
    
    results_to_save = convert_numpy(eval_results)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results_to_save, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 评估结果已保存到: {output_file}")


def print_summary(eval_results: Dict):
    """打印评估结果摘要"""
    print("\n" + "="*60)
    print("评估结果摘要")
    print("="*60)
    
    methods = ['method_a', 'method_b', 'method_c']
    method_labels = [NATURE_COLORS[f'{m}_label'] for m in methods]
    
    print("\n整体性能 (Overall Performance):")
    print("-" * 60)
    print(f"{'指标':<20} {'Keyword Match':<18} {'Semantic Similarity':<20} {'AI Agent':<15}")
    print("-" * 60)
    
    for metric in ['precision@5', 'recall@5', 'f1@5', 'ndcg@5', 'mrr']:
        values = []
        for method in methods:
            val = eval_results[method]['overall'][metric]['mean']
            values.append(f"{val:.4f}")
        print(f"{metric:<20} {values[0]:<18} {values[1]:<20} {values[2]:<15}")
    
    print("\n按期刊统计的期刊数量:")
    for method, label in zip(methods, method_labels):
        num_journals = len(eval_results[method]['by_journal'])
        print(f"  {label}: {num_journals} 个期刊")


def main():
    """主函数"""
    print("="*60)
    print("推荐系统评估与可视化")
    print("="*60)
    
    # 加载数据
    print("\n1. 加载数据...")
    true_labels, method_a, method_b, method_c = load_data()
    print(f"✓ True labels: {len(true_labels)} 个期刊")
    print(f"✓ Method A: {len(method_a)} 个期刊")
    print(f"✓ Method B: {len(method_b)} 个期刊")
    print(f"✓ Method C: {len(method_c)} 个期刊")
    
    # 评估三种方法
    print("\n2. 评估推荐方法...")
    eval_results = {
        'method_a': evaluate_method(true_labels, method_a, 'method_a'),
        'method_b': evaluate_method(true_labels, method_b, 'method_b'),
        'method_c': evaluate_method(true_labels, method_c, 'method_c')
    }
    print("✓ 评估完成")
    
    # 打印摘要
    print_summary(eval_results)
    
    # 保存评估结果
    print("\n3. 保存评估结果...")
    save_evaluation_results(eval_results)
    
    # 创建可视化图表
    print("\n4. 生成可视化图表...")
    create_comparison_figures(eval_results)
    
    print("\n" + "="*60)
    print("完成！所有图表已保存到 experiment 目录")
    print("="*60)


if __name__ == "__main__":
    main()

