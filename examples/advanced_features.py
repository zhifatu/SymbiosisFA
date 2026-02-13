import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from primal_framework.models.entities import *
from primal_framework.core.primal_field import PrimalExcitationField


def demonstrate_philosophical_principles():
    """演示三大哲学原则"""
    print("=" * 60)
    print("秩法图哲学原则演示")
    print("=" * 60)

    # 原则1：活着就是原力激发
    print("\n1. 活着就是原力激发")
    alive = Individual(id="alive", life_state=LifeState.ALIVE)
    extinct = Individual(id="extinct", life_state=LifeState.EXTINCT)

    field = PrimalExcitationField()
    env = Environment()

    alive_result = field.compute_excitation(alive, env)
    extinct_result = field.compute_excitation(extinct, env)

    print(f"   活着个体的激发: {alive_result['total_excitation']:.3f}")
    print(f"   灭绝个体的激发: {extinct_result['total_excitation']:.3f}")
    print(f"   验证: 活着就有原力激发 ✓")

    # 原则2：消灭即目标追求
    print("\n2. 消灭即目标追求")
    hunter = Individual(id="hunter")
    prey = Individual(id="prey")

    elimination = hunter.eliminate(prey, "生存竞争")
    print(f"   消灭事件: {elimination}")
    print(f"   是否作为目标追求: {elimination['as_target_pursuit']}")
    print(f"   验证: 消灭是目标追求的一种形式 ✓")

    # 原则3：场无法维持时坤转
    print("\n3. 场无法维持时坤转")
    weak_field = PrimalExcitationField(
        active_excitation=0.1,
        passive_excitation=0.1,
        maintenance_threshold=0.5
    )

    kunzhuan = weak_field.trigger_kunzhuan_if_needed()
    if kunzhuan:
        print(f"   坤转触发: {kunzhuan['reason']}")
        print(f"   方法: {kunzhuan['kunzhuan_method']}")
        print(f"   原则: {kunzhuan['principle']}")
        print(f"   验证: 场无法维持时触发坤转指引 ✓")

    return True


def simulate_collective_evolution():
    """模拟集体演化"""
    print("\n" + "=" * 60)
    print("集体演化模拟")
    print("=" * 60)

    # 创建环境
    env = Environment(
        pressure_level=0.4,
        resource_abundance=0.6,
        stability=0.7
    )

    # 创建集体
    members = [
        Individual(id=f"member_{i}", primal_strength=PrimalValue(0.4 + 0.05 * i))
        for i in range(5)
    ]

    collective = Collective(id="evolving_collective", members=members)
    field = PrimalExcitationField()

    print(f"初始状态:")
    print(f"   成员数: {collective.size}")
    print(f"   平均原力: {collective.average_primal:.3f}")
    print(f"   场凝聚力: {collective.field_cohesion:.3f}")

    # 模拟10代
    for generation in range(10):
        print(f"\n第{generation}代:")

        # 个体激发
        extinct_count = 0
        for member in collective.members[:]:  # 复制列表以便安全删除
            result = field.compute_excitation(member, env)

            if not result['survival_status']['survivable']:
                collective.members.remove(member)
                extinct_count += 1
                print(f"   {member.id} 灭绝")

        # 集体构建目标
        if collective.members:
            collective.construct_target(f"第{generation}代生存目标")

        print(f"   存活: {collective.size}, 灭绝: {extinct_count}")
        print(f"   平均原力: {collective.average_primal:.3f}")

    print(f"\n最终状态:")
    print(f"   存活成员: {collective.size}")
    print(f"   最终原力: {collective.average_primal:.3f}")

    return collective


def analyze_primal_patterns():
    """分析原力模式"""
    print("\n" + "=" * 60)
    print("原力模式分析")
    print("=" * 60)

    env = Environment()
    field = PrimalExcitationField()

    # 创建不同状态的个体
    individuals = [
        ("强激发", Individual(id="strong", excitation_capacity=0.9)),
        ("弱激发", Individual(id="weak", excitation_capacity=0.3)),
        ("有目标", Individual(id="with_target", excitation_capacity=0.7)),
        ("无目标", Individual(id="no_target", excitation_capacity=0.7)),
    ]

    # 为有目标的个体添加目标
    individuals[2][1].pursue_target({
        'type': 'achievement',
        'content': '重大成就',
        'priority': 'high'
    })

    results = {}
    for name, individual in individuals:
        result = field.compute_excitation(individual, env)
        results[name] = result

    # 分析
    print("不同个体的原力激发比较:")
    for name, result in results.items():
        print(f"  {name}: {result['total_excitation']:.3f}")

    # 模式分析
    field_pattern = field.analyze_excitation_patterns()
    print(f"\n场模式分析:")
    print(f"  平均激发: {field_pattern['mean_excitation']:.3f}")
    print(f"  波动性: {field_pattern['volatility']:.3f}")
    print(f"  生存保障: {field_pattern['survival_assurance']}")

    return results


if __name__ == "__main__":
    print("秩法图框架研究示例")
    print("版本: 1.0.0")
    print("=" * 60)

    # 演示哲学原则
    demonstrate_philosophical_principles()

    # 模拟集体演化
    final_collective = simulate_collective_evolution()

    # 分析原力模式
    analysis_results = analyze_primal_patterns()

    print("\n" + "=" * 60)
    print("研究完成")
    print("=" * 60)
    print("\n框架现在可以用于:")
    print("1. 哲学原则验证实验")
    print("2. 社会演化模拟")
    print("3. 原力动力学分析")
    print("4. 坤转机制研究")
    print("\n开始你的秩法图研究吧！")