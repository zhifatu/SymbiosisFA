"""秩法图理论：目标追求与消灭合理性计算核心

本模块实现了目标因子计算、消灭合理性评估等数学逻辑。
所有数值公式集中在此，供 TargetField 调用。

依赖:
    - core.math.matrix.FundamentalFlowMatrix
    - core.math.indirect.IndirectInfluenceCalculator

理论依据:
    - 公理 D2：消灭即目标追求
    - 决策记录 001：V3_S型抑制（目标因子沿用相同哲学）
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from falaw.core.math.matrix import FundamentalFlowMatrix
from falaw.core.math.indirect import IndirectInfluenceCalculator


@dataclass
class TargetFactorResult:
    """目标因子计算结果"""
    value: float  # 目标因子 [0,1]
    clarity: float  # 目标清晰度
    priority_multiplier: float  # 优先级乘数
    n_targets: int  # 目标数量
    has_high_priority: bool


@dataclass
class EliminationJustification:
    """消灭合理性评估结果"""
    justified: bool
    score: float
    threshold: float
    components: Dict[str, float]
    primal_gain_expected: float


class TargetCalculator:
    """目标计算器

    提供目标因子计算、消灭合理性评估等核心数学功能。
    所有阈值从 DataSource.config 获取，不硬编码。
    """

    def __init__(self,
                 flow_matrix: FundamentalFlowMatrix,
                 config: Optional[Dict] = None):
        self.matrix = flow_matrix
        self.indirect = IndirectInfluenceCalculator(flow_matrix)

        # 默认配置（实际应由 DataSource 注入）
        self.config = config or {
            'target': {
                'base_factor': 0.5,  # 基础目标因子
                'clarity_per_target': 0.2,  # 每个目标清晰度贡献
                'high_priority_multiplier': 1.0,  # 高优先级乘数
                'low_priority_multiplier': 0.7,  # 低优先级乘数
                'max_target_factor': 1.0,  # 最大目标因子
                'zero_target_base': 0.8  # 无目标时基础激发
            },
            'elimination': {
                'base_justification': 0.8,  # 基础合理性
                'primal_gain_factor': 0.3,  # 原力增益系数
                'collective_bonus': 0.4,  # 集体利益加成
                'survival_multiplier': 2.0,  # 生存必要性乘数
                'threshold': 0.6  # 合理性阈值
            }
        }

    def compute_target_factor(self,
                              n_targets: int,
                              has_high_priority: bool) -> TargetFactorResult:
        """计算目标因子

        公式: factor = min(1.0, base + n_targets * clarity * priority)

        参数:
            n_targets: 当前目标数量
            has_high_priority: 是否有高优先级目标

        返回:
            TargetFactorResult 包含因子值和分量
        """
        cfg = self.config['target']

        if n_targets == 0:
            return TargetFactorResult(
                value=cfg['zero_target_base'],
                clarity=0.0,
                priority_multiplier=0.0,
                n_targets=0,
                has_high_priority=False
            )

        clarity = n_targets * cfg['clarity_per_target']
        priority = (cfg['high_priority_multiplier'] if has_high_priority
                    else cfg['low_priority_multiplier'])

        raw_factor = cfg['base_factor'] + clarity * priority
        value = min(cfg['max_target_factor'], raw_factor)

        return TargetFactorResult(
            value=value,
            clarity=clarity,
            priority_multiplier=priority,
            n_targets=n_targets,
            has_high_priority=has_high_priority
        )

    def compute_elimination_justification(self,
                                          agent_type: str,
                                          reason: str,
                                          agent_primal: float = 0.5,
                                          target_primal: float = 0.5,
                                          has_collective_benefit: bool = False) -> EliminationJustification:
        """计算消灭合理性

        参数:
            agent_type: 'Individual' 或 'Collective'
            reason: 消灭理由描述
            agent_primal: 执行者原力强度 [0,1]
            target_primal: 目标原力强度 [0,1]
            has_collective_benefit: 是否有集体利益

        返回:
            EliminationJustification 包含合理性判断和分数
        """
        cfg = self.config['elimination']

        # 基础分数
        base_score = cfg['base_justification']

        # 生存必要性加成
        survival_keywords = ['survival', 'defense', 'threat', 'protect', 'survive']
        if any(kw in reason.lower() for kw in survival_keywords):
            base_score *= cfg['survival_multiplier']

        # 预期原力增益
        expected_gain = (agent_primal * 0.5 + target_primal * 0.3)
        gain_contribution = expected_gain * cfg['primal_gain_factor']

        # 集体利益加成
        collective_bonus = cfg['collective_bonus'] if has_collective_benefit else 0.0
        if agent_type == 'Collective':
            collective_bonus += cfg['collective_bonus'] * 0.5  # 集体执行额外加成

        total_score = base_score + gain_contribution + collective_bonus
        justified = total_score > cfg['threshold']

        return EliminationJustification(
            justified=justified,
            score=total_score,
            threshold=cfg['threshold'],
            components={
                'base': base_score,
                'expected_gain': expected_gain,
                'gain_contribution': gain_contribution,
                'collective_bonus': collective_bonus
            },
            primal_gain_expected=expected_gain
        )

    def compute_eternal_target_effect(self,
                                      agent_type: str,
                                      current_primal: float) -> Dict[str, float]:
        """计算永恒目标参与效果

        永恒目标无法由个体直接达成，通过参与集体实现。
        个体参与获得原力增益，集体获得凝聚力提升。
        """
        if agent_type == 'Individual':
            primal_boost = 0.25  # 参与永恒目标获得显著原力提升
            cohesion_boost = 0.0
        else:  # Collective
            primal_boost = 0.1  # 集体整体原力提升
            cohesion_boost = 0.15  # 集体凝聚力提升

        return {
            'primal_boost': primal_boost,
            'cohesion_boost': cohesion_boost,
            'new_primal': min(1.0, current_primal + primal_boost)
        }

    def compute_collective_participation_effect(self,
                                                individual_primal: float,
                                                excitation_capacity: float = 0.8) -> float:
        """计算个体参与集体目标的原力增益"""
        boost = 0.15 * excitation_capacity
        return min(1.0, individual_primal + boost)

    def compute_target_loss_effects(self,
                                    n_targets_lost: int,
                                    current_cohesion: float,
                                    current_fragmentation: float) -> Dict[str, float]:
        """计算目标丧失的系统影响"""

        # 凝聚力损失：每个目标丧失减少 10% 凝聚力
        cohesion_loss = current_cohesion * 0.1 * n_targets_lost

        # 破碎度增加
        fragmentation_gain = 0.1 * n_targets_lost

        # 坤转风险
        kunzhuan_risk = min(1.0, fragmentation_gain * 2)

        return {
            'cohesion_loss': cohesion_loss,
            'fragmentation_gain': fragmentation_gain,
            'kunzhuan_risk': kunzhuan_risk,
            'new_cohesion': max(0.0, current_cohesion - cohesion_loss),
            'new_fragmentation': min(1.0, current_fragmentation + fragmentation_gain)
        }