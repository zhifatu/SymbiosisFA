import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("开始测试秩法图模拟器...")

try:
    # 直接导入修复后的模块
    from src.falaw.core import Element, SystemState, DynamicsParameters, FALawDynamics

    print("✓ 导入核心模块成功")

    # 测试Element类
    Element._init_elements()  # 手动初始化
    elements = Element.get_all()
    print(f"✓ 加载了 {len(elements)} 个元素:")
    for elem in elements:
        print(f"  {elem.id}: {elem.name} ({elem.symbol})")

    # 测试SystemState
    psi = np.full(8, 0.125)
    state = SystemState(psi=psi)
    print(f"✓ 创建系统状态: Φ={state.total_primal_force:.3f}, S={state.coordination_degree:.3f}")

    # 测试动力学
    params = DynamicsParameters()
    dynamics = FALawDynamics(params)

    print(f"✓ 创建动力学引擎: {len(params.gamma)} 个参数")

    # 运行几步模拟
    print("\n运行10步模拟测试...")
    current_state = state
    for i in range(10):
        new_state = dynamics.integrate_step(current_state, dt=0.1)
        print(f"  步 {i + 1}: t={new_state.time:.1f}, Φ={new_state.total_primal_force:.3f}, "
              f"S={new_state.coordination_degree:.3f}")
        current_state = new_state

    print("\n✓ 模拟测试成功！")

    # 运行完整模拟
    print("\n运行完整模拟...")
    from src.falaw.simulator import FALawSimulator
    from src.falaw.visualizer import FALawVisualizer

    sim = FALawSimulator()
    results = sim.run(duration=20.0, dt=0.05)

    print(f"模拟完成: {results['num_steps']} 步, "
          f"最终共生度: {results['coordination_history'][-1]:.3f}")

    # ============ 关键修改部分 ============
    # 1. 设置字体但不使用'Agg'后端
    import matplotlib

    # 设置英文字体，避免下标字符问题
    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False

    # 重新导入plt以确保设置生效
    import matplotlib.pyplot as plt

    # =====================================

    # 简单可视化
    plt.figure(figsize=(10, 6))

    # 共生度
    plt.subplot(2, 2, 1)
    plt.plot(results['time_series'], results['coordination_history'], 'b-')
    plt.xlabel('时间')
    plt.ylabel('共生度 S')
    plt.title('共生度演化')
    plt.grid(True, alpha=0.3)

    # 权力比
    plt.subplot(2, 2, 2)
    plt.plot(results['time_series'], results['power_ratio_history'], 'g-')
    plt.axhline(y=1.0, color='r', linestyle='--')
    plt.xlabel('时间')
    plt.ylabel('权力比 r')
    plt.title('权力比演化')
    plt.grid(True, alpha=0.3)

    # 总原力
    plt.subplot(2, 2, 3)
    plt.plot(results['time_series'], results['total_force_history'], 'r-')
    plt.xlabel('时间')
    plt.ylabel('总原力 Φ')
    plt.title('总原力演化')
    plt.grid(True, alpha=0.3)

    # 坤转强度 - 使用_8而不是下标₈
    plt.subplot(2, 2, 4)
    plt.plot(results['time_series'], results['psi_history'][:, 7], 'purple')
    plt.xlabel('时间')
    plt.ylabel('坤转强度 ψ_8')  # 关键修改：ψ₈ → ψ_8
    plt.title('坤转倾向')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    # 先保存文件
    plt.savefig('test_results.png', dpi=150)
    print(f"图表已保存为 test_results.png")

    # 再显示图表
    print("正在显示图表...")
    plt.show()

    print("\n✓ 所有测试通过！程序运行正常。")

except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)