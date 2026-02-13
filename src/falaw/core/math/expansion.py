"""秩法图理论：可能性空间计算核心

本模块实现了可能性空间的量化与拓展潜力计算。
包含 PossibilityExpansionSystem 类，提供：
- 6维可能性空间定义
- 各元素对维度的贡献权重
- 最优拓展路径分析

依赖:
    - core.math.matrix.FundamentalFlowMatrix

理论依据:
    - 决策记录 001：V3_S型抑制
    - 公理 S3：可能性场
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from falaw.core.math.matrix import FundamentalFlowMatrix
from falaw.models.enums import ElementType


@dataclass
class PossibilityVector:
    """可能性空间向量"""
    stability: float  # 稳定性维度
    flexibility: float  # 灵活性维度
    diversity: float  # 多样性维度
    connectivity: float  # 连接性维度
    novelty: float  # 新颖性维度
    efficiency: float  # 效率维度

    def to_array(self) -> np.ndarray:
        """转换为numpy数组"""
        return np.array([
            self.stability,
            self.flexibility,
            self.diversity,
            self.connectivity,
            self.novelty,
            self.efficiency
        ])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'PossibilityVector':
        """从numpy数组创建"""
        return cls(
            stability=arr[0],
            flexibility=arr[1],
            diversity=arr[2],
            connectivity=arr[3],
            novelty=arr[4],
            efficiency=arr[5]
        )


class PossibilityExpansionSystem:
    """可能性拓展系统

    将八元素状态映射到6维可能性空间，计算各维度拓展潜力。

    参数
    ----------
    flow_matrix : FundamentalFlowMatrix
        8×8直接流转矩阵

    属性
    ----------
    dimensions : Dict[str, int]
        维度名称到索引的映射
    element_contribution : Dict[ElementType, List[float]]
        每个元素对6个维度的贡献权重
    """

    def __init__(self, flow_matrix: FundamentalFlowMatrix):
        self.flow_matrix = flow_matrix

        # 可能性空间的基础维度
        self.dimensions = {
            'stability': 0,  # 稳定性维度
            'flexibility': 1,  # 灵活性维度
            'diversity': 2,  # 多样性维度
            'connectivity': 3,  # 连接性维度
            'novelty': 4,  # 新颖性维度
            'efficiency': 5  # 效率维度
        }

        # 每个元素对可能性维度的贡献权重
        self.element_contribution = {
            ElementType.QIAN: [0.8, 0.2, 0.1, 0.3, 0.1, 0.6],  # 乾定：高稳定性、效率
            ElementType.SHE: [0.3, 0.7, 0.6, 0.4, 0.8, 0.4],  # 射：高灵活性、多样性、新颖性
            ElementType.XIAN: [0.6, 0.1, 0.2, 0.5, 0.3, 0.3],  # 陷：高稳定性、连接性
            ElementType.LI: [0.1, 0.9, 0.7, 0.2, 0.6, 0.2],  # 离：高灵活性、多样性、新颖性
            ElementType.JIE: [0.7, 0.4, 0.3, 0.6, 0.2, 0.5],  # 界：高稳定性、连接性、效率
            ElementType.SAN: [0.2, 0.8, 0.9, 0.7, 0.5, 0.3],  # 散：高灵活性、多样性、连接性
            ElementType.HUAN: [0.4, 0.6, 0.8, 0.9, 0.4, 0.7],  # 换：高多样性、连接性、效率
            ElementType.KUN: [0.1, 0.9, 0.5, 0.3, 0.9, 0.2]  # 坤转：高灵活性、新颖性
        }

    def compute_possibility_space(self,
                                  element_states: Dict[ElementType, float]) -> np.ndarray:
        """计算当前系统的可能性空间向量

        参数
        ----------
        element_states : Dict[ElementType, float]
            各元素的当前强度值，key为元素类型，value为强度[0,1]

        返回
        -------
        np.ndarray
            6维可能性空间向量，各维度范围[0,1]
        """
        n_dim = len(self.dimensions)
        possibility_vector = np.zeros(n_dim)
        total_weight = 0.0

        for elem, strength in element_states.items():
            if elem in self.element_contribution:
                contribution = np.array(self.element_contribution[elem])
                weight = strength
                possibility_vector += contribution * weight
                total_weight += weight

        # 归一化
        if total_weight > 0:
            possibility_vector = possibility_vector / total_weight
        else:
            possibility_vector = np.zeros(n_dim)

        return possibility_vector

    def compute_expansion_potential(self,
                                    element_states: Dict[ElementType, float],
                                    target_dimension: str) -> float:
        """计算在特定维度上的拓展潜力

        参数
        ----------
        element_states : Dict[ElementType, float]
            各元素的当前强度值
        target_dimension : str
            目标维度名称（stability/flexibility/diversity/connectivity/novelty/efficiency）

        返回
        -------
        float
            拓展潜力值 [0,1]
        """
        if target_dimension not in self.dimensions:
            return 0.0

        dim_idx = self.dimensions[target_dimension]

        # 当前在该维度上的强度
        current_space = self.compute_possibility_space(element_states)
        current_strength = current_space[dim_idx]

        # 计算最大潜力（如果所有元素都最大化贡献该维度）
        max_potential = 0.0
        for elem in ElementType:
            if elem in self.element_contribution:
                max_contribution = self.element_contribution[elem][dim_idx]
                max_potential += max_contribution

        max_potential /= len(ElementType)  # 平均化

        # 潜力 = (最大潜力 - 当前强度) / 最大潜力
        if max_potential > 0:
            potential = (max_potential - current_strength) / max_potential
        else:
            potential = 0.0

        return max(0.0, min(1.0, potential))

    def find_optimal_expansion_path(self,
                                    element_states: Dict[ElementType, float],
                                    target_dimension: str) -> List[Dict]:
        """寻找最优的拓展路径

        参数
        ----------
        element_states : Dict[ElementType, float]
            各元素的当前强度值
        target_dimension : str
            目标维度名称

        返回
        -------
        List[Dict]
            按提升空间排序的优化路径列表
        """
        dim_idx = self.dimensions[target_dimension]
        paths = []

        # 分析每个元素对该维度的贡献
        for elem in ElementType:
            if elem not in element_states:
                continue

            current_strength = element_states[elem]
            current_intensity = current_strength if isinstance(current_strength, (int, float)) else 0.5

            # 该元素的贡献能力
            if elem in self.element_contribution:
                contribution_ability = self.element_contribution[elem][dim_idx]
            else:
                contribution_ability = 0.0

            # 当前贡献
            current_contribution = contribution_ability * current_intensity

            # 最大可能贡献
            max_contribution = contribution_ability * 1.0

            # 提升空间
            improvement_space = max_contribution - current_contribution

            if improvement_space > 0.01:  # 忽略微小提升
                paths.append({
                    'target_element': elem.chinese_name,
                    'current_contribution': float(current_contribution),
                    'max_contribution': float(max_contribution),
                    'improvement_space': float(improvement_space),
                    'contribution_ability': float(contribution_ability)
                })

        # 按提升空间排序
        paths.sort(key=lambda x: x['improvement_space'], reverse=True)
        return paths[:5]  # 返回前5条最优路径

    def get_dimension_names(self) -> List[str]:
        """获取所有维度名称"""
        return list(self.dimensions.keys())


# 为旧代码提供别名
PossibilitySystem = PossibilityExpansionSystem

__all__ = ['PossibilityExpansionSystem', 'PossibilitySystem', 'PossibilityVector']