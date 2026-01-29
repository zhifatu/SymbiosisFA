import sys
import os
import matplotlib

# 设置matplotlib后端
matplotlib.use('TkAgg')  # 或 'Qt5Agg', 'WXAgg'

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.falaw.interactive import FALawInteractive


def main():
    """主函数：启动交互式界面"""
    print("=" * 60)
    print("秩法图交互式参数调节器")
    print("=" * 60)
    print("\n使用说明:")
    print("1. 调整滑块改变参数值")
    print("2. 点击'运行动画'开始实时模拟")
    print("3. 选择预设场景快速切换参数")
    print("4. 点击'重置模拟'重新开始")
    print("5. 点击'导出参数'保存当前配置")
    print("\n图表说明:")
    print("- 上方: 八元素强度演化")
    print("- 左中: 共生度演化 (蓝色线)")
    print("- 右中: 权力比演化 (绿色线)")
    print("- 左下: 最终状态雷达图")
    print("- 右下: 乾定-射相平面图")
    print("=" * 60)

    # 创建交互式界面
    interactive = FALawInteractive(update_interval=0.2)

    # 显示界面
    interactive.show()


def quick_test():
    """快速测试交互功能"""
    print("\n快速测试交互功能...")

    from src.falaw.interactive import FALawInteractive
    import matplotlib.pyplot as plt

    # 创建较小的界面用于测试
    interactive = FALawInteractive(update_interval=0.3)

    # 创建简化的界面
    interactive.fig = plt.figure(figsize=(14, 8))
    plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.4)

    # 只创建必要的图表
    interactive.axes = {
        'coordination': plt.subplot2grid((2, 2), (0, 0)),
        'power_ratio': plt.subplot2grid((2, 2), (0, 1)),
        'psi_plot': plt.subplot2grid((2, 2), (1, 0), colspan=2),
    }

    # 只添加关键滑块
    slider_height = 0.02
    slider_y_start = 0.25

    # 核心参数滑块
    param_defs = [
        ('beta', 0.25, '平衡敏感性β', (0.5, 5.0)),
        ('c0', 0.22, '收敛基础率', (0.01, 0.2)),
        ('d0', 0.19, '发散基础率', (0.01, 0.2)),
        ('theta_immerse', 0.16, '陷场阈值', (0.01, 0.2)),
    ]

    interactive.sliders = {}
    for param_name, y_pos, label, (min_val, max_val) in param_defs:
        ax = plt.axes([0.25, y_pos, 0.65, slider_height])
        slider = matplotlib.widgets.Slider(
            ax=ax,
            label=label,
            valmin=min_val,
            valmax=max_val,
            valinit=getattr(interactive.params, param_name),
            valfmt='%.3f'
        )

        def update_param(val, pname=param_name):
            setattr(interactive.params, pname, val)
            interactive.run_simulation(duration=30.0)
            interactive.update_plots()

        slider.on_changed(update_param)
        interactive.sliders[param_name] = slider

    # 运行初始模拟
    interactive.run_simulation(duration=30.0)
    interactive.update_plots()

    # 添加状态显示
    interactive.status_text = interactive.fig.text(
        0.5, 0.35,
        '就绪 - 拖动滑块观察系统变化',
        ha='center',
        fontsize=11,
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7)
    )

    print("\n界面已启动!")
    print("拖动任意滑块观察系统响应的实时变化")
    print("关闭窗口退出")

    plt.show()


if __name__ == "__main__":
    # 运行完整界面
    main()

    # 或运行快速测试
    # quick_test()