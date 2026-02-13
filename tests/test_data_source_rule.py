import inspect
from falaw.core.fields import (
    PrimalField, TargetField, MechanismField,
    ChaosField, CoordinationField
)
from falaw.core.data_source import DataSource, get_data_source, reset_data_source


def test_no_hardcoded_thresholds():
    """测试1：场中不应有硬编码阈值"""

    fields = [
        PrimalField(),
        TargetField(),
        MechanismField(),
        ChaosField(),
        CoordinationField()
    ]

    forbidden_patterns = [
        '0.05', '0.01', '0.2', '0.5',  # 坤转阈值
        '0.8', '0.85', '0.69', '1.89',  # 原力参数
        'self.theta_', 'params.theta_'
    ]

    for field in fields:
        source = inspect.getsource(field.__class__)
        for pattern in forbidden_patterns:
            assert pattern not in source, \
                f"{field.__class__.__name__} 包含硬编码阈值: {pattern}"


def test_all_numeric_data_from_datasource():
    """测试2：所有数值数据必须从 DataSource 获取"""

    # 重置数据源，确保使用真实实例
    reset_data_source()
    data = get_data_source()

    # 测试 PrimalField
    pf = PrimalField()
    # 它应该调用 data.compute_primal_excitation，而不是自己算
    excitation = pf.compute_excitation(None, 0.3)

    # 验证结果与数据源一致
    assert excitation == data.compute_primal_excitation(0.3), \
        "PrimalField 使用了自创公式"

    # 测试 ChaosField
    cf = ChaosField()
    thresholds = cf.data.get_kunzhuan_thresholds()

    # 验证阈值来自配置，不是硬编码
    assert thresholds['immerse_threshold'] == 0.05, \
        "阈值应与配置文件一致"