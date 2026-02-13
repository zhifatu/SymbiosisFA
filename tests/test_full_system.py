import sys
import os

# 添加 src 到 Python 路径
current_dir = os.path.dirname(__file__)
src_path = os.path.join(current_dir, "src")
sys.path.insert(0, src_path)

print("=" * 70)
print("秩法图完整系统测试")
print("=" * 70)
print(f"Python路径已添加: {src_path}")


# ========== 测试1：导入所有核心模块 ==========

def test_imports():
    """测试所有模块导入"""
    print("\n" + "=" * 50)
    print("测试1：模块导入")
    print("=" * 50)

    modules_to_test = [
        ("entities", ["LifeState", "PrimalValue", "Individual", "Collective", "Environment", "Phenomenon"]),
        ("primal_field", ["PrimalExcitationField"]),
    ]

    all_passed = True
    for module_name, classes in modules_to_test:
        print(f"\n📦 测试模块: {module_name}")

        if module_name == "entities":
            try:
                from primal_framework.models import entities
                print(f"  ✅ 导入成功")

                # 检查每个类
                for class_name in classes:
                    if hasattr(entities, class_name):
                        print(f"    ✅ {class_name}")
                    else:
                        print(f"    ❌ {class_name} 不存在")
                        all_passed = False

            except ImportError as e:
                print(f"  ❌ 导入失败: {e}")
                all_passed = False

        elif module_name == "primal_field":
            try:
                from primal_framework.core.primal_field import PrimalExcitationField
                print(f"  ✅ 导入成功")
                print(f"    ✅ PrimalExcitationField")

            except ImportError as e:
                print(f"  ❌ 导入失败: {e}")
                all_passed = False

    return all_passed


# ========== 测试2：创建和测试实体 ==========

def test_entities():
    """测试实体创建和基本功能"""
    print("\n" + "=" * 50)
    print("测试2：实体功能")
    print("=" * 50)

    try:
        from primal_framework.models.entities import (
            LifeState, PrimalValue, Individual,
            Collective, Environment
        )

        # 1. 测试 PrimalValue
        print("\n🔹 测试 PrimalValue")
        primal = PrimalValue(value=0.75)
        print(f"   值: {primal.value}")
        print(f"   确定性: {primal.certainty}")
        print(f"   有效值: {primal.effective_value}")

        # 2. 测试 Individual
        print("\n🔹 测试 Individual")
        person = Individual(
            id="alice",
            life_state=LifeState.ALIVE,
            primal_strength=primal,
            excitation_capacity=0.8
        )
        print(f"   ID: {person.id}")
        print(f"   生命状态: {person.life_state.value}")
        print(f"   是否可激发: {person.is_excitable}")

        # 测试目标追求
        target_result = person.pursue_target({
            'type': 'survival',
            'priority': 'high',
            'description': '生存目标'
        })
        print(f"   目标追求结果: {target_result['method']}")

        # 3. 测试 Environment
        print("\n🔹 测试 Environment")
        env = Environment(
            pressure_level=0.3,
            resource_abundance=0.7,
            stability=0.6
        )
        print(f"   环境压力: {env.pressure_level}")
        print(f"   是否在变化: {env.is_changing()}")

        # 4. 测试消灭（作为目标追求）
        print("\n🔹 测试消灭作为目标追求")
        bob = Individual(
            id="bob",
            life_state=LifeState.ALIVE,
            primal_strength=PrimalValue(0.5)
        )
        elimination_result = person.eliminate(bob, "资源竞争")
        print(f"   消灭结果: {elimination_result.get('success', False)}")
        print(f"   作为目标追求: {elimination_result.get('as_target_pursuit', False)}")
        print(f"   Bob的生命状态: {bob.life_state.value}")

        # 5. 测试 Collective
        print("\n🔹 测试 Collective")
        group = Collective(
            id="team_alpha",
            members=[person]
        )
        print(f"   集体ID: {group.id}")
        print(f"   成员数: {group.size}")
        print(f"   平均原力: {group.average_primal:.3f}")

        # 测试集体目标构建
        collective_result = group.construct_target("建立新秩序")
        print(f"   集体目标构建: {collective_result.get('field_cohesion_increase', 0)}")

        return True

    except Exception as e:
        print(f"\n❌ 实体测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


# ========== 测试3：测试原力场 ==========

def test_primal_field():
    """测试原力激发场"""
    print("\n" + "=" * 50)
    print("测试3：原力场功能")
    print("=" * 50)

    try:
        from primal_framework.models.entities import (
            LifeState, PrimalValue, Individual, Environment
        )
        from primal_framework.core.primal_field import PrimalExcitationField

        # 1. 创建测试对象
        print("\n🔹 创建测试对象")
        person = Individual(
            id="field_test",
            life_state=LifeState.ALIVE,
            primal_strength=PrimalValue(0.6),
            excitation_capacity=0.7
        )
        env = Environment(pressure_level=0.2, stability=0.8)
        field = PrimalExcitationField(id="test_field")

        print(f"   个体: {person.id}")
        print(f"   环境压力: {env.pressure_level}")
        print(f"   场ID: {field.id}")

        # 2. 测试原力激发计算
        print("\n🔹 测试原力激发计算")
        result = field.compute_excitation(person, env)

        print(f"   总激发水平: {result['total_excitation']:.3f}")
        print(f"   原力增加: {result['primal_increase']:.3f}")
        print(f"   个体新原力: {person.primal_strength.value:.3f}")
        print(f"   生存状态: {result['survival_status']['state']}")
        print(f"   哲学原则: {result['living_principle']}")

        # 3. 测试场维持检查
        print("\n🔹 测试场维持检查")
        maintained = field.is_maintained()
        print(f"   场是否能维持: {maintained}")

        # 4. 测试坤转触发
        print("\n🔹 测试坤转触发")
        kunzhuan = field.trigger_kunzhuan_if_needed()
        if kunzhuan:
            print(f"   ❗坤转触发: {kunzhuan['reason']}")
            print(f"   方法: {kunzhuan['kunzhuan_method']}")
            print(f"   原则: {kunzhuan['principle']}")
        else:
            print(f"   ✅ 场维持正常，无需坤转")

        # 5. 测试激发模式分析
        print("\n🔹 测试激发模式分析")
        # 模拟多次激发
        for _ in range(10):
            field.compute_excitation(person, env)

        pattern = field.analyze_excitation_patterns()
        print(f"   平均激发: {pattern['mean_excitation']:.3f}")
        print(f"   趋势: {pattern['trend']}")
        print(f"   生存保障: {pattern['survival_assurance']}")

        return True

    except Exception as e:
        print(f"\n❌ 原力场测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


# ========== 测试4：哲学原则验证 ==========

def test_philosophical_principles():
    """验证哲学原则"""
    print("\n" + "=" * 50)
    print("测试4：哲学原则验证")
    print("=" * 50)

    try:
        from primal_framework.models.entities import (
            LifeState, PrimalValue, Individual, Environment  # 添加 Environment 导入
        )
        from primal_framework.core.primal_field import PrimalExcitationField

        principles_tested = []

        # 原则1：活着就是原力激发
        print("\n🔹 原则1：活着就是原力激发")
        alive_person = Individual(
            id="alive_test",
            life_state=LifeState.ALIVE,
            primal_strength=PrimalValue(0.1)  # 很低但活着
        )
        extinct_person = Individual(
            id="extinct_test",
            life_state=LifeState.EXTINCT,
            primal_strength=PrimalValue(0.8)  # 高但已灭绝
        )

        env = Environment()  # 这里之前缺少导入
        field = PrimalExcitationField()

        # 计算激发
        alive_result = field.compute_excitation(alive_person, env)
        extinct_result = field.compute_excitation(extinct_person, env)

        print(f"   活着的激发: {alive_result['total_excitation']:.3f}")
        print(f"   灭绝的激发: {extinct_result['total_excitation']:.3f}")

        principle1_passed = alive_result['total_excitation'] > 0.1 and extinct_result['total_excitation'] < 0.1
        principles_tested.append(("活着就是原力激发", principle1_passed))

        # 原则2：消灭即目标追求
        print("\n🔹 原则2：消灭即目标追求")
        hunter = Individual(
            id="hunter",
            life_state=LifeState.ALIVE,
            primal_strength=PrimalValue(0.7)
        )
        prey = Individual(
            id="prey",
            life_state=LifeState.ALIVE,
            primal_strength=PrimalValue(0.4)
        )

        elimination = hunter.eliminate(prey, "生存竞争")

        print(f"   消灭是否成功: {elimination.get('success', False)}")
        print(f"   是否作为目标追求: {elimination.get('as_target_pursuit', False)}")

        principle2_passed = elimination.get('as_target_pursuit', False) == True
        principles_tested.append(("消灭即目标追求", principle2_passed))

        # 原则3：场无法维持时坤转
        print("\n🔹 原则3：场无法维持时坤转")
        weak_field = PrimalExcitationField(
            active_excitation=0.1,
            passive_excitation=0.1,
            maintenance_threshold=0.5
        )

        kunzhuan = weak_field.trigger_kunzhuan_if_needed()

        if kunzhuan:
            print(f"   坤转触发: {kunzhuan['reason']}")
            print(f"   方法: {kunzhuan['kunzhuan_method']}")
            print(f"   忽略残缺: {'ignore_fragmentation' in kunzhuan['principle']}")

        principle3_passed = kunzhuan is not None and 'guidance_from_chaos' in kunzhuan['kunzhuan_method']
        principles_tested.append(("场无法维持时坤转", principle3_passed))

        # 总结
        print("\n" + "-" * 40)
        print("哲学原则验证总结:")
        for principle, passed in principles_tested:
            status = "✅" if passed else "❌"
            print(f"   {status} {principle}")

        all_passed = all(passed for _, passed in principles_tested)
        return all_passed

    except Exception as e:
        print(f"\n❌ 哲学原则测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


# ========== 测试5：集成测试 ==========

def test_integration():
    """集成测试"""
    print("\n" + "=" * 50)
    print("测试5：集成测试")
    print("=" * 50)

    try:
        from primal_framework.models.entities import (
            LifeState, PrimalValue, Individual,
            Collective, Environment, Phenomenon
        )
        from primal_framework.core.primal_field import PrimalExcitationField

        print("🔹 创建完整场景...")

        # 1. 创建环境
        env = Environment(
            pressure_level=0.4,
            resource_abundance=0.6,
            stability=0.7
        )

        # 2. 创建个体
        individuals = []
        for i in range(3):
            person = Individual(
                id=f"person_{i}",
                life_state=LifeState.ALIVE,
                primal_strength=PrimalValue(0.5 + i * 0.1),
                excitation_capacity=0.6 + i * 0.1
            )
            individuals.append(person)

        # 3. 创建集体
        collective = Collective(
            id="test_collective",
            members=individuals
        )

        # 4. 创建原力场
        primal_field = PrimalExcitationField(id="main_field")

        print(f"   环境: 压力={env.pressure_level}, 稳定={env.stability}")
        print(f"   集体: {collective.id}, 成员={collective.size}")
        print(f"   原力场: {primal_field.id}")

        # 5. 运行一轮模拟
        print("\n🔹 运行模拟...")
        events = []

        # 个体激发
        for person in individuals:
            result = primal_field.compute_excitation(person, env)
            events.append({
                'type': 'excitation',
                'individual': person.id,
                'excitation': result['total_excitation']
            })

        # 集体构建目标
        target_result = collective.construct_target("共同生存")
        events.append({
            'type': 'collective_target',
            'collective': collective.id,
            'cohesion_increase': target_result['field_cohesion_increase']
        })

        # 创建现象
        phenomenon = Phenomenon(
            name="群体激发现象",
            description="多个个体在原力场中的协同激发",
            intensity=0.7,
            participants=individuals
        )
        events.append({
            'type': 'phenomenon',
            'name': phenomenon.name,
            'primal_intensity': phenomenon.primal_intensity
        })

        # 输出结果
        print("\n🔹 模拟结果:")
        for event in events:
            if event['type'] == 'excitation':
                print(f"   个体 {event['individual']} 激发: {event['excitation']:.3f}")
            elif event['type'] == 'collective_target':
                print(f"   集体目标构建，场凝聚力增加: {event['cohesion_increase']}")
            elif event['type'] == 'phenomenon':
                print(f"   现象 {event['name']}，原力强度: {event['primal_intensity']:.3f}")

        # 检查场状态
        print("\n🔹 场状态检查:")
        print(f"   场是否维持: {primal_field.is_maintained()}")

        kunzhuan = primal_field.trigger_kunzhuan_if_needed()
        if kunzhuan:
            print(f"   ❗坤转条件满足!")
        else:
            print(f"   ✅ 系统运行正常")

        return True

    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


# ========== 主测试流程 ==========

def main():
    """主测试函数"""
    test_results = []

    # 运行所有测试
    tests = [
        ("模块导入", test_imports),
        ("实体功能", test_entities),
        ("原力场功能", test_primal_field),
        ("哲学原则", test_philosophical_principles),
        ("集成测试", test_integration)
    ]

    for test_name, test_func in tests:
        print(f"\n🚀 开始测试: {test_name}")
        try:
            success = test_func()
            test_results.append((test_name, success))
            status = "✅ 通过" if success else "❌ 失败"
            print(f"   结果: {status}")
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
            test_results.append((test_name, False))

    # 测试总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)

    total_passed = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)

    print(f"\n📊 测试统计: {total_passed}/{total_tests} 通过")

    for test_name, success in test_results:
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}")

    if total_passed == total_tests:
        print("\n🎉 🎉 🎉 所有测试通过！秩法图框架可以正常工作了！")
        print("\n下一步:")
        print("  1. 运行示例: python examples/basic_usage.py")
        print("  2. 运行测试套件: python tests/run_all.py")
        print("  3. 开始你的研究!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} 个测试失败，需要修复")
        print("请查看上面的错误信息进行调试")


if __name__ == "__main__":
    main()