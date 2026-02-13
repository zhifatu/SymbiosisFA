"""秩法图理论：8×8流转矩阵数学核心

本模块定义了 FundamentalFlowMatrix 类，提供：
- 8×8流转矩阵的构建与约束
- 元素自我保留率分析
- 主导流出路径识别
- 流转熵计算

理论依据:
    - 决策记录 002：8×8矩阵设计原则
    - 公理 D2：原力流动守恒
    - 公理 S1：原力守恒定律
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from falaw.models.enums import ElementType


class FundamentalFlowMatrix:
    """基础流转数值矩阵 R_ij

    8×8矩阵，每行和为1，对角线≥0.5。
    表示元素间原力流转的比例。

    属性
    ----------
    matrix : np.ndarray
        8×8流转矩阵，matrix[i,j] 表示从元素j流向元素i的比例
    precision : float
        数值精度阈值

    示例
    --------
    >>> matrix = FundamentalFlowMatrix()
    >>> flow = matrix.get_flow(ElementType.QIAN, ElementType.SHE)
    >>> print(flow)
    0.12
    """

    def __init__(self):
        # 基础矩阵：对角线是自我保留，非对角线是流出比例
        self.matrix = self._build_fundamental_matrix()
        self.precision = 1e-6

        # 强制数值约束
        self._enforce_constraints()

    def _build_fundamental_matrix(self) -> np.ndarray:
        """构建基础数值矩阵"""

        # 8×8 零矩阵
        R = np.zeros((8, 8))

        # 1. 自我保留率（元素保持自身原力的比例）
        self_retention = {
            ElementType.QIAN: 0.70,  # 乾定：高度稳定
            ElementType.SHE: 0.65,  # 射：适度稳定
            ElementType.XIAN: 0.75,  # 陷：高度保留（粘滞性）
            ElementType.LI: 0.60,  # 离：较低保留（易变）
            ElementType.JIE: 0.68,  # 界：适度稳定
            ElementType.SAN: 0.55,  # 散：较低保留（易扩散）
            ElementType.HUAN: 0.62,  # 换：适度保留
            ElementType.KUN: 0.58  # 坤转：较低保留（易变）
        }

        # 设置对角线
        for elem in ElementType:
            R[elem.index, elem.index] = self_retention[elem]

        # 2. 基础流出模式（基于元素特性）
        outflow_patterns = {
            ElementType.QIAN: {
                ElementType.SHE: 0.12,  # 乾定→射：定向观察
                ElementType.JIE: 0.08,  # 乾定→界：设立边界
                ElementType.HUAN: 0.07,  # 乾定→换：建立规则
                ElementType.XIAN: 0.03  # 乾定→陷：结构化场
            },
            ElementType.XIAN: {
                ElementType.LI: 0.15,  # 陷→离：产生逃离压力
                ElementType.SHE: 0.04,  # 陷→射：聚焦观察
                ElementType.SAN: 0.03,  # 陷→散：限制扩散
                ElementType.KUN: 0.03  # 陷→坤转：抵抗革命
            },
            ElementType.LI: {
                ElementType.XIAN: 0.12,  # 离→陷：削弱场
                ElementType.QIAN: 0.10,  # 离→乾定：分解目标
                ElementType.HUAN: 0.08,  # 离→换：破坏公平
                ElementType.SAN: 0.10  # 离→散：增强扩散
            },
            ElementType.KUN: {
                ElementType.QIAN: 0.15,  # 坤转→乾定：建立新标准
                ElementType.XIAN: 0.12,  # 坤转→陷：革命化场
                ElementType.JIE: 0.08,  # 坤转→界：重划边界
                ElementType.HUAN: 0.07  # 坤转→换：改变规则
            }
        }

        # 应用基础流出模式
        for source, targets in outflow_patterns.items():
            src_idx = source.index
            for target, flow in targets.items():
                tgt_idx = target.index
                R[src_idx, tgt_idx] = flow

        # 3. 对称性补充
        symmetry_factors = {
            (ElementType.QIAN, ElementType.SHE): 0.6,
            (ElementType.XIAN, ElementType.LI): 0.8,
            (ElementType.SAN, ElementType.HUAN): 0.7,
            (ElementType.KUN, ElementType.QIAN): 0.3
        }

        for (elem_a, elem_b), factor in symmetry_factors.items():
            a_to_b = R[elem_a.index, elem_b.index]
            if a_to_b > 0:
                R[elem_b.index, elem_a.index] = a_to_b * factor

        return R

    def _enforce_constraints(self):
        """强制数值约束"""
        n = self.matrix.shape[0]

        for i in range(n):
            # 确保非负
            self.matrix[i, :] = np.maximum(0, self.matrix[i, :])

            # 确保对角线≥0.5
            if self.matrix[i, i] < 0.5:
                # 从最大流出中扣除以补充自我保留
                max_outflow_idx = np.argmax([self.matrix[i, j] for j in range(n) if j != i])
                deficit = 0.5 - self.matrix[i, i]
                self.matrix[i, max_outflow_idx] -= deficit
                self.matrix[i, i] = 0.5

            # 确保每行和为1（归一化）
            row_sum = np.sum(self.matrix[i, :])
            if abs(row_sum - 1.0) > self.precision:
                self.matrix[i, :] = self.matrix[i, :] / row_sum

    def get_flow(self, source: ElementType, target: ElementType) -> float:
        """获取从源到目标的流转比例"""
        return self.matrix[source.index, target.index]

    def set_flow(self, source: ElementType, target: ElementType, value: float):
        """设置流转比例（自动调整相关值以保持约束）"""
        old_value = self.matrix[source.index, target.index]

        # 调整源的其他流出以保持行和=1
        self.matrix[source.index, target.index] = value
        total_other = np.sum(self.matrix[source.index, :]) - self.matrix[source.index, source.index]

        if total_other > 0:
            scale = (1 - self.matrix[source.index, source.index]) / total_other
            for j in range(8):
                if j != source.index:
                    self.matrix[source.index, j] *= scale

    def analyze_flow_patterns(self) -> Dict:
        """分析流转模式"""
        n = self.matrix.shape[0]

        analysis = {
            'self_retention': {},
            'dominant_outflows': {},
            'reciprocity': {},
            'flow_entropy': {}
        }

        # 自我保留分析
        for elem in ElementType:
            analysis['self_retention'][elem.chinese_name] = self.matrix[elem.index, elem.index]

        # 主导流出分析
        for elem in ElementType:
            i = elem.index
            outflows = [(j, self.matrix[i, j]) for j in range(8) if j != i]
            outflows.sort(key=lambda x: x[1], reverse=True)

            top_targets = []
            for j, flow in outflows[:3]:
                target_elem = ElementType.get_by_index(j) if hasattr(ElementType, 'get_by_index') else None
                target_name = target_elem.chinese_name if target_elem else f"元素{j}"
                top_targets.append((target_name, flow))

            analysis['dominant_outflows'][elem.chinese_name] = top_targets

        return analysis


# 为旧代码提供别名
FlowMatrix = FundamentalFlowMatrix

__all__ = ['FundamentalFlowMatrix', 'FlowMatrix']