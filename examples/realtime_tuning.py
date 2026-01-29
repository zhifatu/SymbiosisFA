import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.falaw import FALawSimulator, create_initial_state


class RealtimeTuner:
    """实时参数调节器（最小版本）"""

    def __init__(self):
        self.params_to_tune = [
            ('beta', '平衡敏感性', 0.5, 5.0, 2.0),
            ('c0', '收敛基础率', 0.01, 0.2, 0.05),
            ('d0', '发散基础率', 0.01, 0.2, 0.03),
            ('kappa_power', '收敛敏感性', 0.5, 3.0, 1.5),
            ('lambda_power', '发散敏感性', 0.5, 3.0, 2.0),
        ]

        self.fig = None
        self.axes = None
        self.sliders = {}
        self.simulator = None

    def setup(self):
        """设置界面"""
        self.fig, self.axes = plt.subplots(2, 3, figsize=(15, 8))
        plt.subplots_adjust(bottom=0.3)

        # 创建滑块
        slider_height = 0.03
        slider_width = 0.3
        slider_spacing = 0.05
        left_margin = 0.1

        for i, (param_name, label, min_val, max_val, init_val) in enumerate(self.params_to_tune):
            y_pos = 0.15 + i * slider_spacing
            ax = plt.axes([left_margin, y_pos, slider_width, slider_height])

            slider = Slider(
                ax=ax,
                label=label,
                valmin=min_val,
                valmax=max_val,
                valinit=init_val,
                valfmt='%.3f'
            )

            # 设置回调函数
            def update_simulation(val, pname=param_name):
                self.update_parameter(pname, val)
                self.run_and_plot()

            slider.on_changed(update_simulation)
            self.sliders[param_name] = slider

        # 创建模拟器
        self.simulator = FALawSimulator()

        # 初始运行
        self.run_and_plot()

    def update_parameter(self, param_name, value):
        """更新参数"""
        if hasattr(self.simulator.params, param_name):
            setattr(self.simulator.params, param_name, value)

    def run_and_plot(self, duration=30.0):
        """运行模拟并绘图"""
        # 重置模拟器
        self.simulator.reset()

        # 运行模拟
        results = self.simulator.run(duration=duration, dt=0.05)

        # 更新图表
        self.update_plots(results)

    def update_plots(self, results):
        """更新所有图表"""
        time_series = results['time_series']

        # 1. 共生度
        ax = self.axes[0, 0]
        ax.clear()
        ax.plot(time_series, results['coordination_history'], 'b-', linewidth=2)
        ax.set_xlabel('时间')
        ax.set_ylabel('共生度 S')
        ax.set_title('共生度演化')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1])

        # 2. 权力比
        ax = self.axes[0, 1]
        ax.clear()
        power_ratio = results['power_ratio_history']
        ax.plot(time_series, power_ratio, 'g-', linewidth=2)
        ax.axhline(y=1.0, color='r', linestyle='--', alpha=0.5)
        ax.set_xlabel('时间')
        ax.set_ylabel('权力比 r')
        ax.set_title('权力比演化')
        ax.grid(True, alpha=0.3)

        # 3. 总原力
        ax = self.axes[0, 2]
        ax.clear()
        ax.plot(time_series, results['total_force_history'], 'r-', linewidth=2)
        ax.set_xlabel('时间')
        ax.set_ylabel('总原力 Φ')
        ax.set_title('总原力演化')
        ax.grid(True, alpha=0.3)

        # 4. 元素强度（关键元素）
        ax = self.axes[1, 0]
        ax.clear()
        psi_history = results['psi_history']
        ax.plot(time_series, psi_history[:, 0], 'b-', label='乾定', alpha=0.8)
        ax.plot(time_series, psi_history[:, 1], 'g-', label='射', alpha=0.8)
        ax.plot(time_series, psi_history[:, 6], 'r-', label='换', alpha=0.8)
        ax.set_xlabel('时间')
        ax.set_ylabel('强度')
        ax.set_title('关键元素演化')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 5. 坤转强度
        ax = self.axes[1, 1]
        ax.clear()
        ax.plot(time_series, psi_history[:, 7], 'purple', linewidth=2)
        ax.set_xlabel('时间')
        ax.set_ylabel('坤转强度')
        ax.set_title('坤转倾向')
        ax.grid(True, alpha=0.3)

        # 6. 参数摘要
        ax = self.axes[1, 2]
        ax.clear()
        ax.axis('off')

        summary_text = (
            f"模拟结果摘要:\n"
            f"最终共生度: {results['coordination_history'][-1]:.3f}\n"
            f"最终权力比: {results['power_ratio_history'][-1]:.3f}\n"
            f"总原力变化: {results['total_force_history'][-1] / results['total_force_history'][0]:.2f}x\n"
            f"坤转事件: {len(results['kunzhuan_events'])}次\n"
            f"\n当前参数:\n"
            f"β = {self.simulator.params.beta:.2f}\n"
            f"c0 = {self.simulator.params.c0:.3f}\n"
            f"d0 = {self.simulator.params.d0:.3f}\n"
            f"κ = {self.simulator.params.kappa_power:.2f}\n"
            f"λ = {self.simulator.params.lambda_power:.2f}"
        )

        ax.text(0.1, 0.9, summary_text, fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.draw()

    def show(self):
        """显示界面"""
        self.setup()
        plt.show()


def main():
    """主函数"""
    print("实时参数调节器启动...")
    print("拖动滑块观察参数对系统的影响")

    tuner = RealtimeTuner()
    tuner.show()


if __name__ == "__main__":
    main()