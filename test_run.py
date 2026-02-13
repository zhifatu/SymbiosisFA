print("=" * 50)
print("秩法图项目测试 v1.0.0")
print("=" * 50)

# 1. 导入核心模块
print("\n1. 导入核心模块...")
try:
    # ✅ 修正：Element → ElementType
    from falaw.models.enums import ElementType

    print(f"   ✅ 成功: ElementType = {ElementType.QIAN.chinese}")

    # 测试 constants
    from falaw.core.constants import constants

    print(f"   ✅ 常数加载: 临界点 R={constants.CRITICAL_R}")

except Exception as e:
    print(f"   ❌ 失败: {e}")

# 2. 导入场类
print("\n2. 导入场类...")
try:
    from falaw.core.fields import (
        PrimalField,
        ChaosGuidanceField,
        IndividualCollectiveTargetField,
        MechanismCorrespondenceField,
        CoordinationField
    )

    print("   ✅ 成功: 所有五个核心场")
except Exception as e:
    print(f"   ❌ 失败: {e}")

# 3. 创建模拟器
print("\n3. 创建模拟器...")
try:
    from falaw.simulator import FALawSimulator

    sim = FALawSimulator()
    print(f"   ✅ 成功: 模拟器 ID = {sim.id if hasattr(sim, 'id') else 'default'}")

    # 测试 PrimalField 正确用法
    pf = PrimalField()
    # ✅ 修正：compute_excitation 只接受 pressure 参数
    result = pf.compute_excitation(pressure=0.3)
    print(f"   ✅ PrimalField 测试: 压力0.3 → 原力 {result:.3f}")

except Exception as e:
    print(f"   ❌ 失败: {e}")

# 4. 运行演示
print("\n4. 运行演示...")
try:
    if 'sim' in locals():
        from falaw.core.data_source import get_data_source

        ds = get_data_source()
        print(f"   ✅ DataSource 可用")
        print(f"   ✅ 坤转阈值: {ds.config['kunzhuan']['immerse_threshold']}")

        # 测试 ChaosField
        cf = ChaosGuidanceField()
        print(f"   ✅ ChaosField 可用")
    else:
        print("   ⚠️ 跳过: 模拟器未创建")
except Exception as e:
    print(f"   ❌ 失败: {e}")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)