import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import time
from typing import Dict, Any, Optional, List
from .core import SystemState, DynamicsParameters, FALawDynamics
from .simulator import FALawSimulator


class FALawInteractive:
    """秩法图交互式参数调节器"""

    def __init__(self,
                 initial_params: Optional[DynamicsParameters] = None,
                 initial_state: Optional[SystemState] = None,
                 update_interval: float = 0.1):
        """
        初始化交互式调节器

        Args:
            initial_params: 初始参数
            initial_state: 初始状态
            update_interval: 更新间隔（秒）
        """
        self.params = initial_params or DynamicsParameters()
        self.initial_state = initial_state or SystemState(psi=np.full(8, 0.125))
        self.update_interval = update_interval

        # 创建模拟器
        self.simulator = FALawSimulator(
            initial_state=self.initial_state,
            params=self.params
        )

        # 模拟结果
        self.results = None

        # 图形组件
        self.fig = None
        self.axes = None
        self.sliders = {}
        self.buttons = {}

        # 预定义的参数调节范围
        self.param_ranges = {
            # 元素激发系数
            'gamma_0': (0.01, 0.2, 0.05, '乾定激发'),
            'gamma_1': (0.05, 0.3, 0.1, '射激发'),
            'gamma_2': (0.03, 0.2, 0.08, '陷激发'),
            'gamma_3': (0.05, 0.3, 0.12, '离激发'),
            'gamma_4': (0.02, 0.2, 0.06, '界激发'),
            'gamma_5': (0.03, 0.2, 0.07, '散激发'),
            'gamma_6': (0.05, 0.3, 0.15, '换激发'),
            'gamma_7': (0.005, 0.05, 0.01, '坤转激发'),

            # 关键参数
            'beta': (0.5, 5.0, 2.0, '平衡敏感性β'),
            'c0': (0.01, 0.2, 0.05, '收敛基础率c0'),
            'd0': (0.01, 0.2, 0.03, '发散基础率d0'),
            'kappa_power': (0.5, 3.0, 1.5, '收敛敏感性κ'),
            'lambda_power': (0.5, 3.0, 2.0, '发散敏感性λ'),

            # 坤转阈值
            'theta_immerse': (0.01, 0.2, 0.05, '陷场消散θ₃'),
            'theta_target': (0.005, 0.05, 0.01, '目标瓦解θ₁'),
            'theta_order': (0.1, 0.5, 0.2, '秩序崩溃θ_λ'),
            'theta_conflict': (0.2, 1.0, 0.5, '冲突指数θ_c'),

            # 元素能力参数
            'I_max': (0.1, 0.5, 0.3, '最大内在能力'),
            'kappa': (0.5, 2.0, 1.0, '可能性耦合κ'),
            'k_dissipate': (0.1, 0.5, 0.2, '消散率'),
            'k_coalesce': (0.05, 0.3, 0.1, '凝聚率'),
        }

        # 预设场景
        self.preset_scenarios = {
            '理想协调': self._create_ideal_params,
            '危机状态': self._create_crisis_params,
            '发散主导': self._create_divergence_params,
            '收敛主导': self._create_convergence_params,
            '高频坤转': self._create_high_kunzhuan_params,
            '稳定平衡': self._create_stable_params,
        }

        # 运行状态
        self.running = False
        self.animation = None

    def _create_ideal_params(self) -> Dict[str, float]:
        """创建理想协调态参数"""
        return {
            'gamma_0': 0.05, 'gamma_1': 0.1, 'gamma_2': 0.08,
            'gamma_3': 0.12, 'gamma_4': 0.06, 'gamma_5': 0.07,
            'gamma_6': 0.15, 'gamma_7': 0.01,
            'beta': 2.0, 'c0': 0.05, 'd0': 0.03,
            'kappa_power': 1.5, 'lambda_power': 2.0,
            'theta_immerse': 0.05, 'theta_target': 0.01,
            'theta_order': 0.2, 'theta_conflict': 0.5,
        }

    def _create_crisis_params(self) -> Dict[str, float]:
        """创建危机状态参数"""
        return {
            'gamma_0': 0.02, 'gamma_1': 0.05, 'gamma_2': 0.15,
            'gamma_3': 0.02, 'gamma_4': 0.1, 'gamma_5': 0.15,
            'gamma_6': 0.08, 'gamma_7': 0.05,
            'beta': 1.0, 'c0': 0.02, 'd0': 0.1,
            'kappa_power': 0.8, 'lambda_power': 2.5,
            'theta_immerse': 0.03, 'theta_target': 0.005,
            'theta_order': 0.15, 'theta_conflict': 0.3,
        }

    def _create_divergence_params(self) -> Dict[str, float]:
        """创建发散主导参数"""
        return {
            'gamma_5': 0.2, 'gamma_6': 0.1,  # 散和换更强
            'd0': 0.1, 'c0': 0.02,  # 发散强，收敛弱
            'lambda_power': 1.0, 'kappa_power': 3.0,  # 发散敏感，收敛迟钝
            'beta': 0.8,  # 平衡敏感性低
        }

    def _create_convergence_params(self) -> Dict[str, float]:
        """创建收敛主导参数"""
        return {
            'gamma_0': 0.1, 'gamma_4': 0.1,  # 乾定和界更强
            'c0': 0.1, 'd0': 0.02,  # 收敛强，发散弱
            'kappa_power': 0.8, 'lambda_power': 2.5,  # 收敛敏感，发散迟钝
            'beta': 3.0,  # 平衡敏感性高
            'theta_order': 0.3,  # 更容忍秩序波动
        }

    def _create_high_kunzhuan_params(self) -> Dict[str, float]:
        """创建高频坤转参数"""
        return {
            'gamma_7': 0.03,  # 坤转更容易激发
            'theta_immerse': 0.1, 'theta_target': 0.02,
            'theta_order': 0.15, 'theta_conflict': 0.3,
            'beta': 1.0,  # 平衡敏感性中等
            'c0': 0.03, 'd0': 0.05,  # 权力均衡
        }

    def _create_stable_params(self) -> Dict[str, float]:
        """创建稳定平衡参数"""
        return {
            'gamma_0': 0.06, 'gamma_4': 0.08, 'gamma_6': 0.12,  # 关键元素均衡
            'beta': 2.5,  # 高平衡敏感性
            'c0': 0.06, 'd0': 0.04,  # 轻微收敛优势
            'kappa_power': 2.0, 'lambda_power': 2.0,  # 敏感性均衡
            'theta_immerse': 0.06, 'theta_target': 0.015,
            'theta_order': 0.25, 'theta_conflict': 0.6,  # 宽容阈值
        }

    def create_widgets(self):
        """创建图形界面组件"""
        # 创建图形窗口
        self.fig = plt.figure(figsize=(16, 10))
        plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.35)

        # 创建主图表区域（3x2网格）
        self.axes = {
            'psi_plot': plt.subplot2grid((3, 2), (0, 0), colspan=2, rowspan=1),
            'coordination': plt.subplot2grid((3, 2), (1, 0)),
            'power_ratio': plt.subplot2grid((3, 2), (1, 1)),
            'force_radar': plt.subplot2grid((3, 2), (2, 0)),
            'phase_space': plt.subplot2grid((3, 2), (2, 1)),
        }

        # 创建滑块区域
        slider_height = 0.02
        slider_spacing = 0.03
        slider_y_start = 0.15

        # 第一行滑块：核心参数
        self._create_slider_row('beta', slider_y_start, '平衡敏感性β')
        self._create_slider_row('c0', slider_y_start - slider_spacing, '收敛基础率c0')
        self._create_slider_row('d0', slider_y_start - 2 * slider_spacing, '发散基础率d0')

        # 第二行滑块：坤转阈值
        self._create_slider_row('theta_immerse', 0.08, '陷场消散θ₃')
        self._create_slider_row('theta_target', 0.08 - slider_spacing, '目标瓦解θ₁')
        self._create_slider_row('theta_order', 0.08 - 2 * slider_spacing, '秩序崩溃θ_λ')

        # 添加预设场景按钮
        ax_preset = plt.axes([0.1, 0.02, 0.3, 0.06])
        self.preset_buttons = RadioButtons(
            ax_preset,
            list(self.preset_scenarios.keys()),
            active=0
        )
        self.preset_buttons.on_clicked(self.apply_preset)

        # 添加控制按钮
        ax_reset = plt.axes([0.55, 0.02, 0.1, 0.06])
        self.reset_button = Button(ax_reset, '重置模拟')
        self.reset_button.on_clicked(self.reset_simulation)

        ax_run = plt.axes([0.66, 0.02, 0.1, 0.06])
        self.run_button = Button(ax_run, '运行动画')
        self.run_button.on_clicked(self.toggle_animation)

        ax_export = plt.axes([0.77, 0.02, 0.1, 0.06])
        self.export_button = Button(ax_export, '导出参数')
        self.export_button.on_clicked(self.export_parameters)

        # 添加状态显示
        self.status_text = self.fig.text(
            0.45, 0.12,
            '就绪',
            fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )

        # 首次运行模拟
        self.run_simulation()
        self.update_plots()

    def _create_slider_row(self, param_name: str, y_pos: float, label: str):
        """创建单个滑块行"""
        if param_name not in self.param_ranges:
            return

        min_val, max_val, init_val, display_name = self.param_ranges[param_name]

        ax = plt.axes([0.25, y_pos, 0.65, 0.02])
        slider = Slider(
            ax=ax,
            label=display_name,
            valmin=min_val,
            valmax=max_val,
            valinit=init_val,
            valfmt='%.3f'
        )

        # 设置滑块事件
        def update_param(val):
            self._update_parameter(param_name, val)
            if self.running:
                self.run_simulation()
                self.update_plots()

        slider.on_changed(update_param)
        self.sliders[param_name] = slider

        # 显示当前值
        value_text = self.fig.text(
            0.92, y_pos + 0.01,
            f'{init_val:.3f}',
            fontsize=8,
            ha='center'
        )
        setattr(slider, 'value_text', value_text)

    def _update_parameter(self, param_name: str, value: float):
        """更新参数值"""
        # 更新滑块显示
        if param_name in self.sliders:
            self.sliders[param_name].value_text.set_text(f'{value:.3f}')

        # 更新参数对象
        if param_name.startswith('gamma_'):
            idx = int(param_name.split('_')[1])
            if 0 <= idx < len(self.params.gamma):
                self.params.gamma[idx] = value
        elif hasattr(self.params, param_name):
            setattr(self.params, param_name, value)

    def apply_preset(self, label):
        """应用预设场景"""
        if label in self.preset_scenarios:
            # 更新滑块值
            preset_values = self.preset_scenarios[label]()

            for param_name, value in preset_values.items():
                if param_name in self.sliders:
                    self.sliders[param_name].set_val(value)

            # 重置并运行
            self.reset_simulation(None)
            self.run_simulation()
            self.update_plots()

            self.status_text.set_text(f'应用预设: {label}')

    def reset_simulation(self, event):
        """重置模拟"""
        self.simulator = FALawSimulator(
            initial_state=self.initial_state,
            params=self.params
        )
        self.results = None
        self.status_text.set_text('模拟已重置')

    def run_simulation(self, duration: float = 50.0, dt: float = 0.05):
        """运行模拟"""
        try:
            # 确保使用当前参数
            self.simulator.params = self.params

            # 运行模拟
            self.results = self.simulator.run(
                duration=duration,
                dt=dt,
                progress_callback=None
            )

            self.status_text.set_text(
                f'模拟完成: S={self.results["coordination_history"][-1]:.3f}, '
                f'r={self.results["power_ratio_history"][-1]:.3f}'
            )

        except Exception as e:
            self.status_text.set_text(f'模拟错误: {str(e)}')
            import traceback
            traceback.print_exc()

    def update_plots(self):
        """更新所有图表"""
        if self.results is None:
            return

        # 清除所有图表
        for ax in self.axes.values():
            ax.clear()

        # 1. 元素强度演化图
        ax = self.axes['psi_plot']
        time_series = self.results['time_series']
        psi_history = self.results['psi_history']

        colors = plt.cm.Set3(np.linspace(0, 1, 8))
        for i in range(8):
            ax.plot(time_series, psi_history[:, i],
                    color=colors[i], linewidth=2, alpha=0.7)

        # 标记坤转事件
        kunzhuan_events = self.results.get('kunzhuan_events', [])
        for event in kunzhuan_events:
            ax.axvline(x=event['time'], color='red',
                       linestyle=':', alpha=0.5, linewidth=1)

        ax.set_xlabel('时间')
        ax.set_ylabel('元素强度 ψ')
        ax.set_title('八元素强度演化')
        ax.legend(['乾定', '射', '陷', '离', '界', '散', '换', '坤转'],
                  loc='upper right', ncol=4, fontsize=8)
        ax.grid(True, alpha=0.3)

        # 2. 共生度图
        ax = self.axes['coordination']
        ax.plot(time_series, self.results['coordination_history'],
                'b-', linewidth=2)
        ax.axhline(y=0.8, color='orange', linestyle='--', alpha=0.5,
                   label='健康阈值')
        ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5,
                   label='危机阈值')
        ax.set_xlabel('时间')
        ax.set_ylabel('共生度 S')
        ax.set_title('共生度演化')
        ax.set_ylim([0, 1])
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)

        # 3. 权力比图
        ax = self.axes['power_ratio']
        power_ratio = self.results['power_ratio_history']
        ax.plot(time_series, power_ratio, 'g-', linewidth=2)
        ax.axhline(y=1.0, color='r', linestyle='--', alpha=0.5,
                   label='临界 r=1')

        # 着色区域
        ax.fill_between(time_series, 0, 1,
                        where=np.array(power_ratio) < 1,
                        color='green', alpha=0.1, label='健康区域')
        ax.fill_between(time_series, 1, max(power_ratio) if len(power_ratio) > 0 else 2,
                        where=np.array(power_ratio) > 1,
                        color='red', alpha=0.1, label='危险区域')

        ax.set_xlabel('时间')
        ax.set_ylabel('权力比 r = P_d/P_c')
        ax.set_title('权力比演化 (公理D5)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        # 4. 雷达图（最终状态）
        ax = self.axes['force_radar']
        element_names = ['乾定', '射', '陷', '离', '界', '散', '换', '坤转']

        angles = np.linspace(0, 2 * np.pi, 8, endpoint=False).tolist()
        values = psi_history[-1, :].tolist()
        values += values[:1]  # 闭合
        angles += angles[:1]

        ax = plt.subplot2grid((3, 2), (2, 0), projection='polar')
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(element_names)
        ax.set_title(f'最终状态分布 (t={time_series[-1]:.1f})')
        ax.grid(True)

        # 5. 相空间图
        ax = self.axes['phase_space']
        ax.plot(psi_history[:, 0], psi_history[:, 1],
                'b-', alpha=0.3, linewidth=1)
        ax.scatter(psi_history[:, 0], psi_history[:, 1],
                   c=time_series, cmap='viridis', s=20, alpha=0.7)
        ax.set_xlabel('乾定强度 ψ₁')
        ax.set_ylabel('射强度 ψ₂')
        ax.set_title('乾定-射相平面')

        # 标记轨迹
        ax.scatter(psi_history[0, 0], psi_history[0, 1],
                   c='green', s=100, marker='o', label='起始', zorder=5)
        ax.scatter(psi_history[-1, 0], psi_history[-1, 1],
                   c='red', s=100, marker='s', label='结束', zorder=5)

        # 标记坤转点
        for event in kunzhuan_events:
            idx = np.argmin(np.abs(time_series - event['time']))
            if idx < len(psi_history):
                ax.scatter(psi_history[idx, 0], psi_history[idx, 1],
                           c='purple', s=80, marker='*', zorder=6)

        ax.legend()
        ax.grid(True, alpha=0.3)

        # 重绘图形
        plt.draw()

    def toggle_animation(self, event):
        """切换运行动画"""
        if not self.running:
            self.start_animation()
            self.run_button.label.set_text('停止动画')
        else:
            self.stop_animation()
            self.run_button.label.set_text('运行动画')

        self.running = not self.running
        plt.draw()

    def start_animation(self, duration_per_step: float = 5.0):
        """开始动画模拟"""

        def animate(frame):
            if not self.running:
                return

            # 运行一小段模拟
            self.run_simulation(duration=duration_per_step, dt=0.05)
            self.update_plots()

            # 更新状态
            if self.results:
                kunzhuan_count = len(self.results.get('kunzhuan_events', []))
                self.status_text.set_text(
                    f'动画运行中... 坤转次数: {kunzhuan_count}'
                )

        # 设置动画定时器
        self.animation_timer = self.fig.canvas.new_timer(
            interval=int(self.update_interval * 1000)
        )
        self.animation_timer.add_callback(animate)
        self.animation_timer.start()

    def stop_animation(self):
        """停止动画"""
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
            self.status_text.set_text('动画已停止')

    def export_parameters(self, event):
        """导出当前参数"""
        import json
        from datetime import datetime

        # 收集所有参数值
        params_dict = {
            'gamma': self.params.gamma.tolist(),
            'beta': float(self.params.beta),
            'c0': float(self.params.c0),
            'd0': float(self.params.d0),
            'kappa_power': float(self.params.kappa_power),
            'lambda_power': float(self.params.lambda_power),
            'theta_immerse': float(self.params.theta_immerse),
            'theta_target': float(self.params.theta_target),
            'theta_order': float(self.params.theta_order),
            'theta_conflict': float(self.params.theta_conflict),
            'I_max': float(self.params.I_max),
            'kappa': float(self.params.kappa),
            'k_dissipate': float(self.params.k_dissipate),
            'k_coalesce': float(self.params.k_coalesce),
            'timestamp': datetime.now().isoformat(),
            'final_coordination': float(self.results['coordination_history'][-1]) if self.results else 0,
            'final_power_ratio': float(self.results['power_ratio_history'][-1]) if self.results else 0,
        }

        # 保存到文件
        filename = f'falaw_params_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(params_dict, f, indent=2, ensure_ascii=False)

        self.status_text.set_text(f'参数已导出到 {filename}')

    def show(self):
        """显示交互界面"""
        self.create_widgets()
        plt.show()