from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field
from falaw.models.entities import Individual, Environment, PrimalValue, LifeState
from falaw.core.data_source import get_data_source


class PrimalField:
    def __init__(self, config=None):
        self.data = get_data_source(config)

    def compute_excitation(self, entity, pressure: float) -> float:
        """计算个体的原力激发值"""
        # ❌ 之前： self.base_excitation * self.pressure_factor
        # ✅ 现在： 从数据源获取V3_S型抑制计算结果
        return self.data.compute_primal_excitation(pressure)

    def validate_philosophy(self):
        """哲学验证——现在有真实数据支撑"""
        retentions = self.data.get_all_self_retentions()
        return {
            'valid': True,
            'philosophical_basis': 'existence_is_excitation',
            'data': {
                'self_retention': retentions,
                'theoretical_model': 'V3_S型抑制'
            }
        }

    def _update_field_state(self, excitation_level: float):
        """更新场状态"""
        if excitation_level > 0.7:
            self.active_excitation = excitation_level
            self.passive_excitation = 0.3
            self.inhibition = 0.0
        elif excitation_level > 0.3:
            self.active_excitation = 0.3
            self.passive_excitation = excitation_level
            self.inhibition = 0.1
        elif excitation_level > 0.1:
            self.active_excitation = 0.1
            self.passive_excitation = 0.2
            self.inhibition = 1.0 - excitation_level
        else:
            self.active_excitation = 0.0
            self.passive_excitation = 0.0
            self.inhibition = 1.0

        # 记录历史
        self.excitation_history.append(excitation_level)
        if len(self.excitation_history) > 1000:
            self.excitation_history = self.excitation_history[-1000:]

    def _check_survival(self, excitation_level: float,
                        individual: Individual) -> Dict[str, Any]:
        """检查生存状态"""
        if excitation_level < self.survival_threshold:
            # 原力激发条件被极限抑制
            individual.life_state = LifeState.EXTINCT
            return {
                'survivable': False,
                'reason': 'primal_excitation_below_survival_threshold',
                'threshold': self.survival_threshold,
                'actual': excitation_level
            }
        elif excitation_level < self.excitation_threshold:
            # 濒临灭绝
            return {
                'survivable': True,
                'state': 'near_extinction',
                'risk': 'extreme',
                'action_needed': 'immediate_primal_restoration'
            }
        else:
            # 正常生存
            return {
                'survivable': True,
                'state': 'exciting',
                'excitation_level': excitation_level,
                'health': 'good' if excitation_level > 0.5 else 'weak'
            }

    def is_maintained(self) -> bool:
        """场是否还能维持"""
        total_excitation = self.active_excitation + self.passive_excitation
        return total_excitation > self.maintenance_threshold

    def trigger_kunzhuan_if_needed(self) -> Optional[Dict[str, Any]]:
        """如果需要，触发坤转"""
        if not self.is_maintained():
            # 当场无法维持时，坤转启动
            return {
                'action': 'activate_kunzhuan',
                'reason': 'field_cannot_maintain',
                'field_state': {
                    'active': self.active_excitation,
                    'passive': self.passive_excitation,
                    'total': self.active_excitation + self.passive_excitation,
                    'threshold': self.maintenance_threshold
                },
                'kunzhuan_method': 'guidance_from_chaos',
                'principle': 'ignore_fragmentation_reestablish_from_primal'
            }
        return None

    def analyze_excitation_patterns(self) -> Dict[str, Any]:
        """分析激发模式"""
        if not self.excitation_history:
            return {'status': 'no_data'}

        history = np.array(self.excitation_history)

        return {
            'mean_excitation': float(np.mean(history)),
            'std_excitation': float(np.std(history)),
            'max_excitation': float(np.max(history)),
            'min_excitation': float(np.min(history)),
            'trend': 'increasing' if len(history) > 10 and
                                     history[-1] > history[0] else 'stable_or_decreasing',
            'volatility': float(np.std(history[-100:]) if len(history) >= 100
                                else np.std(history)),
            'survival_assurance': np.mean(history > self.survival_threshold) > 0.9
        }

    def validate_philosophy(self) -> Dict[str, Any]:
        """验证哲学一致性"""
        return {
            'valid': True,
            'philosophical_basis': 'existence_is_excitation',
            'details': {
                'principle': '活着即激发',
                'implementation': '所有存活实体均有原力值'
            }
        }


# ================================================
# 文件末尾：保持向后兼容
# ================================================

# 为旧代码提供别名
PrimalExcitationField = PrimalField
Primal = PrimalField

# 导出列表
__all__ = ['PrimalField', 'PrimalExcitationField', 'Primal']