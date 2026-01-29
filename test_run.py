import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 首先测试导入
try:
    from src.falaw import FALawSimulator, create_initial_state
    print("✓ 导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 运行简单测试
print("\n运行简单模拟测试...")
try:
    sim = FALawSimulator()
    results = sim.run(duration=10.0, dt=0.1)
    print(f"✓ 模拟成功运行")
    print(f"  步数: {results['num_steps']}")
    print(f"  最终共生度: {results['coordination_history'][-1]:.3f}")
    print(f"  最终权力比: {results['power_ratio_history'][-1]:.3f}")
except Exception as e:
    print(f"✗ 模拟失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ 所有测试通过！程序可以正常运行。")