from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field

from falaw.core.data_source import get_data_source
from falaw.core.math.target import TargetCalculator
from falaw.models.entities import (
    Individual, Collective, TargetType,
    LifeState, Phenomenon
)


@dataclass
class IndividualCollectiveTargetField:
    """个体与总体目标场：消灭即目标追求（薄封装层）"""

    id: str = "target_field_01"

    def __post_init__(self):
        """延迟初始化，避免 dataclass 覆盖"""
        self.data = get_data_source()

        # 从 DataSource 获取矩阵，初始化计算器
        self.calculator = TargetCalculator(
            flow_matrix=self.data.matrix,
            config=self.data.config  # 共享同一份配置
        )

        # 历史记录（只记录不计算）
        self.target_construction_history: List[Dict] = field(default_factory=list)
        self.target_loss_history: List[Dict] = field(default_factory=list)

    def pursue_target(self,
                      agent: Union[Individual, Collective],
                      target_type: TargetType,
                      target_content: Any,
                      by_elimination: bool = False,
                      elimination_target: Optional[Individual] = None) -> Dict[str, Any]:
        """
        追求目标（包括通过消灭）

        原理：消灭是目标追求的一种形式
        实现：调用 TargetCalculator 进行数值计算，调用 Agent 接口执行操作
        """

        # ========== 1. 参数准备 ==========
        agent_id = agent.id if hasattr(agent, 'id') else str(agent)
        agent_type = type(agent).__name__

        # 获取当前目标数量（通过 Agent 接口，不直接访问属性）
        current_targets = agent.get_current_targets() if hasattr(agent, 'get_current_targets') else []
        n_targets = len(current_targets)
        has_high_priority = any(t.get('priority') == 'high' for t in current_targets)

        # ========== 2. 目标因子计算（核心数学）==========
        target_factor_result = self.calculator.compute_target_factor(
            n_targets=n_targets,
            has_high_priority=has_high_priority
        )

        # ========== 3. 消灭模式处理 ==========
        if by_elimination and elimination_target:
            return self._handle_elimination_pursuit(
                agent=agent,
                target=elimination_target,
                reason=target_content if isinstance(target_content, str) else "elimination_as_goal",
                target_factor=target_factor_result.value
            )

        # ========== 4. 普通目标追求 ==========

        # 构建目标记录
        target_record = {
            'agent': agent_id,
            'agent_type': agent_type,
            'target_type': target_type.value,
            'target_content': target_content,
            'timestamp': 0.0,  # TODO: 从 Simulator 获取时间
            'by_elimination': False,
            'target_factor': target_factor_result.value
        }

        # 根据目标类型分发
        if target_type == TargetType.ETERNAL:
            result = self._handle_eternal_target(agent, target_content, target_record)
        elif target_type == TargetType.COLLECTIVE:
            result = self._handle_collective_target(agent, target_content, target_record)
        elif target_type == TargetType.INDIVIDUAL:
            result = self._handle_individual_target(agent, target_content, target_record)
        else:
            # 默认处理
            result = self._handle_default_target(agent, target_content, target_record)

        # 记录历史
        self.target_construction_history.append(target_record)

        return result

    def _handle_elimination_pursuit(self,
                                    agent: Union[Individual, Collective],
                                    target: Individual,
                                    reason: str,
                                    target_factor: float) -> Dict[str, Any]:
        """处理以消灭为目标追求"""

        agent_type = type(agent).__name__
        agent_primal = agent.get_primal_strength() if hasattr(agent, 'get_primal_strength') else 0.5
        target_primal = target.get_primal_strength() if hasattr(target, 'get_primal_strength') else 0.5
        has_collective_benefit = isinstance(agent, Collective)

        # ========== 核心数学：消灭合理性计算 ==========
        justification = self.calculator.compute_elimination_justification(
            agent_type=agent_type,
            reason=reason,
            agent_primal=agent_primal,
            target_primal=target_primal,
            has_collective_benefit=has_collective_benefit
        )

        if not justification.justified:
            return {
                'success': False,
                'reason': 'elimination_not_justified',
                'justification': {
                    'score': justification.score,
                    'threshold': justification.threshold,
                    'components': justification.components
                }
            }

        # ========== 执行消灭（调用 Agent 接口）==========
        elimination_result = agent.eliminate_target(target, reason)

        if elimination_result.get('success', False):
            # 记录目标追求
            target_record = {
                'agent': agent.id if hasattr(agent, 'id') else str(agent),
                'target_type': 'elimination_as_goal',
                'target_content': f"eliminate_{target.id}",
                'reason': reason,
                'justification_score': justification.score,
                'timestamp': 0.0,
                'by_elimination': True,
                'target_factor': target_factor
            }

            self.target_construction_history.append(target_record)

            return {
                'success': True,
                'method': 'elimination_as_target_pursuit',
                'justification': {
                    'score': justification.score,
                    'threshold': justification.threshold,
                    'components': justification.components
                },
                'elimination_result': elimination_result,
                'expected_primal_gain': justification.primal_gain_expected,
                'philosophical_note': 'elimination_is_a_form_of_goal_pursuit'
            }

        return {
            'success': False,
            'method': 'elimination_attempt_failed',
            'elimination_result': elimination_result,
            'justification': {
                'score': justification.score,
                'threshold': justification.threshold
            }
        }

    def _handle_eternal_target(self,
                               agent: Union[Individual, Collective],
                               target_content: Any,
                               target_record: Dict) -> Dict[str, Any]:
        """处理永恒目标"""

        agent_type = type(agent).__name__
        current_primal = agent.get_primal_strength() if hasattr(agent, 'get_primal_strength') else 0.5

        # ========== 核心数学：永恒目标效果 ==========
        effect = self.calculator.compute_eternal_target_effect(
            agent_type=agent_type,
            current_primal=current_primal
        )

        target_record['eternal_implementation'] = 'through_collective_participation'
        target_record['primal_boost'] = effect['primal_boost']

        # ========== 调用 Agent 接口 ==========
        if isinstance(agent, Individual):
            # 个体参与永恒目标
            agent.participate_in_eternal_target(
                target_content=str(target_content),
                primal_boost=effect['primal_boost']
            )

        return {
            'success': True,
            'target_type': 'eternal',
            'implementation': 'through_collective_participation',
            'effect': effect,
            'philosophical_note': 'individual_achieves_eternal_through_collective'
        }

    def _handle_collective_target(self,
                                  agent: Union[Individual, Collective],
                                  target_content: Any,
                                  target_record: Dict) -> Dict[str, Any]:
        """处理集体目标"""

        if isinstance(agent, Collective):
            # 集体直接构建目标
            result = agent.construct_target(str(target_content))
            target_record['collective_action'] = 'direct_construction'
            return result

        else:  # Individual
            # 个体参与集体目标
            current_primal = agent.get_primal_strength() if hasattr(agent, 'get_primal_strength') else 0.5
            excitation_capacity = getattr(agent, 'excitation_capacity', 0.8)

            # ========== 核心数学：参与集体目标效果 ==========
            new_primal = self.calculator.compute_collective_participation_effect(
                individual_primal=current_primal,
                excitation_capacity=excitation_capacity
            )

            primal_boost = new_primal - current_primal

            target_record['participation_type'] = 'individual_in_collective_goal'
            target_record['primal_boost'] = primal_boost

            # ========== 调用 Agent 接口 ==========
            agent.participate_in_collective_target(
                target_content=str(target_content),
                primal_boost=primal_boost
            )

            return {
                'success': True,
                'participation': 'individual_in_collective',
                'individual': agent.id,
                'collective_target': target_content,
                'primal_boost': primal_boost,
                'new_primal': new_primal,
                'note': 'individual_primal_enhanced_by_collective_participation'
            }

    def _handle_individual_target(self,
                                  agent: Individual,
                                  target_content: Any,
                                  target_record: Dict) -> Dict[str, Any]:
        """处理个体生存目标"""

        if not isinstance(agent, Individual):
            return {'success': False, 'reason': 'only_individuals_can_have_individual_targets'}

        # ========== 核心数学：个体目标效果 ==========
        # 个体生存目标的基础原力增益固定为 0.15 * excitation_capacity
        excitation_capacity = getattr(agent, 'excitation_capacity', 0.8)
        primal_boost = 0.15 * excitation_capacity

        target_record['primal_boost'] = primal_boost

        # ========== 调用 Agent 接口 ==========
        agent.pursue_individual_target({
            'type': 'individual_survival',
            'content': target_content,
            'priority': 'high',
            'primal_boost': primal_boost
        })

        return {
            'success': True,
            'target_type': 'individual_survival',
            'agent': agent.id,
            'primal_boost': primal_boost,
            'philosophical_note': 'survival_as_primal_excitation_goal'
        }

    def _handle_default_target(self,
                               agent: Union[Individual, Collective],
                               target_content: Any,
                               target_record: Dict) -> Dict[str, Any]:
        """默认目标处理"""

        # ========== 调用 Agent 接口 ==========
        agent.add_target({
            'content': str(target_content),
            'type': 'default',
            'timestamp': target_record['timestamp']
        })

        return {
            'success': True,
            'target_record': target_record,
            'note': 'target_pursuit_registered'
        }

    def lose_target(self,
                    agent: Union[Individual, Collective],
                    target_index: Optional[int] = None,
                    target_content: Optional[str] = None) -> Dict[str, Any]:
        """丧失目标"""

        agent_id = agent.id if hasattr(agent, 'id') else str(agent)
        agent_type = type(agent).__name__

        # ========== 获取当前状态（通过接口）==========
        current_cohesion = agent.get_field_cohesion() if hasattr(agent, 'get_field_cohesion') else 0.5
        current_fragmentation = agent.get_field_fragmentation() if hasattr(agent, 'get_field_fragmentation') else 0.0

        # ========== 调用 Agent 接口执行目标丧失 ==========
        if target_index is not None:
            loss_result = agent.remove_target(target_index)
            n_targets_lost = 1 if loss_result.get('success', False) else 0
        else:
            loss_result = agent.remove_all_targets()
            n_targets_lost = loss_result.get('targets_removed', 0)

        # ========== 核心数学：目标丧失影响 ==========
        effects = self.calculator.compute_target_loss_effects(
            n_targets_lost=n_targets_lost,
            current_cohesion=current_cohesion,
            current_fragmentation=current_fragmentation
        )

        # ========== 调用 Agent 接口应用影响 ==========
        if n_targets_lost > 0:
            agent.apply_target_loss_effects(effects)

        loss_record = {
            'agent': agent_id,
            'agent_type': agent_type,
            'timestamp': 0.0,
            'target_index': target_index,
            'target_content': target_content,
            'n_targets_lost': n_targets_lost,
            'effects': effects,
            'kunzhuan_risk': effects['kunzhuan_risk'] > 0.7
        }

        self.target_loss_history.append(loss_record)

        return loss_record

    def analyze_target_dynamics(self) -> Dict[str, Any]:
        """分析目标动力学（仅统计数据，无计算逻辑）"""

        if not self.target_construction_history:
            return {'status': 'no_target_data'}

        # 统计目标类型分布
        type_counts = {}
        elimination_count = 0

        for record in self.target_construction_history:
            target_type = record.get('target_type', 'unknown')
            type_counts[target_type] = type_counts.get(target_type, 0) + 1
            if record.get('by_elimination', False):
                elimination_count += 1

        # 统计目标丧失
        recent_losses = [r for r in self.target_loss_history[-10:]] if self.target_loss_history else []
        recent_loss_rate = len(recent_losses) / 10 if recent_losses else 0

        # 风险等级判断（基于统计数据，不是数学计算）
        risk = 'high' if recent_loss_rate > 0.5 else 'medium' if recent_loss_rate > 0.2 else 'low'

        return {
            'target_construction': {
                'total': len(self.target_construction_history),
                'by_type': type_counts,
                'elimination_as_target_count': elimination_count,
                'elimination_percentage': elimination_count / len(self.target_construction_history)
            },
            'target_loss': {
                'total_losses': len(self.target_loss_history),
                'recent_loss_rate': recent_loss_rate
            },
            'kunzhuan_risk': risk
        }

    def validate_philosophy(self) -> Dict[str, Any]:
        """验证哲学一致性"""

        return {
            'valid': True,
            'philosophical_basis': 'elimination_as_target_pursuit',
            'architecture': 'thin_wrapper_over_math_core',
            'details': {
                'principle': '消灭即目标追求',
                'implementation': '数学核心在 core/math/target.py',
                'data_source_connected': hasattr(self, 'data'),
                'calculator_initialized': hasattr(self, 'calculator')
            }
        }


# ================================================
# 保持向后兼容
# ================================================

TargetField = IndividualCollectiveTargetField
Target = IndividualCollectiveTargetField

__all__ = ['IndividualCollectiveTargetField', 'TargetField', 'Target']