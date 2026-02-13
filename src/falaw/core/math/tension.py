"""秩法图理论：张力场计算引擎

本模块实现了系统张力场的量化计算。
包含 TensionFieldCalculator 类，提供：
- 结构张力（元素分布不均衡性）
- 动力张力（流动不均衡性）
- 势能张力（潜能与实际差距）
- 冲突张力（相互抑制强度）

依赖:
    - core.math.matrix.FundamentalFlowMatrix

理论依据:
    - 决策记录 002：8×8 矩阵设计
    - 公理 D3：陷场与张力
    - 公理 D4：坤转触发条件
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from falaw.core.math.matrix import FundamentalFlowMatrix
from falaw.models.enums import ElementType


@dataclass
class TensionResult:
    """张力计算结果容器"""
    value: float  # 张力值 [0,1]
    level: str  # 等级：极低/低/中/高/临界
    description: str  # 描述文本
    components: Dict  # 各分量详细数据


class TensionFieldCalculator:
    """张力场计算器

    该计算器从 8×8 流转矩阵和元素状态计算系统的四种张力：
    1. 结构张力 - 元素强度分布的不均衡性
    2. 动力张力 - 流动模式的不均衡性
    3. 势能张力 - 当前强度与最大潜能的差距
    4. 冲突张力 - 元素间相互抑制的不对称性

    参数
    ----------
    flow_matrix : FundamentalFlowMatrix
        8×8 直接流转矩阵

    属性
    ----------
    thresholds : Dict[str, float]
        张力等级阈值
        - 'low': 0.2
        - 'medium': 0.5
        - 'high': 0.7
        - 'critical': 0.9
    """

    def __init__(self, flow_matrix: FundamentalFlowMatrix):
        self.flow_matrix = flow_matrix

        # 张力等级阈值（与 DataSource.config 保持一致）
        self.thresholds = {
            'low': 0.2,
            'medium': 0.5,
            'high': 0.7,
            'critical': 0.9
        }

    def compute_tension_field(self, element_states: Dict[ElementType, float]) -> Dict[str, TensionResult]:
        """计算系统的完整张力场

        参数
        ----------
        element_states : Dict[ElementType, float]
            各元素的当前强度值，key为元素类型，value为强度[0,1]

        返回
        -------
        Dict[str, TensionResult]
            包含四种张力及总张力的计算结果
            - 'structural': 结构张力
            - 'dynamic': 动力张力
            - 'potential': 势能张力
            - 'conflict': 冲突张力
            - 'total': 加权总张力
        """

        tensions = {}

        # 1. 结构张力
        structural = self._compute_structural_tension(element_states)
        tensions['structural'] = self._package_result(
            'structural', structural, element_states
        )

        # 2. 动力张力
        dynamic = self._compute_dynamic_tension()
        tensions['dynamic'] = self._package_result(
            'dynamic', dynamic, element_states
        )

        # 3. 势能张力
        potential = self._compute_potential_tension(element_states)
        tensions['potential'] = self._package_result(
            'potential', potential, element_states
        )

        # 4. 冲突张力
        conflict = self._compute_conflict_tension()
        tensions['conflict'] = self._package_result(
            'conflict', conflict, element_states
        )

        # 5. 总张力（加权平均）
        weights = {'structural': 0.3, 'dynamic': 0.2,
                   'potential': 0.25, 'conflict': 0.25}

        total_value = 0.0
        for key, weight in weights.items():
            total_value += tensions[key].value * weight

        tensions['total'] = self._package_result(
            'total', total_value, element_states
        )

        return tensions

    def _compute_structural_tension(self, element_states: Dict[ElementType, float]) -> float:
        """计算结构张力：元素分布的不均衡性"""
        if not element_states:
            return 0.0

        intensities = list(element_states.values())
        intensities_array = np.array(intensities)
        mean_intensity = np.mean(intensities_array)

        if mean_intensity == 0:
            return 0.0

        # 使用变异系数衡量不均衡性
        cv = np.std(intensities_array) / mean_intensity
        return min(1.0, cv)

    def _compute_dynamic_tension(self) -> float:
        """计算动力张力：流动的不均衡性"""
        n = len(ElementType)
        outflow_imbalance = []

        for elem in ElementType:
            i = elem.index
            total_outflow = 1.0 - self.flow_matrix.matrix[i, i]
            outflow_imbalance.append(total_outflow)

        if len(outflow_imbalance) < 2:
            return 0.0

        imbalance_std = np.std(outflow_imbalance)
        max_possible_std = 0.5  # 理论最大标准差

        return min(1.0, imbalance_std / max_possible_std if max_possible_std > 0 else 0)

    def _compute_potential_tension(self, element_states: Dict[ElementType, float]) -> float:
        """计算势能张力：潜能与实际之间的差距"""
        if not element_states:
            return 0.0

        max_possible_intensity = 1.0
        actual_intensities = list(element_states.values())
        mean_actual = np.mean(actual_intensities)

        potential_gap = max_possible_intensity - mean_actual
        return min(1.0, potential_gap)

    def _compute_conflict_tension(self) -> float:
        """计算冲突张力：相互抑制的强度"""
        n = len(ElementType)
        conflict_sum = 0.0
        conflict_count = 0

        for i in range(n):
            for j in range(n):
                if i != j:
                    flow_ij = self.flow_matrix.matrix[i, j]
                    flow_ji = self.flow_matrix.matrix[j, i]

                    if flow_ij > 0.01 and flow_ji > 0.01:
                        symmetry = min(flow_ij, flow_ji) / max(flow_ij, flow_ji)
                        conflict = 1.0 - symmetry
                        conflict_sum += conflict
                        conflict_count += 1

        if conflict_count == 0:
            return 0.0

        avg_conflict = conflict_sum / conflict_count
        return min(1.0, avg_conflict)

    def _classify_tension_level(self, value: float) -> str:
        """分类张力等级"""
        if value < self.thresholds['low']:
            return '极低'
        elif value < self.thresholds['medium']:
            return '低'
        elif value < self.thresholds['high']:
            return '中'
        elif value < self.thresholds['critical']:
            return '高'
        else:
            return '临界'

    def _get_tension_description(self, tension_type: str, value: float) -> str:
        """获取张力描述文本"""
        descriptions = {
            'structural': [
                "结构均衡，系统稳定",
                "结构轻度不均衡，存在优化空间",
                "结构中度不均衡，需要调整",
                "结构严重不均衡，面临风险",
                "结构极度不均衡，濒临崩溃"
            ],
            'dynamic': [
                "流动平衡，动力充足",
                "流动轻度不平衡，动力稳定",
                "流动中度不平衡，需要调节",
                "流动严重不平衡，动力紧张",
                "流动极度不平衡，动力崩溃"
            ],
            'potential': [
                "潜能充分实现，发展空间小",
                "有适度发展潜能",
                "有较大发展潜能",
                "有巨大发展潜能",
                "潜能几乎未开发"
            ],
            'conflict': [
                "高度和谐，冲突极少",
                "轻度冲突，基本和谐",
                "中度冲突，需要协调",
                "严重冲突，紧张对立",
                "极度冲突，濒临对抗"
            ],
            'total': [
                "系统高度稳定，张力极低，但可能缺乏活力",
                "系统稳定，适度张力有利于发展",
                "系统张力适中，处于健康发展状态",
                "系统张力较高，需要关注和调节",
                "系统张力临界，面临重大变革压力"
            ]
        }

        level_idx = 0
        if value < self.thresholds['low']:
            level_idx = 0
        elif value < self.thresholds['medium']:
            level_idx = 1
        elif value < self.thresholds['high']:
            level_idx = 2
        elif value < self.thresholds['critical']:
            level_idx = 3
        else:
            level_idx = 4

        desc_list = descriptions.get(tension_type, ["未知状态"] * 5)
        return desc_list[level_idx]

    def _package_result(self, tension_type: str, value: float,
                        element_states: Dict) -> TensionResult:
        """封装张力计算结果"""
        return TensionResult(
            value=value,
            level=self._classify_tension_level(value),
            description=self._get_tension_description(tension_type, value),
            components={
                'raw_value': value,
                'thresholds': self.thresholds.copy(),
                'element_count': len(element_states)
            }
        )

    def get_kunzhuan_readiness(self, element_states: Dict[ElementType, float]) -> Dict[str, float]:
        """计算坤转准备度（用于 ChaosField）

        参数
        ----------
        element_states : Dict[ElementType, float]
            各元素的当前强度值

        返回
        -------
        Dict[str, float]
            - 'tension': 总张力值
            - 'readiness': 坤转准备度 [0,1]
            - 'threshold_crossed': 超过阈值的张力数量
        """
        tensions = self.compute_tension_field(element_states)
        total_tension = tensions['total'].value

        # 坤转准备度与总张力呈 S 型关系
        readiness = 1.0 / (1.0 + np.exp(-10 * (total_tension - 0.6)))

        # 统计超过阈值的张力数量
        threshold_crossed = 0
        for key in ['structural', 'dynamic', 'potential', 'conflict']:
            if tensions[key].value > self.thresholds['high']:
                threshold_crossed += 1

        return {
            'tension': total_tension,
            'readiness': readiness,
            'threshold_crossed': threshold_crossed
        }
