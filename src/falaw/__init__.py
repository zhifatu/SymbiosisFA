from .core import (
    Element,
    SystemState,
    DynamicsParameters,
    FALawDynamics
)

from .simulator import FALawSimulator
from .visualizer import FALawVisualizer
from .utils import (
    create_initial_state,
    save_results,
    load_results,
    analyze_stability
)

from .interactive import FALawInteractive

# 在 __all__ 中添加
__all__ = [
    # ... 原有导入 ...
    "FALawInteractive",  # 新增
]

__version__ = "1.0.0"
__author__ = "秩法图理论研究组"

__all__ = [
    # 核心类
    "Element",
    "SystemState",
    "DynamicsParameters",
    "FALawDynamics",

    # 模拟器
    "FALawSimulator",

    # 可视化
    "FALawVisualizer",

    # 工具函数
    "create_initial_state",
    "save_results",
    "load_results",
    "analyze_stability"
]