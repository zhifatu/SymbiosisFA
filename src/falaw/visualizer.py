import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional
import matplotlib

# 设置中文字体（如果需要）
try:
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False
except:
    pass


class FALawVisualizer:
    """秩法图可视化器"""

    def __init__(self, element_names: Optional[List[str]] = None):
        self.element_names = element_names or [
            "乾定", "射", "陷", "离", "界", "散", "换", "坤转"
        ]
        self.colors = plt.cm.Set3(np.linspace(0, 1, 8))

    def plot_state_evolution(self, results: Dict[str, Any],
                             figsize: tuple = (15, 10)):
        """绘制系统状态演化图"""
        time_series = results['time_series']
        psi_history = results['psi_history']

        fig, axes = plt.subplots(3, 2, figsize=figsize)
        axes = axes.flatten()

        # 1. 元素强度演化
        ax = axes[0]
        for i in range(8):
            ax.plot(time_series, psi_history[:, i],
                    label=self.element_names[i],
                    color=self.colors[i], linewidth=2, alpha=0.8)
        ax.set_xlabel('时间')
        ax.set_ylabel('元素强度 ψ')
        ax.set_title('八元素强度演化')
        ax.legend(loc='upper right', ncol=2, fontsize=8)
        ax.grid(True, alpha=0.3)

        # 2. 共生度与总原力
        ax = axes[1]
        ax.plot(time_series, results['coordination_history'],
                'b-', linewidth=2, label='共生度 S')
        ax.set_xlabel('时间')
        ax.set_ylabel('共生度', color='b')
        ax.tick_params(axis='y', labelcolor='b')
        ax.set_title('共生度与总原力演化')
        ax.grid(True, alpha=0.3)

        ax2 = ax.twinx()
        ax2.plot(time_series, results['total_force_history'],
                 'r--', linewidth=2, label='总原力 Φ')
        ax2.set_ylabel('总原力', color='r')
        ax2.tick_params(axis='y', labelcolor='r')

        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        # 3. 权力比
        ax = axes[2]
        power_ratio = results['power_ratio_history']
        ax.plot(time_series, power_ratio, 'g-', linewidth=2)
        ax.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='临界 r=1')
        ax.fill_between(time_series, 0, 1,
                        where=np.array(power_ratio) < 1,
                        color='green', alpha=0.1, label='健康区域 (r<1)')
        ax.fill_between(time_series, 1, max(power_ratio) if len(power_ratio) > 0 else 2,
                        where=np.array(power_ratio) > 1,
                        color='red', alpha=0.1, label='危险区域 (r>1)')
        ax.set_xlabel('时间')
        ax.set_ylabel('权力比 r = P_d/P_c')
        ax.set_title('权力比演化 (公理D5)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 4. 坤转元素强度
        ax = axes[3]
        ax.plot(time_series, psi_history[:, 7],
                'purple', linewidth=2, label='坤转强度')

        # 标记坤转事件
        kunzhuan_events = results.get('kunzhuan_events', [])
        for event in kunzhuan_events:
            ax.axvline(x=event['time'], color='red',
                       linestyle=':', alpha=0.7, linewidth=1)
            ax.text(event['time'], 0.9, '坤转',
                    rotation=90, fontsize=8, color='red',
                    ha='center', va='top')

        ax.set_xlabel('时间')
        ax.set_ylabel('坤转强度 ψ₈')
        ax.set_title('坤转倾向与事件')
        ax.set_ylim([0, 1])
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 5. 相空间投影 (乾定-射-换 三角关系)
        ax = axes[4]
        ax.plot(psi_history[:, 0], psi_history[:, 1],
                'b-', alpha=0.5, linewidth=1)
        ax.scatter(psi_history[:, 0], psi_history[:, 1],
                   c=time_series, cmap='viridis', s=20, alpha=0.7)
        ax.set_xlabel('乾定强度 ψ₁')
        ax.set_ylabel('射强度 ψ₂')
        ax.set_title('乾定-射相平面')
        ax.grid(True, alpha=0.3)

        # 标记起始和结束点
        ax.scatter(psi_history[0, 0], psi_history[0, 1],
                   c='green', s=100, marker='o', label='起始')
        ax.scatter(psi_history[-1, 0], psi_history[-1, 1],
                   c='red', s=100, marker='s', label='结束')
        ax.legend()

        # 6. 元素分布雷达图（最终状态）
        ax = axes[5]
        angles = np.linspace(0, 2 * np.pi, 8, endpoint=False).tolist()
        values = psi_history[-1, :].tolist()
        values += values[:1]  # 闭合
        angles += angles[:1]

        # 清除原来的ax[5]，创建极坐标图
        fig.delaxes(ax)
        ax = plt.subplot(3, 2, 6, projection='polar')
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(self.element_names)
        ax.set_title(f'最终状态分布 (t={time_series[-1]:.1f})')
        ax.grid(True)

        plt.tight_layout()
        return fig, axes

    def plot_kunzhuan_analysis(self, results: Dict[str, Any]):
        """坤转事件分析图"""
        kunzhuan_events = results.get('kunzhuan_events', [])
        if not kunzhuan_events:
            print("未检测到坤转事件")
            return None

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()

        # 1. 坤转时刻系统状态
        ax = axes[0]
        event_times = [e['time'] for e in kunzhuan_events]
        conditions = [e['conditions'] for e in kunzhuan_events]

        ax.bar(range(len(event_times)), conditions)
        ax.set_xlabel('坤转事件序号')
        ax.set_ylabel('满足的条件数量')
        ax.set_title('坤转事件触发条件')
        ax.set_xticks(range(len(event_times)))
        ax.set_xticklabels([f't={t:.1f}' for t in event_times], rotation=45)
        ax.grid(True, alpha=0.3, axis='y')

        # 2. 坤转前后元素分布变化
        ax = axes[1]
        if len(kunzhuan_events) > 0:
            event = kunzhuan_events[0]
            before = event['state_before']
            after = event['state_after']

            if before is not None and after is not None:
                x = np.arange(8)
                width = 0.35
                ax.bar(x - width / 2, before, width, label='坤转前', alpha=0.7)
                ax.bar(x + width / 2, after, width, label='坤转后', alpha=0.7)
                ax.set_xlabel('元素')
                ax.set_ylabel('强度')
                ax.set_title(f'坤转前后元素分布变化 (t={event["time"]:.1f})')
                ax.set_xticks(x)
                ax.set_xticklabels(self.element_names)
                ax.legend()
                ax.grid(True, alpha=0.3, axis='y')

        # 3. 坤转时间间隔分布
        ax = axes[2]
        if len(event_times) > 1:
            intervals = np.diff(event_times)
            ax.hist(intervals, bins=min(10, len(intervals)), alpha=0.7, edgecolor='black')
            ax.set_xlabel('坤转间隔时间')
            ax.set_ylabel('频次')
            ax.set_title(f'坤转间隔分布 (平均={np.mean(intervals):.2f})')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, '需要多次坤转\n才能分析间隔',
                    ha='center', va='center', transform=ax.transAxes)
            ax.set_title('坤转间隔分布')

        # 4. 坤转触发条件组合
        ax = axes[3]
        condition_patterns = {}
        for event in kunzhuan_events:
            pattern = event['conditions']
            condition_patterns[pattern] = condition_patterns.get(pattern, 0) + 1

        if condition_patterns:
            patterns = list(condition_patterns.keys())
            counts = list(condition_patterns.values())
            ax.pie(counts, labels=[f'{p}条件' for p in patterns], autopct='%1.1f%%')
            ax.set_title('坤转触发条件组合分布')
        else:
            ax.text(0.5, 0.5, '无坤转事件数据',
                    ha='center', va='center', transform=ax.transAxes)
            ax.set_title('坤转触发条件组合')

        plt.tight_layout()
        return fig, axes

    def plot_comparative_trials(self, trials_results: List[Dict[str, Any]]):
        """比较多次试验的结果"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()

        # 1. 最终共生度分布
        ax = axes[0]
        final_coordinations = [r['coordination_history'][-1] for r in trials_results]
        ax.hist(final_coordinations, bins=10, alpha=0.7, edgecolor='black')
        ax.set_xlabel('最终共生度')
        ax.set_ylabel('试验数量')
        ax.set_title(f'多次试验最终共生度分布 (平均={np.mean(final_coordinations):.3f})')
        ax.axvline(x=np.mean(final_coordinations), color='r', linestyle='--', label='平均值')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. 坤转次数分布
        ax = axes[1]
        kunzhuan_counts = [len(r.get('kunzhuan_events', [])) for r in trials_results]
        ax.hist(kunzhuan_counts,
                bins=range(min(kunzhuan_counts), max(kunzhuan_counts) + 2),
                alpha=0.7, edgecolor='black', align='left')
        ax.set_xlabel('坤转次数')
        ax.set_ylabel('试验数量')
        ax.set_title(f'多次试验坤转次数分布 (平均={np.mean(kunzhuan_counts):.2f})')
        ax.set_xticks(range(min(kunzhuan_counts), max(kunzhuan_counts) + 1))
        ax.grid(True, alpha=0.3)

        # 3. 最终权力比分布
        ax = axes[2]
        final_power_ratios = [r['power_ratio_history'][-1] for r in trials_results]
        ax.hist(final_power_ratios, bins=10, alpha=0.7, edgecolor='black')
        ax.set_xlabel('最终权力比 r')
        ax.set_ylabel('试验数量')
        ax.set_title(f'多次试验最终权力比分布')
        ax.axvline(x=1.0, color='r', linestyle='--', label='临界 r=1')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 4. 总原力增长分布
        ax = axes[3]
        total_force_growth = []
        for r in trials_results:
            initial = r['total_force_history'][0]
            final = r['total_force_history'][-1]
            growth = (final - initial) / initial if initial > 0 else 0
            total_force_growth.append(growth)

        ax.hist(total_force_growth, bins=10, alpha=0.7, edgecolor='black')
        ax.set_xlabel('总原力增长率')
        ax.set_ylabel('试验数量')
        ax.set_title(f'总原力增长分布 (平均={100 * np.mean(total_force_growth):.1f}%)')
        ax.axvline(x=np.mean(total_force_growth), color='r', linestyle='--', label='平均值')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig, axes