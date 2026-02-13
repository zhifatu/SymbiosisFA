"""秩法图理论：间接影响计算核心

本模块实现了从直接流转矩阵到多阶间接影响的完整计算链。
包含 IndirectInfluenceCalculator 类，提供：
- 直接/间接影响分离
- 主导路径分析
- 全影响矩阵生成

依赖:
    - core.math.matrix.FundamentalFlowMatrix

理论依据:
    - 决策记录 002：8×8矩阵设计
    - 公理 D2：原力流动守恒
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from falaw.core.math.matrix import FundamentalFlowMatrix


class IndirectInfluenceCalculator:
    """间接影响计算器（矩阵幂次法）

    该计算器将直接流转矩阵扩展为包含间接影响的完整影响网络。
    使用衰减因子 γ=0.7^(n-1) 对高阶影响进行加权。

    参数
    ----------
    flow_matrix : FundamentalFlowMatrix
        8×8直接流转矩阵，必须满足行和为1、对角线≥0.5

    属性
    ----------
    direct_matrix : np.ndarray
        直接流转矩阵（只读）
    power_matrices : Dict[int, np.ndarray]
        各阶间接影响矩阵缓存
    """

    def __init__(self, flow_matrix: FundamentalFlowMatrix):
        self.flow_matrix = flow_matrix
        self.direct_matrix = flow_matrix.matrix

        # 计算幂次流转矩阵（用于间接影响）
        self._compute_power_matrices()

    def _compute_power_matrices(self, max_order: int = 5):
        """计算流转矩阵的幂次"""
        self.power_matrices = {
            1: self.direct_matrix,  # 直接影响
        }

        # 计算到max_order阶间接影响
        for k in range(2, max_order + 1):
            self.power_matrices[k] = np.linalg.matrix_power(self.direct_matrix, k)

    def compute_total_influence(self,
                                source_idx: int,
                                target_idx: int,
                                max_order: int = 3) -> Dict[str, float]:
        """
        计算从源到目标的总影响（包括间接）

        参数
        ----------
        source_idx : int
            源元素索引 (0-7)
        target_idx : int
            目标元素索引 (0-7)
        max_order : int, default=3
            最大间接阶数，取值范围[1,5]

        返回
        -------
        Dict[str, float]
            - 'total_influence': 归一化总影响 [0,1]
            - 'direct_influence': 直接影响
            - 'indirect_influences': 各阶间接影响
            - 'max_order': 最大阶数
            - 'dominant_path': 主导路径强度
        """

        total_flow = 0.0
        flow_by_order = {}

        for order in range(1, max_order + 1):
            if order in self.power_matrices:
                flow = self.power_matrices[order][source_idx, target_idx]
                flow_by_order[order] = float(flow)

                # 间接影响的衰减因子（距离越远影响越小）
                if order > 1:
                    decay_factor = 0.7 ** (order - 1)  # 每阶衰减30%
                    flow *= decay_factor

                total_flow += flow

        # 归一化总影响
        max_possible = sum(0.7 ** (k - 1) for k in range(1, max_order + 1))
        normalized_total = total_flow / max_possible if max_possible > 0 else 0

        return {
            'total_influence': float(normalized_total),
            'direct_influence': float(flow_by_order.get(1, 0)),
            'indirect_influences': flow_by_order,
            'max_order': max_order,
            'dominant_path': self._find_dominant_path(source_idx, target_idx, max_order)
        }

    def _find_dominant_path(self, source_idx: int, target_idx: int,
                            max_order: int) -> List[Tuple[List[int], float]]:
        """寻找主导的间接路径"""
        if source_idx == target_idx:
            return []

        paths = []

        # 搜索一阶间接路径（经过一个中间元素）
        for mediator in range(8):
            if mediator != source_idx and mediator != target_idx:
                direct_to_mediator = self.direct_matrix[source_idx, mediator]
                mediator_to_target = self.direct_matrix[mediator, target_idx]

                if direct_to_mediator > 0.01 and mediator_to_target > 0.01:
                    path_strength = direct_to_mediator * mediator_to_target
                    paths.append(([source_idx, mediator, target_idx], float(path_strength)))

        # 按强度排序
        paths.sort(key=lambda x: x[1], reverse=True)

        # 返回最强的3条路径
        return paths[:3]

    def compute_influence_matrix(self, max_order: int = 3) -> np.ndarray:
        """计算总影响矩阵"""
        n = self.direct_matrix.shape[0]
        total_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    influence = self.compute_total_influence(i, j, max_order)
                    total_matrix[i, j] = influence['total_influence']

        return total_matrix


# 为旧代码提供别名
IndirectCalculator = IndirectInfluenceCalculator

__all__ = ['IndirectInfluenceCalculator', 'IndirectCalculator']