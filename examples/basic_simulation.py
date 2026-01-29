import sys
import os
import matplotlib.pyplot as plt

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.falaw import FALawSimulator, FALawVisualizer, create_initial_state, save_results


def main():
    """基础模拟示例"""
    print("=" * 60)
    print("秩法图理论模拟器 - 快速开始")
    print("=" * 60)

    # 1. 创建初始状态（理想协调态）
    print("\n1. 初始化系统状态...")
    initial_state = create_initial_state('ideal')
    print(f"   初始共生度: {initial_state.coordination_degree:.3f}")
    print(f"   初始权力比: {initial_state.power_ratio:.3f}")

    # 2. 创建模拟器
    print("\n2. 创建模拟器...")
    simulator = FALawSimulator(initial_state=initial_state)

    # 3. 运行模拟
    print("\n3. 运行模拟 (时长=50, dt=0.01)...")
    results = simulator.run(duration=50.0, dt=0.01)

    # 4. 显示结果摘要
    print("\n4. 模拟结果摘要:")
    print(f"   模拟步数: {results['num_steps']}")
    print(f"   最终时间: {results['final_state'].time:.1f}")
    print(f"   最终共生度: {results['coordination_history'][-1]:.3f}")
    print(f"   最终权力比: {results['power_ratio_history'][-1]:.3f}")
    print(f"   坤转事件数: {len(results['kunzhuan_events'])}")

    if results['kunzhuan_events']:
        print("   坤转发生时间:",
              [f"t={e['time']:.1f}" for e in results['kunzhuan_events']])

    # 5. 可视化
    print("\n5. 生成可视化图表...")
    visualizer = FALawVisualizer()
    fig1, _ = visualizer.plot_state_evolution(results)

    if results['kunzhuan_events']:
        fig2, _ = visualizer.plot_kunzhuan_analysis(results)

    print("\n模拟完成! 显示图表中...")
    plt.show()

    # 6. 保存结果
    print("\n6. 保存结果到文件...")
    save_results(results, "simulation_results.json")
    print("   结果已保存到 simulation_results.json")


def run_crisis_scenario():
    """危机场景模拟"""
    print("\n" + "=" * 60)
    print("危机场景模拟")
    print("=" * 60)

    # 创建危机初始状态
    initial_state = create_initial_state('crisis')

    simulator = FALawSimulator(initial_state=initial_state)
    results = simulator.run(duration=100.0, dt=0.01)

    print(f"初始共生度: {initial_state.coordination_degree:.3f}")
    print(f"初始权力比: {initial_state.power_ratio:.3f}")
    print(f"最终共生度: {results['coordination_history'][-1]:.3f}")
    print(f"坤转事件数: {len(results['kunzhuan_events'])}")

    visualizer = FALawVisualizer()
    visualizer.plot_state_evolution(results)
    plt.show()


if __name__ == "__main__":
    main()

    # 可选：运行危机场景
    # run_crisis_scenario()