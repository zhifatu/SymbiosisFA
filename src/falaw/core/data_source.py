from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

from falaw.core.math.matrix import FundamentalFlowMatrix
from falaw.core.math.indirect import IndirectInfluenceCalculator
from falaw.core.math.tension import TensionFieldCalculator
from falaw.core.math.expansion import PossibilityExpansionSystem
from falaw.models.enums import ElementType
from falaw.core.math.target import TargetCalculator


class DataSource:
    """秩法图核心数据源——五个场的唯一数据入口"""

    def __init__(self, config: Optional[Dict] = None):
        """初始化数据源"""

        # 1. 配置（使用传入的配置，否则使用默认配置）
        self.config = config or self._default_config()

        # 2. 初始化数学核心（严格按依赖顺序）
        self.matrix = FundamentalFlowMatrix()
        self.indirect = IndirectInfluenceCalculator(self.matrix)
        self.tension = TensionFieldCalculator(self.matrix)
        self.expansion = PossibilityExpansionSystem(self.matrix)

        # 3. 目标计算器（新增）
        self.target_calculator = TargetCalculator(self.matrix, self.config)

    def _default_config(self) -> Dict:
        """默认配置——所有阈值集中在这里"""
        return {
            # 坤转阈值（来自张力场研究）
            'kunzhuan': {
                'immerse_threshold': 0.05,  # θ₃ 陷场消散
                'target_gradient_threshold': 0.01,  # θ₁ 目标瓦解
                'order_collapse_threshold': 0.2,  # θ_λ 秩序崩溃
                'conflict_threshold': 0.5,  # θ_conflict 元素冲突
                'min_conditions': 3  # 最少满足条件数
            },
            # 原力激发参数（来自V3_S型抑制）
            'primal': {
                'base_excitation': 0.85,  # b
                'pressure_sensitivity': 0.80,  # s
                'adaptive_capacity': 0.69,  # a
                'resilience_factor': 1.89,  # r
                'sigmoid_steepness': 10.0  # k
            },
            # 权力动力学参数（来自公理D5）
            'power': {
                'c0': 0.05,  # 收敛贡献基础率
                'd0': 0.03,  # 发散耗散基础率
                'kappa': 1.5,  # 收敛敏感性
                'lambda': 2.0,  # 发散敏感性
                'r_critical': 1.0
            },
            # 目标计算参数（新增）
            'target': {
                'base_factor': 0.5,
                'clarity_per_target': 0.2,
                'high_priority_multiplier': 1.0,
                'low_priority_multiplier': 0.7,
                'max_target_factor': 1.0,
                'zero_target_base': 0.8
            },
            'elimination': {
                'base_justification': 0.8,
                'primal_gain_factor': 0.3,
                'collective_bonus': 0.4,
                'survival_multiplier': 2.0,
                'threshold': 0.6
            }
        }

    # ---------- 1. 矩阵数据 ----------
    def get_self_retention(self, element: ElementType) -> float:
        """获取元素的自我保留率 R[i,i]"""
        return self.matrix.matrix[element.index, element.index]

    def get_flow(self, source: ElementType, target: ElementType) -> float:
        """获取从source到target的流转比例"""
        return self.matrix.get_flow(source, target)

    def get_all_self_retentions(self) -> Dict[str, float]:
        """获取所有元素的自我保留率"""
        analysis = self.matrix.analyze_flow_patterns()
        return analysis['self_retention']

    # ---------- 2. 间接影响数据 ----------
    def get_total_influence(self, source_idx: int, target_idx: int) -> float:
        """获取总影响（含间接）"""
        result = self.indirect.compute_total_influence(source_idx, target_idx)
        return result['total_influence']

    def get_influence_matrix(self) -> np.ndarray:
        """获取总影响矩阵"""
        return self.indirect.compute_influence_matrix()

    # ---------- 3. 张力场数据 ----------
    def get_tension(self, element_states: Dict) -> Dict:
        """获取当前张力场"""
        return self.tension.compute_tension_field(element_states)

    def get_kunzhuan_thresholds(self) -> Dict:
        """获取坤转阈值（从配置读取）"""
        return self.config['kunzhuan']

    # ---------- 4. 可能性空间数据 ----------
    def get_possibility_space(self, element_states: Dict) -> np.ndarray:
        """获取可能性空间向量"""
        return self.expansion.compute_possibility_space(element_states)

    def get_expansion_potential(self, element_states: Dict, dimension: str) -> float:
        """获取特定维度的拓展潜力"""
        return self.expansion.compute_expansion_potential(element_states, dimension)

    # ---------- 5. 权力动力学数据 ----------
    def get_power_dynamics(self, power_ratio: float) -> Dict:
        """获取权力动力学计算结果"""
        from falaw.core.math.power import PowerDynamics
        pd = PowerDynamics(self.config['power'])
        dphi, r = pd.compute_growth_rate(power_ratio)
        return {
            'growth_rate': dphi,
            'power_ratio': r,
            'is_healthy': r < self.config['power']['r_critical']
        }

    # ---------- 6. 原力激发计算（V3_S型抑制）----------
    def compute_primal_excitation(self, pressure: float) -> float:
        """V3_S型抑制理论——秩法图数学核心"""
        p = pressure
        b = self.config['primal']['base_excitation']
        s = self.config['primal']['pressure_sensitivity']
        a = self.config['primal']['adaptive_capacity']
        r = self.config['primal']['resilience_factor']
        k = self.config['primal']['sigmoid_steepness']

        # S型抑制（V3核心公式）
        suppression = 1 / (1 + np.exp(-k * (s * p - 1)))

        # 有界适应
        if p < 0.7:
            adapt_gain = min(0.3, a * (1 - np.exp(-r * p)))
        else:
            adapt_gain = a * (1 - np.exp(-r * p)) * (1 - (p - 0.7) / 0.3)

        adaptation = 1 + max(0, adapt_gain)

        # 综合激发
        excitation = b * (1 - 0.8 * suppression) * adaptation
        return max(0.05, min(1.2, excitation))

    # ---------- 7. 目标计算接口（新增）-----------
    def compute_target_factor(self, n_targets: int, has_high_priority: bool) -> float:
        """计算目标因子"""
        result = self.target_calculator.compute_target_factor(n_targets, has_high_priority)
        return result.value

    def compute_elimination_justification(self,
                                          agent_type: str,
                                          reason: str,
                                          agent_primal: float = 0.5,
                                          target_primal: float = 0.5,
                                          has_collective_benefit: bool = False) -> Dict:
        """计算消灭合理性"""
        result = self.target_calculator.compute_elimination_justification(
            agent_type, reason, agent_primal, target_primal, has_collective_benefit
        )
        return {
            'justified': result.justified,
            'score': result.score,
            'threshold': result.threshold,
            'components': result.components
        }


# 全局单例（整个系统共用一个数据源）
_DATA_SOURCE = None


def get_data_source(config: Optional[Dict] = None) -> DataSource:
    """获取全局数据源单例"""
    global _DATA_SOURCE
    if _DATA_SOURCE is None:
        _DATA_SOURCE = DataSource(config)
    return _DATA_SOURCE


def reset_data_source():
    """重置数据源（仅用于测试）"""
    global _DATA_SOURCE
    _DATA_SOURCE = None