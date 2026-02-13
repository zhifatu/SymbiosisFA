__version__ = "1.0.0"
__author__ = "秩法图研究组"

# 导出测试类
from .philosophy_test import PhilosophicalConsistencyTestSuite
from .completeness_test import CompletenessTester
from .kunzhuan_test import KunzhuanValidator

__all__ = [
    'PhilosophicalConsistencyTestSuite',
    'CompletenessTester',
    'KunzhuanValidator'
]
src / primal_framework / __init__.py
或
primal_framework / __init__.py:

python
"""
秩法图框架 - 哲学计算化实现
"""

__version__ = "1.0.0"
__author__ = "秩法图研究组"
__description__ = "基于原力激发、目标追求、坤转指引三大公理的哲学计算框架"

# 核心哲学原理
PRINCIPLES = {
    'primal_excitation': '存在即原力激发',
    'target_pursuit': '消灭即目标追求',
    'kunzhuan_essence': '坤转是混沌指引非重建'
}

# 导出主要组件
from .models.primal_value import PrimalValue
from .models.life_state import LifeState, ExtinctionRecord

from .core.fields.primal_field import PrimalField
from .core.fields.target_field import TargetField
from .core.fields.mechanism_field import MechanismField
from .core.fields.chaos_field import ChaosField
from .core.fields.coordination_field import CoordinationField

from .simulator import FALawSimulator

__all__ = [
    # 模型
    'PrimalValue',
    'LifeState',
    'ExtinctionRecord',

    # 场系统
    'PrimalField',
    'TargetField',
    'MechanismField',
    'ChaosField',
    'CoordinationField',

    # 模拟器
    'FALawSimulator',

    # 常量
    'PRINCIPLES'
]