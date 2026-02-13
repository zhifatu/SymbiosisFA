from falaw.core.data_source import get_data_source
from falaw.core.fields import PrimalField, ChaosGuidanceField
from falaw.core.fields import IndividualCollectiveTargetField
from falaw.core.fields import MechanismCorrespondenceField, CoordinationField

print('=' * 60)
print('秩法图核心架构验证测试')
print('=' * 60)

# 1. 测试 DataSource
print('\n1. 测试 DataSource...')
ds = get_data_source()
assert ds is not None
print('   ✅ DataSource 单例创建成功')
print(f'   ✅ 坤转阈值: {ds.config["kunzhuan"]["immerse_threshold"]}')
print(f'   ✅ 原力参数: b={ds.config["primal"]["base_excitation"]}, s={ds.config["primal"]["pressure_sensitivity"]}')

# 2. 测试五个核心场初始化
print('\n2. 测试五个核心场初始化...')
pf = PrimalField()
cf = ChaosGuidanceField()
tf = IndividualCollectiveTargetField()
mf = MechanismCorrespondenceField()
cof = CoordinationField()
print('   ✅ PrimalField 初始化成功')
print('   ✅ ChaosGuidanceField 初始化成功')
print('   ✅ TargetField 初始化成功')
print('   ✅ MechanismField 初始化成功')
print('   ✅ CoordinationField 初始化成功')

# 3. 验证每个场都接入 DataSource
print('\n3. 验证 DataSource 接入...')
assert hasattr(pf, 'data'), 'PrimalField 未接入 DataSource'
assert hasattr(cf, 'data'), 'ChaosField 未接入 DataSource'
assert hasattr(tf, 'data'), 'TargetField 未接入 DataSource'
assert hasattr(mf, 'data'), 'MechanismField 未接入 DataSource'
assert hasattr(cof, 'data'), 'CoordinationField 未接入 DataSource'
print('   ✅ 所有场均已接入 DataSource')

# 4. 测试基本功能调用
print('\n4. 测试基本功能调用...')
excitation = pf.compute_excitation(None, pressure=0.3)
print(f'   ✅ PrimalField.compute_excitation(0.3) = {excitation:.3f}')

thresholds = cf.kunzhuan_config
print(f'   ✅ ChaosField 坤转阈值: {thresholds["min_conditions"]}个条件')

primal_boost = tf.calculator.compute_eternal_target_effect('Individual', 0.5)
print(f'   ✅ TargetField 永恒目标效果: 原力+{primal_boost["primal_boost"]}')

print('\n' + '=' * 60)
print('🎉 秩法图核心架构验证通过！')
print('=' * 60)